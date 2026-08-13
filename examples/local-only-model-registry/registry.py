"""Reference implementation: fail-loud local-only model verification (TR-SEC-003).

The pattern in three parts:

1. Declare provider metadata once. ``MODEL_REGISTRY`` maps each known model
   string to a ``ModelInfo`` naming its provider family ("local" | "cloud").
   Task-level config (a classification model, a synthesis model, an embedding
   model, ...) stores the model string; the registry is the one place that
   knows what that string actually resolves to.
2. Verify at the single choke point every caller already passes through, not
   at each caller separately. ``validate_local_only()`` is meant to be called
   from inside whatever one function already builds the running config for
   every entry point (a ``load_config()``, a settings loader, an app
   factory) -- not duplicated into each entry point's own startup path. Two
   call sites that both need to remember to enforce the same check is the
   shape that lets enforcement quietly stop happening (see "Why fail loud"
   below).
3. Fail loud on the unverifiable case, not just the known-bad case. A model
   string absent from ``MODEL_REGISTRY`` raises, exactly like one that is
   registered but resolves to "cloud" -- it is not treated as trusted-local
   by omission.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    provider_family: str  # "local" | "cloud"
    base_url: str | None = None  # None for cloud providers


# The single source of truth. Every model string a caller might configure for
# a registry-eligible field must appear here before require_local_only can
# verify it -- see test_drift_guard_every_default_is_registered below for how
# a project should guard this as its own model list grows.
MODEL_REGISTRY: dict[str, ModelInfo] = {
    "local/embedding-model": ModelInfo("local", "http://localhost:11434"),
    "local/vision-model": ModelInfo("local", "http://localhost:11434"),
    "cloud/classification-model": ModelInfo("cloud"),
    "cloud/synthesis-model": ModelInfo("cloud"),
}


def validate_local_only(require_local_only: bool, model_fields: dict[str, str]) -> None:
    """Raise if any field in ``model_fields`` resolves to a non-local provider
    while ``require_local_only`` is set.

    ``model_fields`` maps a human-readable field name (for the error message)
    to the model string currently configured for it, e.g.
    ``{"llm.classification_model": "cloud/classification-model"}``. Skip a
    field entirely (don't pass it) if it's legitimately optional and unset --
    an empty string is not itself a model to verify.

    No-op when require_local_only is False -- this function changes nothing
    about routing; it only verifies the routing that's already configured.
    """
    if not require_local_only:
        return

    for field_name, model in model_fields.items():
        info = MODEL_REGISTRY.get(model)
        if info is None:
            raise ValueError(
                f"require_local_only is set, but {field_name}={model!r} is not in "
                f"MODEL_REGISTRY, so its provider cannot be verified as local. "
                f"Register it in MODEL_REGISTRY or change {field_name} to a "
                f"registered local model."
            )
        if info.provider_family != "local":
            raise ValueError(
                f"require_local_only is set, but {field_name}={model!r} resolves "
                f"to a {info.provider_family!r} provider, not 'local'."
            )
