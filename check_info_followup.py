def check_missing_fields(current_info, previous_info):
    missing_values = [
        "",
        "Unknown",
        "unknown",
        "null",
        None
    ]

    lookup_fields = ['emergency_type', 'location', 'people_involved', 'injuries', 'hazards', 'severity']

    missing_fields = []
    for field in previous_info:
        current_value = current_info.get(field, "Unknown")

        if current_value in missing_values:
            current_info[field] = previous_info.get(field, "Unknown")

        if(field in lookup_fields and current_info[field] in missing_values):
            missing_fields.append(field)

    return current_info, missing_fields

def ask_follow(missing_fields):

    follow_questions = {
        "emergency_type": "What type of emergency is it?",
        "location": "What is the exact location?",
        "people_involved": "How many people are involved?",
        "injuries": "How many people are injured?",
        "hazard": "What was the cause of the incidient?",
        "severity": "How serious is the situation?"
    }

    questions = []

    for field in missing_fields:
        questions.append(follow_questions[field])

    return questions