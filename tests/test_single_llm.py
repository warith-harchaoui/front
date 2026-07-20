"""
test_single_llm — enforce the one-authorized-LLM rule.

House rule (absolute): the ONLY LLM the front skills use is ``gemma3:4b`` via
Ollama. No other model tag, no MLX, anywhere in the skill scripts — forever.
This test makes that machine-checkable, the same way the repo gates skill-spec
conformance and Claude-trailer-free commits.

Scope: every ``front-*/scripts/*.py``. Not an LLM (allowed, unchecked):
whisper.cpp (captions), NeMo Sortformer/TitaNet (diarization), SHAP/DoWhy
(figures) — those are ASR / diarization / stats models, not the Ollama LLM.

Author
------
Project maintainers.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Every shipped skill's Python scripts.
SCRIPTS = sorted(
    p for p in REPO_ROOT.glob("front-*/scripts/*.py")
    if "__pycache__" not in p.parts
)

#: Model families that are NOT the one authorized LLM. Any literal mention in a
#: skill script is a violation. ``gemma3:4b`` is deliberately absent — it is the
#: only allowed tag. (Word-boundary so ``gemma3:4b`` never matches ``gemma3n``.)
FORBIDDEN_MODEL = re.compile(
    r"\b(?:gemma4\w*|gemma3:12b|gemma3n\w*|gemma2\w*|llava\w*|moondream\w*|"
    r"qwen[\d.]\w*|llama3[\d.]*-?vision\w*|mistral\w*|phi[\d]\w*|deepseek\w*)\b",
    re.IGNORECASE,
)

#: A concrete ``model:tag-mlx`` literal (an MLX build). "No MLX" prose is fine;
#: an actual ``…-mlx`` tag is not.
MLX_TAG = re.compile(r"[\w.]+:[\w.]*-mlx\b", re.IGNORECASE)


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_no_forbidden_model_tag(script: Path) -> None:
    """A skill script must not name any LLM model tag other than gemma3:4b."""
    text = script.read_text(encoding="utf-8")
    hits = sorted(set(FORBIDDEN_MODEL.findall(text)))
    assert not hits, (
        f"{script.relative_to(REPO_ROOT)} names non-authorized model tag(s) {hits}. "
        "The one authorized LLM is gemma3:4b via Ollama (see memory single_llm_gemma3_4b)."
    )


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_no_mlx_tag(script: Path) -> None:
    """A skill script must not name an MLX model tag (``…-mlx``)."""
    text = script.read_text(encoding="utf-8")
    hits = sorted(set(MLX_TAG.findall(text)))
    assert not hits, (
        f"{script.relative_to(REPO_ROOT)} names an MLX tag {hits}. No MLX — gemma3:4b only."
    )


def test_gemma3_4b_is_the_declared_default() -> None:
    """The Ollama-backed scripts that declare a default model use gemma3:4b."""
    # These are the scripts with a hard-coded default model constant.
    declarers = [
        REPO_ROOT / "front-vision" / "scripts" / "alt_from_ollama.py",
        REPO_ROOT / "front-vision" / "scripts" / "install_alt_ai.py",
        REPO_ROOT / "front-publish" / "scripts" / "_ollama.py",
        REPO_ROOT / "front-audio" / "scripts" / "name_from_transcript.py",
        REPO_ROOT / "front-audio" / "scripts" / "translate_captions.py",
        REPO_ROOT / "front-publish" / "scripts" / "narrate_post.py",
    ]
    for script in declarers:
        assert '"gemma3:4b"' in script.read_text(encoding="utf-8"), (
            f"{script.relative_to(REPO_ROOT)} must declare gemma3:4b as its default model."
        )


#: The Ollama-LLM scripts. The model is fixed at gemma3:4b for all of them —
#: none may expose a user-facing switch to pick a different LLM. (whisper.cpp
#: ``--model`` in front-audio/captions is an ASR model, not the LLM, so it is
#: intentionally NOT in this list.)
LLM_SCRIPTS = [
    REPO_ROOT / "front-vision" / "scripts" / "alt_from_ollama.py",
    REPO_ROOT / "front-vision" / "scripts" / "install_alt_ai.py",
    REPO_ROOT / "front-audio" / "scripts" / "name_from_transcript.py",
    REPO_ROOT / "front-audio" / "scripts" / "translate_captions.py",
    REPO_ROOT / "front-publish" / "scripts" / "plain_language.py",
    REPO_ROOT / "front-publish" / "scripts" / "meta_from_ollama.py",
    REPO_ROOT / "front-publish" / "scripts" / "narrate_post.py",
]

#: An option-definition literal that would expose the LLM model on the command
#: line — click ``@click.option("--model"...)`` or argparse
#: ``add_argument("--model"...)`` / ``"--ai-hints-model"``. Prose mentions and
#: internal ``model=`` kwargs are fine; a *defined CLI flag* is the violation.
_MODEL_FLAG = re.compile(r'"--(?:model|ai-hints-model)"')


@pytest.mark.parametrize("script", LLM_SCRIPTS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_llm_model_is_not_user_selectable(script: Path) -> None:
    """No LLM script may expose a ``--model`` (or ``--ai-hints-model``) CLI flag.

    The one authorized LLM is gemma3:4b, fixed — not a knob. ``OLLAMA_MODEL``
    survives only as a bare test seam (env var, never a documented user option).
    """
    text = script.read_text(encoding="utf-8")
    assert not _MODEL_FLAG.search(text), (
        f"{script.relative_to(REPO_ROOT)} defines a user-facing model flag. "
        "The LLM is fixed at gemma3:4b — remove the --model / --ai-hints-model option "
        "(see memory single_llm_gemma3_4b)."
    )


@pytest.mark.parametrize(
    "skill_md",
    sorted(REPO_ROOT.glob("front-*/SKILL.md")),
    ids=lambda p: p.parent.name,
)
def test_skill_description_advertises_no_model_override(skill_md: Path) -> None:
    """A skill's ``description:`` frontmatter must not advertise a model override.

    The user-facing contract is one model, gemma3:4b. A description that dangles
    ``OLLAMA_MODEL`` / ``--model`` as an override contradicts the lock and is the
    exact drift this gate prevents (see the v0.25.0 assessment).
    """
    text = skill_md.read_text(encoding="utf-8")
    # Isolate the YAML ``description:`` block (up to the next top-level key).
    m = re.search(r"(?ms)^description:\s*>-?\n(.*?)^\w[\w-]*:", text)
    description = m.group(1) if m else ""
    for needle in ("OLLAMA_MODEL", "--model"):
        assert needle not in description, (
            f"{skill_md.relative_to(REPO_ROOT)} description advertises {needle!r}. "
            "The model is fixed at gemma3:4b — do not surface an override in the description."
        )
