from django.core.management.base import BaseCommand
from prediction.models import Symptom

class Command(BaseCommand):
    help = 'Populates the database with initial symptoms'
    
    def handle(self, *args, **options):
        symptoms = [
            'fever', 'cough', 'fatigue', 'difficulty_breathing', 'sore_throat',
            'headache', 'body_ache', 'rash', 'itching', 'abdominal_pain',
            'diarrhea', 'nausea', 'chest_pain', 'shortness_of_breath', 'dizziness',
            'frequent_urination', 'excessive_thirst', 'joint_pain', 'stiffness',
            'swelling', 'runny_nose', 'sensitivity_to_light', 'vomiting',
            'loss_of_appetite', 'weight_loss', 'night_sweats', 'blurred_vision',
            'numbness', 'tingling', 'muscle_weakness', 'confusion', 'memory_loss',
            'anxiety', 'depression', 'insomnia', 'excessive_sweating', 'dry_mouth',
            'constipation', 'blood_in_stool', 'painful_urination', 'irregular_heartbeat',
            'swollen_glands', 'ear_pain', 'hearing_loss', 'vision_changes', 'dry_eyes',
            'hair_loss', 'brittle_nails', 'muscle_cramps', 'tremors', 'seizures'
        ]
        
        for symptom_name in symptoms:
            Symptom.objects.get_or_create(
                name=symptom_name,
                defaults={
                    'description': f'Description of {symptom_name}'
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(symptoms)} symptoms'))