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

EVAL_PROMPTS_DIR = PRODUCT_ROOT / "evals" / "prompts"

# The ten golden-prompt files and the archetype each archetype prompt must name;
# adversarial and cross-skill prompts are not archetype-bound.
EVAL_PROMPT_ARCHETYPES: dict[str, str | None] = {
    "01-single-data-indicator.md": "single_data_indicator",
    "02-multi-indicator-system.md": "multi_indicator_system",
    "03-multi-asset-allocation.md": "multi_asset_allocation",
    "04-multi-timeframe.md": "multi_timeframe",
    "05-pairs-spread.md": "pairs_spread",
    "06-order-risk.md": "order_risk",
    "07-precomputed-ml.md": "precomputed_ml",
    "08-adversarial-lookahead.md": None,
    "09-adversarial-ast-bypass.md": None,
    "10-cross-skill-repair-loop.md": None,
}

EVAL_PROMPT_SECTIONS = ("Preconditions", "Prompt", "Pass criteria", "Rubric")

_ADVERSARIAL_PROMPTS = {
    "08-adversarial-lookahead.md",
    "09-adversarial-ast-bypass.md",
    "10-cross-skill-repair-loop.md",
}

# Command verbs exposed by the CLI (src/backtrader_skills/cli.py). Adversarial
# prompts may only reference the command words review, run prepare, repair, and
# spec (spec validate included).
_CLI_VERBS = {
    "doctor",
    "data",
    "catalog",
    "spec",
    "render",
    "approval",
    "review",
    "run",
    "repair",
    "install",
    "compare",
    "prepare",
    "execute",
    "validate",
    "scaffold",
    "apply",
    "preview",
    "approve",
    "revoke",
    "show",
}

_ALLOWED_CLI_PATHS = {
    ("review",),
    ("run", "prepare"),
    ("repair",),
    ("spec",),
    ("spec", "validate"),
}

_SECTION_HEADING = re.compile(r"^## ", re.MULTILINE)
_BACKTICK_SPAN = re.compile(r"`([^`]+)`")
_SKILL_NAME_TOKEN = re.compile(r"backtrader-strategy-[a-z]+")
_RUBRIC_ROW = re.compile(r"^\|.*\|$", re.MULTILINE)


def _prompt_sections(text: str) -> dict[str, str]:
    """Split a prompt file into its '## Name' sections, keyed by name."""

    sections: dict[str, str] = {}
    for part in _SECTION_HEADING.split(text)[1:]:
        lines = part.splitlines()
        sections[lines[0].strip()] = "\n".join(lines[1:]).strip()
    return sections


def test_author_contract_enumerates_the_runtime_vocabulary() -> None:
    contract = AUTHORING_CONTRACT.read_text(encoding="utf-8")
    missing = [
        value
        for value in (*ARCHETYPES, *OUTPUT_PROFILES, *sorted(EXPRESSION_KINDS))
        if value not in contract
    ]
    # Short operator tokens ("and", "or", "not", ...) match ordinary prose by
    # coincidence, so they must appear as explicitly backtick-delimited tokens.
    missing += [value for value in sorted(OPERATORS) if f"`{value}`" not in contract]
    assert not missing, f"authoring-contract.md does not name: {sorted(missing)}"


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


def test_eval_suite_reference_contract() -> None:
    prompt_files = {path.name for path in EVAL_PROMPTS_DIR.glob("*.md")}
    expected = set(EVAL_PROMPT_ARCHETYPES)
    assert prompt_files == expected, f"eval prompt drift: {sorted(prompt_files ^ expected)}"

    for name, archetype in EVAL_PROMPT_ARCHETYPES.items():
        text = (EVAL_PROMPTS_DIR / name).read_text(encoding="utf-8")
        sections = _prompt_sections(text)
        missing = [section for section in EVAL_PROMPT_SECTIONS if section not in sections]
        assert not missing, f"{name} is missing sections: {missing}"

        prompt = sections["Prompt"]
        assert prompt, f"{name} has an empty Prompt section"
        assert any(skill in prompt for skill in SKILLS), f"{name} Prompt names no skill"
        assert any(value in prompt for value in ARCHETYPES), f"{name} Prompt names no archetype"
        if archetype is not None:
            assert archetype in text, f"{name} does not contain its archetype: {archetype}"

        rubric_rows = len(_RUBRIC_ROW.findall(sections["Rubric"])) - 2
        assert 3 <= rubric_rows <= 5, f"{name} Rubric has {rubric_rows} scored rows (want 3-5)"

        if name in _ADVERSARIAL_PROMPTS:
            for skill in _SKILL_NAME_TOKEN.findall(text):
                assert skill in SKILLS, f"{name} references unknown skill: {skill}"
            for span in _BACKTICK_SPAN.findall(text):
                verbs = tuple(token for token in span.split() if token in _CLI_VERBS)
                if not verbs:
                    continue
                assert verbs in _ALLOWED_CLI_PATHS, (
                    f"{name} references unsupported CLI command words: `{span}`"
                )

    assert (PRODUCT_ROOT / "scripts" / "record_eval.py").is_file(), (
        "scripts/record_eval.py is missing from the repo"
    )
    assert (PRODUCT_ROOT / "evals" / "README.md").is_file(), "evals/README.md is missing"
