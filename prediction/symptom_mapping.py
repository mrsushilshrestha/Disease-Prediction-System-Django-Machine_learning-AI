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
    "high fever": "high_fever",
    "cough": "cough",
    "headache": "headache",
    "nausea": "nausea",
    "vomiting": "vomiting",
    "diarrhea": "diarrhoea",
    "stomach pain": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "chest pain": "chest_pain",
    "difficulty breathing": "breathlessness",
    "shortness of breath": "breathlessness",
    "dizziness": "dizziness",
    "skin rash": "skin_rash",
    "itching": "itching",
    "sore throat": "patches_in_throat",
    "runny nose": "runny_nose",
    "congestion": "congestion",
    "back pain": "back_pain",
    "constipation": "constipation",
    "anxiety": "anxiety",
    "depression": "depression",
    "blurred vision": "blurred_and_distorted_vision",
    "sweating": "sweating",
    "chills": "chills",
    "shivering": "shivering",
    "loss of appetite": "loss_of_appetite",
    "yellowing of eyes": "yellowing_of_eyes",
    "yellowing of skin": "yellowish_skin",
    "dark urine": "dark_urine",
    
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
    
    # Try to find partial matches if exact match not found
    for key, value in symptom_mapping.items():
        if key in user_input or user_input in key:
            return value
    
    # If no match found, convert spaces to underscores to match training data format
    return user_input.replace(' ', '_')