"""Greeter agent: extraction, merge, verification, response."""


from app.services.verification_service import verify_legitimacy
from app.tools.extraction import extract_identification, extract_intent
from app.tools.response_builder import (
    build_followup_response,
    build_identification_failure_response,
    build_identified_response,
    compute_missing_fields,
    has_minimum_identification_data,
    merge_collected_data,
)


def greeter_agent(state: dict) -> dict:
    """
    Greeter: extract intent + identification, merge with session, verify (2/3 rule).
    Returns state updates for one of: needs_more_info, identification_failed, is_identified.
    """
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])
    existing_data = state.get("collected_data") or {}

    # 1. Extract intent
    intent, intent_confidence = extract_intent(user_message, conversation_history)

    # 2. Extract identification from current message
    new_data = extract_identification(user_message, conversation_history)

    # 3. Merge with session
    collected_data = merge_collected_data(existing_data, new_data)

    # 4. Compute missing fields
    missing_fields = compute_missing_fields(collected_data)

    # 5. Check if we have enough to verify
    if not has_minimum_identification_data(collected_data):
        response = build_followup_response(collected_data, missing_fields)
        return {
            "intent": intent,
            "intent_confidence": intent_confidence,
            "collected_data": collected_data,
            "missing_fields": missing_fields,
            "needs_more_info": True,
            "is_identified": False,
            "identification_failed": False,
            "final_response": response,
        }

    # 6. Verify against customer base (2/3 rule)
    is_verified, customer_record = verify_legitimacy(collected_data)

    if is_verified and customer_record:
        response = build_identified_response(collected_data.get("name"))
        return {
            "intent": intent,
            "intent_confidence": intent_confidence,
            "collected_data": collected_data,
            "missing_fields": missing_fields,
            "needs_more_info": False,
            "is_identified": True,
            "identification_failed": False,
            "customer_record": customer_record,
            "final_response": response,
        }

    # Verification failed
    response = build_identification_failure_response()
    return {
        "intent": intent,
        "intent_confidence": intent_confidence,
        "collected_data": collected_data,
        "missing_fields": missing_fields,
        "needs_more_info": False,
        "is_identified": False,
        "identification_failed": True,
        "final_response": response,
    }
