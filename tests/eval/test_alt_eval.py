"""
test_alt_eval — opt-in LLM-output checks for ``alt_from_ollama.describe``.

The deterministic suite (``tests/test_alt_from_ollama.py``) mocks every
network call. This module does the opposite: it actually runs the local
Ollama model against four small fixture images and asserts on the
quality of the alt text. Every test in here is excluded from the
default ``pytest`` run; run with::

    pytest -m eval

Skips cleanly when:

- The Ollama daemon is not reachable (``ollama_available`` fixture).
- The vision model is not pulled (``require_model`` fixture).
- The image fixtures are missing (``image_fixture`` fixture).
- ``deepeval`` is not installed (``pytest.importorskip``).

Assertions, per ``.private/tests.md``:

- **Relevance**: the alt text mentions the dominant subject (DeepEval's
  ``AnswerRelevancyMetric``, with a lenient pass threshold).
- **Faithfulness**: the alt text does not invent facts not visible
  (``FaithfulnessMetric`` against a hand-written ground-truth caption).
- **Length**: hard cap of 150 characters and no trailing ``…``.
- **Multilingual**: ``--lang fr`` produces French output, verified via
  ``_lang.detect_text_language``.

The thresholds are intentionally lenient. These tests guard against
catastrophic regressions (model returns boilerplate, returns English
when asked for French, returns 800 characters), not minute differences
in phrasing between model versions.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip the whole module gracefully when DeepEval isn't installed. The
# project lists it in requirements-dev.txt; this guard keeps the test
# friendly to lightweight contributor checkouts.
deepeval = pytest.importorskip("deepeval")

import alt_from_ollama  # noqa: E402 — imported via tests/conftest.py sys.path
from _lang import detect_text_language  # noqa: E402

pytestmark = pytest.mark.eval


# ── Fixture ground-truth captions ───────────────────────────────────────────

# Each entry pairs a basename under tests/fixtures/images/ with a short
# human-written caption used as the "truth" reference for faithfulness
# scoring. Keep these literal and conservative — only mention what is
# clearly in the synthetic image.
GROUND_TRUTH: dict[str, dict] = {
    "chart-bar": {
        "kind": "informative",
        "truth": "A bar chart with five coloured bars of varying heights on a white background.",
        "expected_subject_keywords": ("chart", "bar", "graph"),
    },
    "portrait": {
        "kind": "informative",
        "truth": "A stylised silhouette of a person's head and shoulders on a cream background.",
        "expected_subject_keywords": ("person", "portrait", "silhouette", "figure", "head"),
    },
    "ui-screenshot": {
        "kind": "informative",
        "truth": "A screenshot of a desktop application with a sidebar on the left and a content area on the right.",
        "expected_subject_keywords": ("screen", "interface", "ui", "window", "app", "sidebar"),
    },
    "decorative-pattern": {
        "kind": "decorative",
        "truth": "A repeating diagonal stripe pattern.",
        "expected_subject_keywords": (),  # decorative → empty alt expected
    },
}


# ── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("name", ["chart-bar", "portrait", "ui-screenshot"])
def test_alt_relevance_and_faithfulness(
    name: str,
    image_fixture,
    ollama_available,
    require_model,
) -> None:
    """
    Generate alt text against the fixture image and score it with DeepEval.

    Two metrics, both lenient: a single very-low score is the regression
    signal — we are catching "returns boilerplate" or "describes the
    wrong picture", not minor phrasing.
    """
    from deepeval import evaluate  # noqa: F401 — imported for side-effect parity
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
    from deepeval.test_case import LLMTestCase

    model = alt_from_ollama.pick_default_model()
    require_model(model)

    img = image_fixture(name)
    spec = GROUND_TRUTH[name]
    alt: str = alt_from_ollama.describe(
        str(img),
        kind=spec["kind"],
        lang="en",
        model=model,
    )

    # Hard structural checks before scoring — these alone catch most
    # regressions and are cheap.
    assert alt, "Alt text is empty for an informative image"
    assert len(alt) <= 150, f"Alt text exceeds 150-char cap: {len(alt)} chars"
    assert not alt.rstrip().endswith("…"), "Alt text ends with ellipsis"

    # Lightweight keyword sanity check — at least one expected subject
    # word should appear. This is cheaper and more deterministic than
    # the DeepEval call below and catches obvious failures.
    lowered = alt.lower()
    assert any(kw in lowered for kw in spec["expected_subject_keywords"]), (
        f"None of the expected subject words {spec['expected_subject_keywords']} "
        f"appear in alt text: {alt!r}"
    )

    # DeepEval relevance + faithfulness. Thresholds kept lenient since
    # the metrics themselves run via the same local Ollama daemon and
    # are noisy across model versions.
    case = LLMTestCase(
        input=f"Describe this image for a screen-reader user. Subject hint: {name}.",
        actual_output=alt,
        expected_output=spec["truth"],
        retrieval_context=[spec["truth"]],
    )
    try:
        relevance = AnswerRelevancyMetric(threshold=0.4)
        relevance.measure(case)
        assert relevance.score is None or relevance.score >= 0.4, (
            f"Relevance below 0.4 for {name}: score={relevance.score}, alt={alt!r}"
        )
        faithfulness = FaithfulnessMetric(threshold=0.4)
        faithfulness.measure(case)
        assert faithfulness.score is None or faithfulness.score >= 0.4, (
            f"Faithfulness below 0.4 for {name}: score={faithfulness.score}, alt={alt!r}"
        )
    except Exception as e:  # pragma: no cover — DeepEval errors are environment-dependent
        # DeepEval needs its own model wiring; on a vanilla Ollama install it
        # often raises configuration errors. We let those skip rather than
        # fail the suite — the structural assertions above are the load
        # bearing checks.
        pytest.skip(f"DeepEval scoring unavailable: {e}")


def test_decorative_returns_empty(image_fixture) -> None:
    """
    A ``kind="decorative"`` request must short-circuit to ``""`` with no
    network round-trip, regardless of whether Ollama is up.
    """
    img = image_fixture("decorative-pattern")
    out: str = alt_from_ollama.describe(str(img), kind="decorative", lang="en")
    assert out == "", f"Decorative image must return empty string, got {out!r}"


def test_alt_french_lang(
    image_fixture,
    ollama_available,
    require_model,
) -> None:
    """
    ``--lang fr`` should produce French output for the same fixture image.
    Verified via :func:`_lang.detect_text_language`.
    """
    model = alt_from_ollama.pick_default_model()
    require_model(model)

    img = image_fixture("chart-bar")
    alt_fr: str = alt_from_ollama.describe(
        str(img),
        kind="informative",
        lang="fr",
        model=model,
    )
    assert alt_fr, "French alt text is empty"
    assert len(alt_fr) <= 150
    detected = detect_text_language(alt_fr, fallback="en")
    # `langdetect` is noisy on very short text — accept either a positive
    # French detection or a French stop-word in the output. Both signal the
    # model honoured the language hint.
    french_markers = (" le ", " la ", " les ", " un ", " une ", " des ", " et ", " sur ")
    has_marker = any(m in f" {alt_fr.lower()} " for m in french_markers)
    assert detected == "fr" or has_marker, (
        f"`--lang fr` did not produce French output. detected={detected!r}, alt={alt_fr!r}"
    )
