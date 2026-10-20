from decimal import Decimal, InvalidOperation

class BlueprintValidationError(Exception):
    """Custom exception for blueprint validation errors."""
    pass

def validate_against_tenant_blueprint(blueprint_rules: list[dict], raw_scores: dict) -> Decimal:
    """
    Validate incoming assessment scores against a tenant's dynamic JSON blueprint and calculates the weighted total score safely using Decimals.
    """
    total_score = Decimal("0.00")

    for rule in blueprint_rules:
        key = rule.get("key")
        label = rule.get("label", key)
        max_allowed = Decimal(str(rule.get("max_score", 0)))

        # Extract raw score safely, defaulting to 0 if missing
        raw_val = raw_scores.get(key, 0)

        try:
            score = Decimal(str(raw_val))
        except (InvalidOperation, TypeError):
            raise BlueprintValidationError(f"Invalid numeric format for score: '{raw_val}' in {label}")

        if score < Decimal("0.00") or score > max_allowed:
            raise BlueprintValidationError(
                f"Invalid score for {label}: received {score}, max allowed is {max_allowed}"
            )

        total_score += score

    return total_score
