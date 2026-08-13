"""Tests the fail-loud local-only model verification reference implementation
(TR-SEC-003, v0.7 export) in examples/local-only-model-registry/registry.py.

Contract under test: every field checked resolves to a "local" MODEL_REGISTRY
entry when require_local_only is set, or validate_local_only() raises -- for
both a registered-cloud model and an unregistered model string.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "local-only-model-registry"
sys.path.insert(0, str(EXAMPLE_DIR))

from registry import MODEL_REGISTRY, ModelInfo, validate_local_only


def test_drift_guard_every_default_is_registered() -> None:
    """Every model this example ships must have a MODEL_REGISTRY entry --
    the same 'unreviewed grant' shape agent-permission-guard.py (TR-SEC-010)
    and examples/provenance-trust-tags/ (TR-SEC-011) guard against."""
    shipped_defaults = [
        "local/embedding-model",
        "local/vision-model",
        "cloud/classification-model",
        "cloud/synthesis-model",
    ]
    for model in shipped_defaults:
        assert model in MODEL_REGISTRY, f"{model!r} missing from MODEL_REGISTRY"


def test_disabled_by_default_is_a_noop_even_with_cloud_models() -> None:
    validate_local_only(
        require_local_only=False,
        model_fields={"llm.synthesis_model": "cloud/synthesis-model"},
    )  # must not raise


def test_registered_cloud_model_raises_when_required_local() -> None:
    with pytest.raises(ValueError, match="llm.synthesis_model"):
        validate_local_only(
            require_local_only=True,
            model_fields={"llm.synthesis_model": "cloud/synthesis-model"},
        )


def test_registered_local_model_passes_when_required_local() -> None:
    validate_local_only(
        require_local_only=True,
        model_fields={"embeddings.model": "local/embedding-model"},
    )  # must not raise


def test_unregistered_model_raises_rather_than_passing_silently() -> None:
    """The pattern's central claim: an unverifiable model string must fail
    loud, not be treated as trusted-local by omission."""
    with pytest.raises(ValueError, match="not in MODEL_REGISTRY"):
        validate_local_only(
            require_local_only=True,
            model_fields={"llm.synthesis_model": "some/new-model-nobody-registered"},
        )


def test_every_candidate_field_is_checked_not_just_the_first() -> None:
    with pytest.raises(ValueError, match="write_path.vision_model"):
        validate_local_only(
            require_local_only=True,
            model_fields={
                "embeddings.model": "local/embedding-model",
                "write_path.vision_model": "cloud/classification-model",
            },
        )


def test_model_info_provider_family_local_or_cloud() -> None:
    assert MODEL_REGISTRY["local/embedding-model"] == ModelInfo("local", "http://localhost:11434")
    assert MODEL_REGISTRY["cloud/synthesis-model"] == ModelInfo("cloud")
