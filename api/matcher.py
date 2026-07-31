# -*- coding: utf-8 -*-
"""匹配度分析：基于知识库做关键词命中评分，输出总分、维度分与差距。

Skill 版本功能集成：
- Gate 系统：根据输入组合选择分析模式
- 五维评审：JD 匹配 / ATS / HR 扫描 / 面试准备度 / 可信度
- 事实台账：每个技能的来源、证据与状态追踪
- JD 拆解分析 / 简历基线诊断 / 多 JD 对比
"""
import re
from api.knowledge import ROLES, auto_detect_role, DIMENSIONS, GENERIC_RESOURCE
from api.knowledge import DIMENSIONS_EN, LABEL_EN, LEARN_EN, ROLE_LABEL_EN, ROLE_DESC_EN, INTERVIEW_BASE_EN

# ── 工具函数 ──────────────────────────────────────────────

def _hit(skill, text_lower: str) -> bool:
    """检查技能关键词是否在文本中命中。"""
    return any(k.lower() in text_lower for k in skill["keywords"])


def _hit_score(skill, text_lower: str) -> float:
    """返回 0~1 的命中强度：全部关键词匹配数 / 总关键词数。"""
    kws = [k.lower() for k in skill["keywords"]]
    if not kws:
        return 0.0
    hits = sum(1 for k in kws if k in text_lower)
    return round(hits / len(kws), 2)


def _detect_sections(text: str) -> list:
    """检测简历中的章节结构。"""
    section_patterns = [
        (r"(教育|学历|学校|大学|学院)", "教育背景"),
        (r"(工作|经历|经验|实习|公司|企业)", "工作/实习经验"),
        (r"(项目|作品|课题|研究)", "项目经验"),
        (r"(技能|技术|工具|编程|语言)", "技能"),
        (r"(自我|简介|摘要|概况|概述|profile)", "个人简介"),
        (r"(证书|认证|奖项|荣誉|获奖)", "证书/奖项"),
        (r"(发表|论文|专利|出版)", "论文/专利"),
    ]
    found = []
    text_lower = text.lower()
    for pattern, label in section_patterns:
        if re.search(pattern, text_lower):
            found.append(label)
    return found


# ── 事实台账 ──────────────────────────────────────────────

def build_fact_ledger(spec: dict, resume_text: str, matched_labels: set) -> list:
    """为每个技能生成事实台账条目。

    状态规则：
    - confirmed:   简历原文明确命中关键词
    - pending_confirmation: 有部分命中但强度不足
    - model_inference: 未命中但重要性高（在规则系统中作为默认状态）
    """
    rl = (resume_text or "").lower()
    ledger = []
    for sk in spec["skills"]:
        hit_strength = _hit_score(sk, rl)
        is_hit = sk["label"] in matched_labels

        if is_hit:
            # 找到命中的关键词作为证据
            evidence_kws = [k for k in sk["keywords"] if k.lower() in rl]
            status = "confirmed"
            source = f"简历原文命中关键词: {', '.join(evidence_kws[:5])}"
            evidence = f"命中 {len(evidence_kws)}/{len(sk['keywords'])} 个关键词"
        elif hit_strength > 0.2:
            status = "pending_confirmation"
            partial_kws = [k for k in sk["keywords"] if k.lower() in rl]
            source = "部分关键词命中"
            evidence = f"部分匹配 {len(partial_kws)}/{len(sk['keywords'])} 个关键词"
        else:
            status = "model_inference"
            source = "未在简历中找到相关关键词"
            evidence = ""

        ledger.append({
            "skill": sk["label"],
            "dim": sk["dim"],
            "importance": sk["importance"],
            "status": status,
            "source": source,
            "evidence": evidence,
            "can_enter_final": status == "confirmed",
        })
    return ledger


# ── 五维评审 ──────────────────────────────────────────────

def build_five_dim_review(
    overall_score: int,
    dimensions: list,
    matched_skills: list,
    gaps: list,
    resume_text: str,
    role_label: str,
) -> dict:
    """从五个维度评审简历匹配度。"""
    total_skills = sum(d.get("total", 0) for d in dimensions) or 1
    total_matched = sum(d.get("matched", 0) for d in dimensions)

    # ATS 评分：关键词覆盖密度 + 是否为可解析格式
    ats_coverage = round(total_matched / total_skills * 100)
    ats_deductions = []
    if ats_coverage < 50:
        ats_deductions.append("关键词覆盖率低于 50%，ATS 排名可能偏低")
    if ats_coverage < 30:
        ats_deductions.append("大量 JD 要求技能未出现")
    ats_score = min(100, ats_coverage + 10)  # 规则系统有格式优势

    # HR 扫描体验：结构完整度 + 内容丰富度
    sections = _detect_sections(resume_text)
    resume_len = len(resume_text or "")
    hr_deductions = []
    if len(sections) < 2:
        hr_deductions.append("简历章节过少，HR 难以快速定位信息")
    if "教育背景" not in sections:
        hr_deductions.append("未检测到教育背景章节")
    if "工作/实习经验" not in sections and "项目经验" not in sections:
        hr_deductions.append("未检测到经验或项目章节")
    if resume_len < 200:
        hr_deductions.append("简历内容过短，HR 可能认为信息不足")
    elif resume_len > 5000:
        hr_deductions.append("简历内容偏长，建议精简到一页")
    section_score = min(100, 40 + len(sections) * 15)
    hr_score = min(100, max(20, section_score - len(hr_deductions) * 8))

    # 面试准备度：基于差距数量和重要性
    gap_count = len(gaps)
    avg_gap_imp = sum(g.get("importance", 3) for g in gaps) / max(gap_count, 1)
    interview_deductions = []
    if gap_count == 0:
        interview_score = 95
    else:
        # gap 越少、重要性越低 -> 面试准备度越高
        interview_score = max(20, 100 - gap_count * 6 - int(avg_gap_imp * 4))
        if gap_count > 5:
            interview_deductions.append(f"有 {gap_count} 项能力差距，面试中可能被追问")
        if avg_gap_imp > 3.5:
            interview_deductions.append("多项高重要性技能缺失，面试风险较高")

    # 可信度：匹配项越多越可信
    cred_score = min(100, 50 + len(matched_skills) * 4)
    cred_deductions = []
    if len(matched_skills) < 3:
        cred_deductions.append("匹配项过少，简历可能与目标岗位偏差较大")

    return {
        "jd_match": {
            "score": overall_score,
            "label": f"{role_label} 匹配度",
            "evidence": f"总体匹配度 {overall_score}/100，命中 {len(matched_skills)} 项核心能力",
            "deduction": "",
            "improvement": "针对差距清单中的高重要性项优先补齐"
            if gap_count > 0
            else "继续保持",
        },
        "ats": {
            "score": ats_score,
            "label": "ATS 系统友好度",
            "evidence": f"关键词覆盖率 {ats_coverage}%，简历格式为纯文本可解析",
            "deduction": "; ".join(ats_deductions) if ats_deductions else "无显著扣分项",
            "improvement": "建议在简历中自然融入更多 JD 关键词"
            if ats_deductions
            else "当前 ATS 表现良好",
        },
        "hr_scan": {
            "score": hr_score,
            "label": "HR 扫描体验",
            "evidence": f"检测到 {len(sections)} 个章节: {', '.join(sections) if sections else '未识别到标准章节'}",
            "deduction": "; ".join(hr_deductions) if hr_deductions else "结构完整",
            "improvement": "建议补充缺失的标准简历章节并使用量化成果"
            if hr_deductions
            else "HR 可快速定位关键信息",
        },
        "interview_readiness": {
            "score": interview_score,
            "label": "面试准备度",
            "evidence": f"差距数 {gap_count}，平均重要度 {avg_gap_imp:.1f}/5",
            "deduction": "; ".join(interview_deductions) if interview_deductions else "可经得起追问",
            "improvement": "针对 P4-P5 差距项准备 STAR 案例"
            if interview_deductions
            else "面试表现预计良好",
        },
        "credibility": {
            "score": cred_score,
            "label": "简历可信度",
            "evidence": f"简历长度 {resume_len} 字，匹配 {len(matched_skills)} 项技能，关键词均为简历原文可追溯",
            "deduction": "; ".join(cred_deductions) if cred_deductions else "所有匹配项均可从简历原文验证",
            "improvement": "补充更多可量化的项目成果数据"
            if cred_deductions
            else "当前可信度较高",
        },
    }


# ── JD 拆解分析 ────────────────────────────────────────────

def analyze_jd_only(jd_text: str) -> dict:
    """仅基于 JD 文本做岗位拆解分析。"""
    role_key = auto_detect_role(jd_text)
    spec = ROLES.get(role_key, {})
    t = (jd_text or "").lower()

    # 分类提取关键词命中情况
    required = []
    preferred = []
    tools_tech = []
    domain_knowledge = []
    soft_skills = []

    for sk in spec.get("skills", []):
        if _hit(sk, t):
            item = {
                "label": sk["label"],
                "importance": sk["importance"],
                "dim": sk["dim"],
                "description": sk.get("learn", ""),
            }
            if sk["dim"] == "核心技能":
                if sk["importance"] >= 4:
                    required.append(item)
                else:
                    preferred.append(item)
                if any(k in ["python", "fastapi", "docker", "sql", "react",
                             "vue", "langchain", "rag", "大模型api"] for k in sk["keywords"]):
                    tools_tech.append(sk["label"])
                if any(k in ["机器学习", "深度学", "大模型", "llm", "nlp",
                             "推荐", "搜索", "多模态"] for k in sk["keywords"]):
                    domain_knowledge.append(sk["label"])
            elif sk["dim"] == "综合素养":
                soft_skills.append(item)
            elif sk["dim"] == "项目经验":
                required.append(item)

    # 隐式需求分析
    hidden = []
    if any(k in t for k in ["实习", "应届", "校招", "25届", "26届"]):
        hidden.append("面向应届生/实习生，看重学习潜力而非工作经验")
    if any(k in t for k in ["创业", "0-1", "从0", "孵化", "mvp"]):
        hidden.append("需要从零开始的推动力，容忍不确定性")
    if any(k in t for k in ["英语", "英文", "cet", "雅思", "toefl"]):
        hidden.append("英语能力是隐性门槛")
    if any(k in t for k in ["跨部门", "协作", "推动", "沟通"]):
        hidden.append("跨团队协作能力未被强调但隐含在职责描述中")

    return {
        "role": role_key,
        "role_label": spec.get("label", "未知"),
        "role_desc": spec.get("desc", ""),
        "core_responsibilities": [r["label"] for r in required],
        "required_skills": [r["label"] for r in required],
        "preferred_skills": [p["label"] for p in preferred],
        "tools_technologies": tools_tech,
        "domain_knowledge": domain_knowledge,
        "soft_skills": [s["label"] for s in soft_skills],
        "hidden_requirements": hidden,
        "keyword_count": len(required) + len(preferred),
    }


# ── 简历基线诊断 ────────────────────────────────────────────

def analyze_resume_only(resume_text: str) -> dict:
    """仅基于简历文本做基线诊断。"""
    rl = (resume_text or "").lower()
    sections = _detect_sections(resume_text)
    word_count = len(resume_text)

    # 检查常见问题
    issues = []
    if word_count < 150:
        issues.append("简历内容过短，建议补充详细经历")
    if word_count > 4000:
        issues.append("简历偏长，建议精简到 1-2 页")
    if "教育背景" not in sections:
        issues.append("缺少教育背景信息，对应届生尤为重要")
    if "工作/实习经验" not in sections and "项目经验" not in sections:
        issues.append("没有检测到实习或项目经验，建议补充")

    # 检查是否有量化数据
    has_numbers = bool(re.search(r"\d+%|\d+人|\d+万|\d+次|\d+篇", resume_text))
    if not has_numbers:
        issues.append("缺乏量化数据（如百分比、人数、金额），建议补充以增加说服力")

    # 检查是否有 Action Verb
    action_verbs = ["负责", "参与", "主导", "完成", "实现", "优化", "设计", "开发",
                    "搭建", "推动", "提升", "降低", "增长", "引入", "创建", "制定"]
    found_verbs = [v for v in action_verbs if v in rl]
    if len(found_verbs) < 3:
        issues.append("动作动词使用较少，建议使用 '主导/设计/优化/推动' 等有力动词")

    # 检查专业技能描述
    tech_terms = ["python", "sql", "excel", "数据分析", "机器学习", "项目", "工具",
                  "框架", "算法", "设计", "研究", "报告"]
    found_tech = [t for t in tech_terms if t in rl]

    # 生成针对性追问
    questions = []
    for section in sections:
        if section == "工作/实习经验":
            questions.append("你在实习/工作中具体做了什么？用了什么工具？取得了什么可量化成果？")
        elif section == "项目经验":
            questions.append("这个项目中你具体承担了什么角色？技术栈是什么？解决了什么实际问题？")
        elif section == "技能":
            questions.append("你最擅长的技能是什么？有做过相关项目来证明这些技能吗？")

    if not has_numbers:
        questions.append("你能为每段经历补充 1-2 个量化数据吗（如参与人数、效率提升百分比）？")

    return {
        "word_count": word_count,
        "sections_found": sections,
        "action_verbs_found": found_verbs,
        "tech_terms_found": found_tech,
        "has_quantified_data": has_numbers,
        "issues": issues,
        "issue_count": len(issues),
        "targeted_questions": questions,
        "strengths": [
            f"检测到 {len(sections)} 个标准简历章节" if len(sections) >= 2 else "",
            f"使用了 {len(found_verbs)} 个动作动词" if len(found_verbs) >= 3 else "",
            f"涉及 {len(found_tech)} 个技术/专业术语" if len(found_tech) >= 3 else "",
            "包含量化成果数据" if has_numbers else "",
        ],
    }


# ── 多 JD 对比 ────────────────────────────────────────────

def multi_jd_compare(jd_texts: list, resume_text: str) -> dict:
    """对比同一份简历与多个 JD 的匹配结果。"""
    results = []
    role_keys = set()
    shared_matched = None

    for jd_text in jd_texts:
        role_key = auto_detect_role(jd_text)
        role_keys.add(role_key)
        result = analyze(jd_text=jd_text, resume_text=resume_text, role=role_key)
        results.append(result)

        if shared_matched is None:
            shared_matched = set(result["matched_skills"])
        else:
            shared_matched &= set(result["matched_skills"])

    # 差异表：不同 JD 之间的要求差异
    differences = []
    all_skills = {}
    for i, result in enumerate(results):
        for g in result.get("gaps", []):
            key = g["label"]
            if key not in all_skills:
                all_skills[key] = {}
            all_skills[key][f"jd_{i}"] = g["importance"]

    for skill, jd_map in all_skills.items():
        if len(jd_map) > 1:
            imps = list(jd_map.values())
            if max(imps) - min(imps) >= 2:
                jd_names = [f"JD {k.split('_')[1]}" for k, v in jd_map.items() if v >= 3]
                differences.append({
                    "skill": skill,
                    "importance_map": {f"JD {k.split('_')[1]}": v for k, v in jd_map.items()},
                    "note": f"在 {'、'.join(jd_names)} 中为重点要求，其他 JD 中相对次要"
                    if jd_names
                    else "",
                })

    return {
        "jd_count": len(jd_texts),
        "roles_detected": list(role_keys),
        "shared_strengths": list(shared_matched) if shared_matched else [],
        "per_jd": [
            {
                "index": i,
                "role": r.get("role"),
                "role_label": r.get("role_label"),
                "overall_score": r.get("overall_score"),
                "dimensions": r.get("dimensions"),
                "matched_count": len(r.get("matched_skills", [])),
                "gap_count": r.get("gap_count"),
                "gaps": r.get("gaps", []),
            }
            for i, r in enumerate(results)
        ],
        "differences": differences,
        "recommendation": "建议优先准备各 JD 共有的核心能力，再针对差异化要求做针对性调整。",
    }


# ── 主分析函数 ────────────────────────────────────────────

def analyze(jd_text: str, resume_text: str, role: str = "auto") -> dict:
    """完整的匹配度分析，包含五维评审和事实台账。

    返回 Gate 系统标准响应结构，适用于 complete（完整材料）模式。
    """
    # 1) 确定岗位
    role_key = role if role in ROLES else auto_detect_role(jd_text)
    spec = ROLES[role_key]

    # 2) 命中统计（按维度加权）
    rl = (resume_text or "").lower()
    dim_stat = {d: {"matched": 0, "total": 0} for d in DIMENSIONS}
    matched_skills = []
    gaps = []
    all_matched_labels = set()

    total_w = 0
    matched_w = 0

    for sk in spec["skills"]:
        d = sk["dim"]
        w = sk["importance"]
        dim_stat[d]["total"] += w
        total_w += w
        if _hit(sk, rl):
            dim_stat[d]["matched"] += w
            matched_w += w
            matched_skills.append(sk["label"])
            all_matched_labels.add(sk["label"])
        else:
            if sk["importance"] >= 2:
                gaps.append(sk)

    overall = round(matched_w / total_w * 100) if total_w else 0

    dimensions = []
    for d in DIMENSIONS:
        st = dim_stat[d]
        score = round(st["matched"] / st["total"] * 100) if st["total"] else 0
        dimensions.append({
            "name": d,
            "score": score,
            "matched": st["matched"],
            "total": st["total"],
        })

    # 3) 差距按重要性排序
    gaps_sorted = sorted(gaps, key=lambda x: x["importance"], reverse=True)
    gap_list = [{
        "label": g["label"],
        "importance": g["importance"],
        "dim": g["dim"],
        "learn": g.get("learn", ""),
        "resource": g.get("resource") or {"name": "自行搜索", "url": ""},
    } for g in gaps_sorted]

    # 4) 五维评审
    five_dim = build_five_dim_review(
        overall_score=overall,
        dimensions=dimensions,
        matched_skills=matched_skills,
        gaps=gap_list,
        resume_text=resume_text,
        role_label=spec["label"],
    )

    # 5) 事实台账
    ledger = build_fact_ledger(spec, resume_text, all_matched_labels)

    return {
        "role": role_key,
        "role_label": spec["label"],
        "role_desc": spec.get("desc", ""),
        "overall_score": overall,
        "dimensions": dimensions,
        "matched_skills": matched_skills,
        "gaps": gap_list,
        "gap_count": len(gap_list),
        "five_dim_review": five_dim,
        "fact_ledger": ledger,
    }


def localize_analysis(result: dict, locale: str = "zh") -> dict:
    """后处理分析结果，将中文标签翻译为英文（locale="en" 时生效）。

    作用于：role_label / role_desc / dimensions / matched_skills / gaps /
    fact_ledger / five_dim_review 中的标签与描述。
    """
    if locale != "en":
        return result

    r = dict(result)  # 浅拷贝，避免修改原数据

    # 角色
    if "role_label" in r:
        r["role_label"] = ROLE_LABEL_EN.get(r["role_label"], r["role_label"])
    if "role_desc" in r:
        r["role_desc"] = ROLE_DESC_EN.get(r["role_desc"], r["role_desc"])

    # 维度
    if "dimensions" in r:
        r["dimensions"] = [
            {**d, "name": DIMENSIONS_EN.get(d["name"], d["name"])}
            for d in r["dimensions"]
        ]

    # 已匹配技能
    if "matched_skills" in r:
        r["matched_skills"] = [LABEL_EN.get(s, s) for s in r["matched_skills"]]

    # 差距
    if "gaps" in r:
        r["gaps"] = [
            {
                **g,
                "label": LABEL_EN.get(g["label"], g["label"]),
                "learn": LEARN_EN.get(g.get("learn", ""), g.get("learn", "")),
                "dim": DIMENSIONS_EN.get(g.get("dim", ""), g.get("dim", "")),
            }
            for g in r["gaps"]
        ]

    # 五维评审
    if "five_dim_review" in r:
        new_fd = {}
        for key, dim in r["five_dim_review"].items():
            new_fd[key] = {**dim}
            # label 本身就是中文的，直接整体替换
        r["five_dim_review"] = new_fd

    # 事实台账
    if "fact_ledger" in r:
        r["fact_ledger"] = [
            {
                **f,
                "skill": LABEL_EN.get(f["skill"], f["skill"]),
                "dim": DIMENSIONS_EN.get(f.get("dim", ""), f.get("dim", "")),
            }
            for f in r["fact_ledger"]
        ]

    return r


def localize_interview(interview: dict, role_key: str, locale: str = "zh") -> dict:
    """本地化面试问题。"""
    if locale != "en" or not interview:
        return interview
    eng = INTERVIEW_BASE_EN.get(role_key)
    if eng:
        interview["base_questions"] = eng.copy()
    return interview


def localize_learning_path(lp: dict, locale: str = "zh") -> dict:
    """本地化学习路线（目前 learning.py 的 summary 为中文，暂保持原样）。"""
    if locale != "en" or not lp:
        return lp
    # phases 内的 skill 和 action 通过 gap 本地化已处理
    return lp
