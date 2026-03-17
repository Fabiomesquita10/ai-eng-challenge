"""Guardrails: safety and compliance layer. Pass-through for now."""


def guardrails_agent(state: dict) -> dict:
    """
    Validate input/output and enforce policies.
    Currently pass-through: returns state unchanged.
    TODO: Add validation, blocklist, policy checks.
    """
    return {}
