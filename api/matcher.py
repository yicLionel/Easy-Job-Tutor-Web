# -*- coding: utf-8 -*-
"""匹配度分析：基于知识库做关键词命中评分，输出总分、维度分与差距。"""
from knowledge import ROLES, auto_detect_role, DIMENSIONS


def _hit(skill, text_lower: str) -> bool:
    return any(k.lower() in text_lower for k in skill["keywords"])


def analyze(jd_text: str, resume_text: str, role: str = "auto") -> dict:
    # 1) 确定岗位
    role_key = role if role in ROLES else auto_detect_role(jd_text)
    spec = ROLES[role_key]

    # 2) 命中统计（按维度加权）
    rl = (resume_text or "").lower()
    dim_stat = {d: {"matched": 0, "total": 0} for d in DIMENSIONS}
    matched_skills = []
    gaps = []

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
        else:
            # 仅把有一定重要性的缺失项列为“差距”
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

    return {
        "role": role_key,
        "role_label": spec["label"],
        "role_desc": spec.get("desc", ""),
        "overall_score": overall,
        "dimensions": dimensions,
        "matched_skills": matched_skills,
        "gaps": gap_list,
        "gap_count": len(gap_list),
    }
