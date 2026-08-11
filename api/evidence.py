from dataclasses import dataclass
import re


@dataclass(frozen=True)
class EvidenceMatch:
    status: str
    evidence: tuple[str, ...]
    matched_keywords: tuple[str, ...]
    reason: str


NEGATION_PATTERNS = (
    r"不熟悉",
    r"不了解",
    r"不会",
    r"没有使用",
    r"没有.{0,8}经验",
    r"未使用",
    r"从未",
    r"\bno\b.{0,16}\bexperience\b",
    r"\bnever\b",
    r"\bnot\b(?!\s+only\b)",
    r"\bnot familiar\b",
)
ACTION_PATTERNS = (
    r"负责",
    r"主导",
    r"设计",
    r"开发",
    r"搭建",
    r"实现",
    r"优化",
    r"部署",
    r"上线",
    r"\bbuilt\b",
    r"\bdeveloped\b",
    r"\bdesigned\b",
    r"\bimplemented\b",
    r"\bdeployed\b",
)


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    if re.fullmatch(r"[A-Za-z0-9]+", keyword) and len(keyword) <= 3:
        escaped = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return re.compile(escaped, re.IGNORECASE)


def _keyword_spans(skill: dict, text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for keyword in skill.get("keywords", []):
        if not keyword:
            continue
        for match in _keyword_pattern(keyword).finditer(text):
            spans.append((match.start(), match.end(), keyword))
    return sorted(spans, key=lambda item: (item[0], item[1], item[2].lower()))


def _line_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    return line_start, len(text) if line_end == -1 else line_end


def _line_for_span(text: str, start: int, end: int) -> str:
    line_start, line_end = _line_bounds(text, start, end)
    line = text[line_start:line_end].strip()
    if len(line) <= 240:
        return line

    relative_start = max(0, start - line_start)
    window_start = min(max(0, relative_start - 80), len(line) - 240)
    return line[window_start:window_start + 240].strip()


def _context_for_span(text: str, start: int, end: int) -> tuple[str, int, int]:
    line_start, line_end = _line_bounds(text, start, end)
    line = text[line_start:line_end]
    relative_start = start - line_start
    relative_end = end - line_start

    separators = list(re.finditer(r"[.;。！？!?]|\b(?:but|however|yet)\b|但是|不过|然而|但", line, re.I))
    context_start = 0
    context_end = len(line)
    for separator in separators:
        if separator.end() <= relative_start:
            context_start = separator.end()
        elif separator.start() >= relative_end:
            context_end = separator.start()
            break

    return (
        line[context_start:context_end],
        relative_start - context_start,
        relative_end - context_start,
    )


def _has_tool_use_coordination_reset(
    text: str,
    current_skill_keywords: list[str],
) -> bool:
    """Reset after a completed ``used <tool>`` denial and before a new action.

    The classifier has no entity catalogue, so token capitalization cannot prove
    that the first conjunct names a different skill.  A single-object tool-use
    predicate is the narrow syntactic transition supported by this interface;
    coordinated resume actions such as ``designed ... and developed ...`` keep
    sharing the preceding negation.
    """
    for coordinator in re.finditer(r"\band\b", text, re.IGNORECASE):
        preceding = text[:coordinator.start()].strip()
        tool_use = re.fullmatch(
            r"used\s+(?P<object>[^\s,，;；]+)",
            preceding,
            re.IGNORECASE,
        )
        if not tool_use:
            continue
        denied_object = tool_use.group("object")
        if any(
            _keyword_pattern(keyword).fullmatch(denied_object)
            for keyword in current_skill_keywords
            if keyword
        ):
            continue
        following = text[coordinator.end():]
        if any(
            re.match(rf"\s*(?:{pattern})", following, re.IGNORECASE)
            for pattern in ACTION_PATTERNS
        ):
            return True
    return False


def _is_negated(
    text: str,
    span: tuple[int, int, str],
    current_skill_keywords: list[str],
) -> bool:
    context, keyword_start, keyword_end = _context_for_span(
        text,
        span[0],
        span[1],
    )
    for pattern in NEGATION_PATTERNS:
        for negation in re.finditer(pattern, context, re.IGNORECASE):
            if negation.start() <= keyword_start:
                between = context[negation.end():keyword_start]
                if (
                    not re.search(r"[,，;；]", between)
                    and not _has_tool_use_coordination_reset(
                        between,
                        current_skill_keywords,
                    )
                ):
                    return True
                continue

            between = context[keyword_end:negation.start()]
            if re.search(r"[,，;；]|\b(?:and|but)\b|以及|并且|但是", between, re.I):
                continue
            stripped = between.strip(" \t:：—-")
            if not stripped or re.fullmatch(
                r"(?:[A-Za-z0-9_-]+\s+){0,4}(?:is|was|were|has|have|had|do|does|did)",
                stripped,
                re.IGNORECASE,
            ):
                return True
    return False


def _has_action_context(text: str, span: tuple[int, int, str]) -> bool:
    context, _, _ = _context_for_span(text, span[0], span[1])
    return any(re.search(pattern, context, re.IGNORECASE) for pattern in ACTION_PATTERNS)


def _unique(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def classify_skill_evidence(skill: dict, resume_text: str) -> EvidenceMatch:
    text = resume_text or ""
    spans = _keyword_spans(skill, text)
    if not spans:
        return EvidenceMatch(
            status="not_found",
            evidence=(),
            matched_keywords=(),
            reason="no_keyword",
        )

    skill_keywords = skill.get("keywords", [])
    non_negated = [
        span
        for span in spans
        if not _is_negated(text, span, skill_keywords)
    ]
    if not non_negated:
        return EvidenceMatch(
            status="not_found",
            evidence=_unique([_line_for_span(text, *span[:2]) for span in spans]),
            matched_keywords=_unique([span[2] for span in spans]),
            reason="explicit_negation",
        )

    action_spans = [span for span in non_negated if _has_action_context(text, span)]
    if action_spans:
        return EvidenceMatch(
            status="evidenced",
            evidence=_unique([_line_for_span(text, *span[:2]) for span in action_spans]),
            matched_keywords=_unique([span[2] for span in action_spans]),
            reason="action_context",
        )

    return EvidenceMatch(
        status="uncertain",
        evidence=_unique([_line_for_span(text, *span[:2]) for span in non_negated]),
        matched_keywords=_unique([span[2] for span in non_negated]),
        reason="keyword_without_experience_context",
    )
