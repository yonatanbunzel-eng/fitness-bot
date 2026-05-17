TOOLS = [
    {
        "name": "log_food",
        "description": "Log a meal or food item the user just ate or described.",
        "input_schema": {
            "type": "object",
            "required": ["meal_type", "food_items", "total_calories", "confidence", "reply_message"],
            "properties": {
                "meal_type": {
                    "type": "string",
                    "enum": ["breakfast", "lunch", "dinner", "snack"],
                    "description": "Time of day for this meal"
                },
                "food_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "calories"],
                        "properties": {
                            "name": {"type": "string"},
                            "grams": {"type": "number"},
                            "calories": {"type": "integer"},
                            "protein_g": {"type": "number"},
                            "carbs_g": {"type": "number"},
                            "fat_g": {"type": "number"},
                            "fiber_g": {"type": "number"}
                        }
                    }
                },
                "total_calories": {"type": "integer"},
                "total_protein_g": {"type": "number"},
                "total_carbs_g": {"type": "number"},
                "total_fat_g": {"type": "number"},
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Confidence level of the nutrition estimate"
                },
                "notes": {"type": "string"},
                "reply_message": {
                    "type": "string",
                    "description": "Short WhatsApp reply to send the user (max 6 lines)"
                },
                "suggest_alternative": {
                    "type": "boolean",
                    "description": "True if the meal is significantly off-plan and alternatives should be offered"
                },
                "alternative_suggestion": {
                    "type": "string",
                    "description": "Brief alternative meal suggestion if suggest_alternative is true"
                }
            }
        }
    },
    {
        "name": "log_workout",
        "description": "Log a completed workout session from voice, text, or Strava.",
        "input_schema": {
            "type": "object",
            "required": ["workout_type", "workout_date", "summary", "reply_message"],
            "properties": {
                "workout_type": {
                    "type": "string",
                    "enum": ["strength", "run", "flexibility", "other"]
                },
                "workout_date": {"type": "string", "description": "YYYY-MM-DD"},
                "exercises": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "sets": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "reps": {"type": "integer"},
                                        "kg": {"type": "number"},
                                        "duration_seconds": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                },
                "distance_km": {"type": "number"},
                "duration_minutes": {"type": "integer"},
                "pace_min_per_km": {"type": "number"},
                "summary": {"type": "string"},
                "plan_adherence": {
                    "type": "string",
                    "enum": ["on_plan", "off_plan", "rest_day", "no_plan"],
                    "description": "Whether this workout matches the weekly plan for today"
                },
                "adherence_note": {"type": "string"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "log_water",
        "description": "Log water intake.",
        "input_schema": {
            "type": "object",
            "required": ["amount_ml", "reply_message"],
            "properties": {
                "amount_ml": {"type": "integer", "description": "Amount in milliliters"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "log_weight",
        "description": "Log a body weight measurement.",
        "input_schema": {
            "type": "object",
            "required": ["weight_kg", "reply_message"],
            "properties": {
                "weight_kg": {"type": "number"},
                "notes": {"type": "string"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "log_sleep",
        "description": "Log sleep duration and quality.",
        "input_schema": {
            "type": "object",
            "required": ["duration_hours", "reply_message"],
            "properties": {
                "duration_hours": {"type": "number"},
                "quality_score": {"type": "integer", "description": "1-10 subjective quality"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "set_weekly_plan",
        "description": "Set or update the weekly training plan based on user input.",
        "input_schema": {
            "type": "object",
            "required": ["planned_sessions", "reply_message"],
            "properties": {
                "planned_sessions": {
                    "type": "object",
                    "description": "Map of day name to session info: {\"monday\": {\"type\": \"push\", \"notes\": \"...\"}, ...}",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "notes": {"type": "string"},
                            "rest": {"type": "boolean"}
                        }
                    }
                },
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "adapt_weekly_plan",
        "description": "Adapt the remaining weekly training plan due to schedule change or off-plan workout.",
        "input_schema": {
            "type": "object",
            "required": ["updated_sessions", "adaptation_reason", "reply_message"],
            "properties": {
                "updated_sessions": {
                    "type": "object",
                    "description": "Updated day→session map for the remaining days of the week"
                },
                "adaptation_reason": {"type": "string"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "send_summary",
        "description": "Generate and send a daily or weekly progress summary.",
        "input_schema": {
            "type": "object",
            "required": ["period", "reply_message"],
            "properties": {
                "period": {"type": "string", "enum": ["daily", "weekly"]},
                "reply_message": {
                    "type": "string",
                    "description": "The full summary message to send"
                }
            }
        }
    },
    {
        "name": "set_goals",
        "description": "Set or update the user's nutrition and training goals.",
        "input_schema": {
            "type": "object",
            "required": ["reply_message"],
            "properties": {
                "calories_target": {"type": "integer"},
                "protein_g": {"type": "number"},
                "carbs_g": {"type": "number"},
                "fat_g": {"type": "number"},
                "water_ml": {"type": "integer"},
                "sleep_hours": {"type": "number"},
                "supplements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "dose": {"type": "string"},
                            "timing": {"type": "string"}
                        }
                    }
                },
                "weekly_training_split": {"type": "object"},
                "weekly_run_km": {"type": "number"},
                "reply_message": {"type": "string"}
            }
        }
    },
    {
        "name": "chat_reply",
        "description": "Send a conversational reply when no data needs to be logged (e.g., answering a question, giving advice).",
        "input_schema": {
            "type": "object",
            "required": ["reply_message"],
            "properties": {
                "reply_message": {"type": "string"}
            }
        }
    }
]
