from __future__ import annotations

import re

from backtrader_skills.ir import ARCHETYPES, EXPRESSION_KINDS, OPERATORS, OUTPUT_PROFILES

from .conftest import PRODUCT_ROOT

SKILLS = ("backtrader-strategy-author", "backtrader-strategy-review", "backtrader-strategy-test")

AUTHORING_CONTRACT = (
    PRODUCT_ROOT / "skills" / "backtrader-strategy-author" / "references" / "authoring-contract.md"
)
REVIEW_RULES = (
    PRODUCT_ROOT / "skills" / "backtrader-strategy-review" / "references" / "review-rules.md"
)
VALIDATION_SOURCE = PRODUCT_ROOT / "src" / "backtrader_skills" / "validation.py"

# Diagnostic code string literals. The [A-Z] class requires at least one letter
# after the prefix underscore, so bare startswith("BT_") / startswith("SEC_")
# prefixes do not match.
_DIAGNOSTIC_CODE = re.compile(r'"(?P<code>(?:SEC|BT|PY)_[A-Z][A-Z_]*)')

# Markdown inline link targets; .md targets with a URL scheme or anchor suffix
# are ignored.
_LINK_TARGET = re.compile(r"\]\(([^)]+)\)")


def test_author_contract_enumerates_the_runtime_vocabulary() -> None:
    contract = AUTHORING_CONTRACT.read_text(encoding="utf-8")
    vocabulary = (
        *ARCHETYPES,
        *OUTPUT_PROFILES,
        *sorted(EXPRESSION_KINDS),
        *sorted(OPERATORS),
    )
    missing = sorted({value for value in vocabulary if value not in contract})
    assert not missing, f"authoring-contract.md does not name: {missing}"


def test_review_rules_cover_every_diagnostic_code() -> None:
    source = VALIDATION_SOURCE.read_text(encoding="utf-8")
    codes = _DIAGNOSTIC_CODE.findall(source)
    assert len(codes) > 5, f"diagnostic code scanner found only {len(codes)} codes"

    rules = REVIEW_RULES.read_text(encoding="utf-8")
    missing = sorted({code for code in codes if code not in rules})
    assert not missing, f"review-rules.md does not cover: {missing}"


def _linked_markdown_files(skill: str) -> list[str]:
    skill_md = (PRODUCT_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    return [
        target
        for target in _LINK_TARGET.findall(skill_md)
        if target.endswith(".md") and "://" not in target
    ]


def test_skill_structure_invariants() -> None:
    for skill in SKILLS:
        skill_dir = PRODUCT_ROOT / "skills" / skill
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        assert len(text.splitlines()) <= 60, f"{skill}/SKILL.md exceeds 60 lines"

        links = _linked_markdown_files(skill)
        for target in links:
            assert (skill_dir / target).is_file(), f"{skill}/SKILL.md links missing {target}"

        assert any(
            "worked-example" in target for target in links
        ), f"{skill}/SKILL.md does not link a worked-example reference"
        assert any(
            "failure-playbook" in target for target in links
        ), f"{skill}/SKILL.md does not link a failure-playbook reference"
