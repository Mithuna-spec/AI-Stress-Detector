def evaluate_breathing(breath_rate):

    if breath_rate == 0:
        return {
            "score": 0,
            "level": "No Data",
            "message": "Unable to detect breathing properly"
        }

    # Scoring Logic
    if breath_rate < 8:
        score = 30
        level = "Very Calm"
    elif 8 <= breath_rate <= 12:
        score = 40
        level = "Calm"
    elif 12 < breath_rate <= 18:
        score = 55
        level = "Normal"
    elif 18 < breath_rate <= 24:
        score = 75
        level = "Elevated"
    else:
        score = 90
        level = "High Stress"

    return {
        "score": score,
        "level": level,
        "message": f"Breathing rate: {breath_rate} breaths/min"
    }
