import os
import requests
import pandas as pd
from django.core.management.base import BaseCommand
from prediction.models import Disease, Symptom

class Command(BaseCommand):
    help = 'Downloads and loads disease-symptom dataset from GitHub'
    
    def handle(self, *args, **options):
        # URLs for the datasets
        training_data_url = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/training_data.csv"
        test_data_url = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/test_data.csv"
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Download training data
        training_data_path = os.path.join(data_dir, 'training_data.csv')
        self.stdout.write(self.style.SUCCESS(f'Downloading training data to {training_data_path}'))
        response = requests.get(training_data_url)
        with open(training_data_path, 'wb') as f:
            f.write(response.content)
        
        # Download test data
        test_data_path = os.path.join(data_dir, 'test_data.csv')
        self.stdout.write(self.style.SUCCESS(f'Downloading test data to {test_data_path}'))
        response = requests.get(test_data_url)
        with open(test_data_path, 'wb') as f:
            f.write(response.content)
        
        # Load and process the data
        self.stdout.write(self.style.SUCCESS('Processing data and populating database...'))
        
        # Read the training data
        df = pd.read_csv(training_data_path)
        
        # Get all symptoms (column names except the last one which is 'prognosis')
        symptoms = list(df.columns)[:-1]
        
        # Get all unique diseases
        diseases = df['prognosis'].unique()
        
        # Add symptoms to database
        for symptom_name in symptoms:
            # Convert column names to readable format (replace '_' with space and capitalize)
            readable_name = symptom_name.replace('_', ' ').capitalize()
            Symptom.objects.get_or_create(
                name=symptom_name,
                defaults={
                    'description': f'Description of {readable_name}'
                }
            )
        
        # Add diseases to database
        for disease_name in diseases:
            # For each disease, find the symptoms that are most commonly associated with it
            disease_data = df[df['prognosis'] == disease_name]
            # Get symptoms that have value 1 (present) for this disease
            disease_symptoms = []
            for symptom in symptoms:
                if disease_data[symptom].values[0] == 1:
                    disease_symptoms.append(symptom)
            
            Disease.objects.get_or_create(
                name=disease_name,
                defaults={
                    'description': f'Information about {disease_name}',
                    'symptoms': ','.join(disease_symptoms),
                    'causes': f'Common causes of {disease_name}',
                    'home_remedies': f'Home remedies for {disease_name}',
                    'medications': f'Common medications for {disease_name}'
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(symptoms)} symptoms and {len(diseases)} diseases'))