# -*- coding: utf-8 -*-
"""根据差距生成：分阶段学习路线 + 针对性面试问题。"""
from knowledge import ROLES

# 时间估算（按重要性粗略给）
_EST_DAYS = {1: "3-5 天", 2: "1-2 周", 3: "2-4 周", 4: "1-2 个月", 5: "2-3 个月"}

# importance -> 阶段
def _phase_of(imp: int) -> str:
    if imp <= 2:
        return "阶段一 · 基础夯实"
    if imp == 3:
        return "阶段二 · 核心突破"
    return "阶段三 · 高阶实战"


def _est(imp: int) -> str:
    return _EST_DAYS.get(imp, "2-4 周")


def build_path(role: str, gaps: list) -> dict:
    """gaps: matcher 输出的 gap_list（含 label/importance/dim/learn/resource）。"""
    spec = ROLES.get(role, {})
    role_label = spec.get("label", role)

    if not gaps:
        return {
            "summary": f"太棒了！你的简历与「{role_label}」岗位的匹配度很高，核心能力基本齐备。建议继续做 1 个代表性项目并准备作品集，冲击面试。",
            "phases": [],
        }

    phases = {}
    for g in gaps:
        ph = _phase_of(g["importance"])
        phases.setdefault(ph, [])
        phases[ph].append({
            "skill": g["label"],
            "dim": g["dim"],
            "importance": g["importance"],
            "action": g.get("learn", ""),
            "estimate": _est(g["importance"]),
            "resource": g.get("resource") or {"name": "自行搜索", "url": ""},
        })

    # 固定阶段顺序
    order = ["阶段一 · 基础夯实", "阶段二 · 核心突破", "阶段三 · 高阶实战"]
    phase_list = []
    for ph in order:
        if ph in phases:
            phase_list.append({
                "name": ph,
                "steps": sorted(phases[ph], key=lambda x: x["importance"], reverse=True),
            })

    # 收尾：实战项目建议
    top_missing = "、".join([g["label"] for g in gaps[:3]])
    summary = (
        f"针对你与「{role_label}」岗位的差距，建议优先补齐【{top_missing}】等能力。"
        f"学习路线分为 {len(phase_list)} 个阶段，建议每完成一个阶段就做一个小项目沉淀作品集。"
    )
    phase_list.append({
        "name": "阶段四 · 作品集与复盘",
        "steps": [{
            "skill": "输出代表性项目",
            "dim": "综合",
            "importance": 5,
            "action": "把学到的能力整合成 1 个可演示项目（如 AI 小工具 / 运营复盘 / 产品方案），写好 README 与复盘。",
            "estimate": "持续",
            "resource": {"name": "GitHub", "url": "https://github.com"},
        }],
    })

    return {"summary": summary, "phases": phase_list}


def build_interview(role: str, gaps: list) -> dict:
    spec = ROLES.get(role, {})
    role_label = spec.get("label", role)
    base = spec.get("interview_base", [])

    # 针对差距生成追问
    targeted = []
    for g in gaps[:5]:
        imp = g["importance"]
        if imp >= 4:
            tone = "请重点准备"
        elif imp >= 3:
            tone = "建议准备"
        else:
            tone = "可补充了解"
        targeted.append({
            "question": f"{tone}：面试官可能会问你在「{g['label']}」上的实践经验，请用 STAR 法则准备一个具体案例。",
            "skill": g["label"],
            "importance": imp,
        })

    return {
        "role_label": role_label,
        "base_questions": base,
        "targeted_questions": targeted,
    }
