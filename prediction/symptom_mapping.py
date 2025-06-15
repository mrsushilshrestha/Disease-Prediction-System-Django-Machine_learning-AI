# Mapping of common symptom descriptions to the exact symptom names in training data
symptom_mapping = {
    # General mappings
    "joint pain": "joint_pain",
    "pain in joints": "joint_pain",
    "painful joints": "joint_pain",
    "aching joints": "joint_pain",
    "stiff joints": "movement_stiffness",
    "joint stiffness": "movement_stiffness",
    "swollen joints": "swelling_joints",
    "joint swelling": "swelling_joints",
    "difficulty moving": "movement_stiffness",
    "limited mobility": "movement_stiffness",
    "neck stiffness": "stiff_neck",
    "knee pain": "knee_pain",
    "hip pain": "hip_joint_pain",
    "pain when walking": "painful_walking",
    "muscle weakness": "muscle_weakness",
    "tired": "fatigue",
    "exhaustion": "fatigue",
    "weight loss": "weight_loss",
    "fever": "mild_fever",
    "high temperature": "mild_fever",
    
    # Arthritis-specific mappings
    "morning stiffness": "movement_stiffness",
    "joint redness": "redness_of_eyes",  # closest match
    "warm joints": "swelling_joints",    # associated symptom
    "reduced range of motion": "movement_stiffness",
    "difficulty bending": "movement_stiffness",
    "joint warmth": "swelling_joints",   # associated symptom
    "joint tenderness": "joint_pain",
    "joint inflammation": "swelling_joints",
}

def map_user_symptom(user_input):
    """Convert user input to the exact symptom name used in the training data"""
    user_input = user_input.lower().strip()
    if user_input in symptom_mapping:
        return symptom_mapping[user_input]
    return user_input