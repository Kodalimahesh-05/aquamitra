"""
AquaMitra AI Safety & Guardrails Layer
Enforces non-diagnostic, responsible, and non-guaranteed aquaculture wording.
"""

import re
from typing import Tuple

# Prohibited diagnostic and guarantee assertions
PROHIBITED_TERMS = [
    r"\bguarantee(d|s)?\s+(profit|yield|survival|income)\b",
    r"\bdiagnos(e|ed|is)\b",
    r"\byour fish (have|suffer from|contracted) [a-zA-Z\s]+(disease|infection|virus|bacteria)\b",
    r"\bwill (definitely|certainly) die\b",
    r"\bprescribe\b",
    r"\bthe system (adjusted|activated|turned on) the (aerator|pump|feeder)\b"
]

MANDATORY_ADVISORY = (
    "\n\n*Suggested Action: Recheck relevant parameters and monitor pond conditions closely. "
    "Consult a qualified fisheries professional or veterinary specialist if the condition persists.*"
)


def check_prohibited_terms(text: str) -> Tuple[bool, list]:
    """
    Checks if a string contains any prohibited claims or unsupported medical assertions.
    """
    violations = []
    for pattern in PROHIBITED_TERMS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(pattern)
    return len(violations) > 0, violations


def enforce_ai_safety(text: str, append_advisory: bool = False) -> str:
    """
    Sanitizes AI-generated text to ensure adherence to decision-support guidelines.
    Replaces aggressive causal or diagnostic claims with responsible phrasing.
    """
    if not text:
        return ""

    sanitized = text

    # Soften causal claims
    sanitized = re.sub(
        r"\bcaused the mortality\b",
        "occurred around the same period as the mortality",
        sanitized,
        flags=re.IGNORECASE
    )
    sanitized = re.sub(
        r"\bproves the fish are diseased\b",
        "indicates conditions requiring attention",
        sanitized,
        flags=re.IGNORECASE
    )
    sanitized = re.sub(
        r"\bguaranteed profit\b",
        "estimated net difference",
        sanitized,
        flags=re.IGNORECASE
    )

    if append_advisory and "consult a qualified fisheries" not in sanitized.lower():
        sanitized += MANDATORY_ADVISORY

    return sanitized.strip()
