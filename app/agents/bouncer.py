"""Bouncer agent: customer classification (regular, premium, not_customer)."""


def bouncer_agent(state: dict) -> dict:
    """
    Classify customer based on customer_record from Greeter.
    Only called when is_identified=True, so customer_record exists.
    """
    customer_record = state.get("customer_record") or {}

    premium = customer_record.get("premium", False)

    return {
        "customer_type": "premium" if premium else "regular",
        "priority_level": "high" if premium else "normal",
    }
