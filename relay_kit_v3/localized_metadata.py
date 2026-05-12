from __future__ import annotations

from typing import Any, Mapping


DEFAULT_LOCALE = "en"
SUPPORTED_LOCALE_PACKS = {"en", "vi"}

SKILL_DESCRIPTION_OVERRIDES: dict[str, dict[str, str]] = {
    "vi": {
        "go-service-engineering": "Dùng khi yêu cầu tập trung vào backend Go service. Thiết kế ranh giới service, routing, persistence, middleware, jobs, cache và bằng chứng test cho mức production.",
        "next-product-frontend": "Dùng khi công việc tập trung vào Next.js product UI hoặc kiến trúc frontend. Lập kế hoạch và triển khai App Router, ranh giới server/client, server actions, data fetching và các gate chất lượng.",
        "growth-marketing": "Dùng khi yêu cầu tập trung vào tăng trưởng hoặc triển khai marketing. Xây định vị, kế hoạch chiến dịch, checklist launch, funnel metrics và kiểm định chất lượng theo mục tiêu sản phẩm.",
        "market-research": "Dùng khi cần intelligence thị trường, tinh chỉnh ICP, phân tích tín hiệu pricing hoặc kiểm định giả thuyết thị trường trước khi thực thi.",
        "automation-ops": "Dùng khi yêu cầu là automation workflow hoặc scripting vận hành. Định nghĩa scheduler, webhook, runbook, rollback safety và kỷ luật dry-run.",
        "vietnamese-product-localization": "Dùng khi output sản phẩm cần bản địa hóa cho người dùng Việt Nam. Tạo tài liệu tiếng Việt hoặc song ngữ, support copy, release notes và giao tiếp với ràng buộc chất lượng.",
    },
}

COMMAND_INTENT_OVERRIDES: dict[str, dict[str, str]] = {
    "vi": {
        "relay-start": "Bắt đầu một yêu cầu với routing rõ ràng và lane mode cụ thể.",
        "relay-plan": "Tạo artifacts kế hoạch sẵn sàng triển khai và thứ tự slice.",
        "relay-build": "Thực thi thay đổi implementation trong lane đang hoạt động.",
        "relay-token-audit": "Kiểm toán token budget, độ an toàn nén context và mức giữ tín hiệu trước khi thực thi.",
    },
}

COMMAND_EVIDENCE_OVERRIDES: dict[str, dict[str, str]] = {
    "vi": {
        "relay-start": "workflow-state được cập nhật với track/hub/next-skill đã chọn.",
        "relay-plan": "artifacts kế hoạch được cập nhật với acceptance và thứ tự delivery.",
        "relay-token-audit": "token audit report với budget violations, raw pointers và retention metrics.",
    },
}

AGENT_DISPLAY_NAME_OVERRIDES: dict[str, dict[str, str]] = {
    "vi": {
        "relay-engineer": "Relay Ky Su",
        "relay-growth": "Relay Tang Truong",
    },
}

AGENT_INTENT_OVERRIDES: dict[str, dict[str, str]] = {
    "vi": {
        "relay-engineer": "Triển khai công việc kỹ thuật với planning, verification và readiness gate chặt chẽ.",
        "relay-growth": "Thực thi tăng trưởng dựa trên research với launch/support artifacts có thể đo lường.",
    },
}

AGENT_EVIDENCE_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "vi": {
        "relay-engineer": [
            "scoped implementation diff cùng test hoặc verification output",
            "review findings với residual risk hoặc pass rõ ràng",
            "readiness và policy gates gắn với quyết định release",
        ],
        "relay-growth": [
            "research findings có xếp hạng nguồn và tác động ICP/pricing",
            "kế hoạch campaign/funnel kèm checklist launch QA",
            "runbook automation kèm dry-run và rollback discipline",
        ],
    },
}

LOCALE_TRIGGER_PREFIX: dict[str, str] = {
    "en": "Use when ",
    "vi": "Dùng khi ",
}


def normalize_locale(locale: str | None) -> str:
    if locale is None:
        return DEFAULT_LOCALE
    value = str(locale).strip().replace("_", "-").lower()
    return value or DEFAULT_LOCALE


def locale_candidates(locale: str | None) -> list[str]:
    normalized = normalize_locale(locale)
    candidates: list[str] = []
    if normalized:
        candidates.append(normalized)
    if "-" in normalized:
        base = normalized.split("-", 1)[0]
        if base and base not in candidates:
            candidates.append(base)
    if DEFAULT_LOCALE not in candidates:
        candidates.append(DEFAULT_LOCALE)
    return candidates


def _specific_locale_candidates(locale: str | None) -> list[str]:
    normalized = normalize_locale(locale)
    candidates: list[str] = []
    if normalized:
        candidates.append(normalized)
    if "-" in normalized:
        base = normalized.split("-", 1)[0]
        if base and base not in candidates:
            candidates.append(base)
    return candidates


def locale_pack(locale: str | None) -> str:
    for candidate in locale_candidates(locale):
        if candidate in SUPPORTED_LOCALE_PACKS:
            return candidate
    return DEFAULT_LOCALE


def resolve_locale_pack(locale: str | None, fallback_locale: str | None = None) -> str:
    ordered_candidates: list[str] = []
    for candidate in _specific_locale_candidates(locale):
        if candidate not in ordered_candidates:
            ordered_candidates.append(candidate)
    for candidate in _specific_locale_candidates(fallback_locale):
        if candidate not in ordered_candidates:
            ordered_candidates.append(candidate)
    if DEFAULT_LOCALE not in ordered_candidates:
        ordered_candidates.append(DEFAULT_LOCALE)
    for candidate in ordered_candidates:
        if candidate in SUPPORTED_LOCALE_PACKS:
            return candidate
    return DEFAULT_LOCALE


def resolve_metadata_locale(locale_policy: Mapping[str, Any] | None) -> str:
    if not locale_policy:
        return DEFAULT_LOCALE
    locale_profile = locale_policy.get("locale_profile")
    fallback_locale = locale_policy.get("fallback_locale")
    return resolve_locale_pack(
        str(locale_profile) if isinstance(locale_profile, str) else None,
        str(fallback_locale) if isinstance(fallback_locale, str) else None,
    )


def expected_trigger_prefixes(locale: str | None, fallback_locale: str | None = None) -> list[str]:
    pack = resolve_locale_pack(locale, fallback_locale)
    prefixes = [LOCALE_TRIGGER_PREFIX.get(pack, LOCALE_TRIGGER_PREFIX[DEFAULT_LOCALE])]
    if LOCALE_TRIGGER_PREFIX[DEFAULT_LOCALE] not in prefixes:
        prefixes.append(LOCALE_TRIGGER_PREFIX[DEFAULT_LOCALE])
    return prefixes


def localized_skill_description(
    skill_name: str,
    base_description: str,
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> str:
    pack = resolve_locale_pack(locale, fallback_locale)
    override = _lookup_map(localized_map=SKILL_DESCRIPTION_OVERRIDES, key=skill_name, locale=pack)
    if override is not None:
        return override
    if pack == DEFAULT_LOCALE:
        return base_description
    english_prefix = LOCALE_TRIGGER_PREFIX[DEFAULT_LOCALE]
    if base_description.startswith(english_prefix):
        suffix = base_description[len(english_prefix) :]
        localized_prefix = LOCALE_TRIGGER_PREFIX.get(pack, english_prefix)
        return f"{localized_prefix}{suffix}"
    return base_description


def localized_command_intent(
    command_id: str,
    base_intent: str,
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> str:
    pack = resolve_locale_pack(locale, fallback_locale)
    override = _lookup_map(localized_map=COMMAND_INTENT_OVERRIDES, key=command_id, locale=pack)
    if override is not None:
        return override
    if pack == "vi":
        return f"Muc tieu: {base_intent}"
    return base_intent


def localized_command_evidence(
    command_id: str,
    base_evidence: str,
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> str:
    pack = resolve_locale_pack(locale, fallback_locale)
    override = _lookup_map(localized_map=COMMAND_EVIDENCE_OVERRIDES, key=command_id, locale=pack)
    if override is not None:
        return override
    if pack == "vi":
        return f"Bang chung mong doi: {base_evidence}"
    return base_evidence


def localized_agent_display_name(
    profile_id: str,
    base_display_name: str,
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> str:
    pack = resolve_locale_pack(locale, fallback_locale)
    override = _lookup_map(localized_map=AGENT_DISPLAY_NAME_OVERRIDES, key=profile_id, locale=pack)
    return override if override is not None else base_display_name


def localized_agent_intent(
    profile_id: str,
    base_intent: str,
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> str:
    pack = resolve_locale_pack(locale, fallback_locale)
    override = _lookup_map(localized_map=AGENT_INTENT_OVERRIDES, key=profile_id, locale=pack)
    if override is not None:
        return override
    if pack == "vi":
        return f"Y dinh: {base_intent}"
    return base_intent


def localized_agent_evidence(
    profile_id: str,
    base_evidence: list[str],
    *,
    locale: str | None,
    fallback_locale: str | None = None,
) -> list[str]:
    pack = resolve_locale_pack(locale, fallback_locale)
    locale_map = AGENT_EVIDENCE_OVERRIDES.get(pack, {})
    override = locale_map.get(profile_id)
    if override is not None:
        return list(override)
    if pack == DEFAULT_LOCALE:
        return list(base_evidence)
    label = "Bang chung: " if pack == "vi" else "Evidence: "
    return [f"{label}{item}" for item in base_evidence]


def _lookup_map(*, localized_map: Mapping[str, Mapping[str, Any]], key: str, locale: str) -> str | None:
    locale_map = localized_map.get(locale)
    if not locale_map:
        return None
    value = locale_map.get(key)
    if isinstance(value, str):
        return value
    return None
