"""Token costs per action and plan feature maps."""

TOKEN_COSTS: dict[str, int] = {
    "chat_message": 1,
    "fortune_followup": 1,
    "profile_create": 3,
    "career_analysis": 8,
    "love_analysis": 8,
    "comprehensive_analysis": 10,
    "compatibility_analysis": 12,
}

PLAN_FEATURES: dict[str, dict[str, bool]] = {
    "free": {"career": False, "love": False, "compatibility": False},
    "basic": {"career": True, "love": False, "compatibility": False},
    "premium": {"career": True, "love": True, "compatibility": True},
}

PLAN_MONTHLY_TOKENS: dict[str, int] = {
    "free": 5,
    "basic": 60,
    "premium": -1,
}
