import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.symptom_encoder = None
        self.disease_encoder = None
        self.symptoms_list = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'disease_model.pkl')
        self.load_or_train_model()
    
    def load_or_train_model(self):
        # Check if model exists
        if os.path.exists(self.model_path):
            # Load the model
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.symptom_encoder = model_data['symptom_encoder']
                self.disease_encoder = model_data['disease_encoder']
                self.symptoms_list = model_data['symptoms_list']
        else:
            # Train the model
            self.train_model()
    
    def train_model(self):
        # Path to the CSV data
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        training_data_path = os.path.join(data_dir, 'training_data.csv')
        
        # Check if the CSV file exists
        if not os.path.exists(training_data_path):
            # If not, use the hardcoded dataset as fallback
            print("CSV data not found. Using hardcoded dataset.")
            self._train_with_hardcoded_data()
            return
        
        # Load the CSV data
        df = pd.read_csv(training_data_path)
        
        # Get all symptoms (column names except the last one which is 'prognosis')
        self.symptoms_list = list(df.columns)[:-1]
        
        # Features (X) are all columns except 'prognosis'
        X = df[self.symptoms_list]
        
        # Target (y) is the 'prognosis' column
        y = df['prognosis']
        
        # Encode diseases
        self.disease_encoder = LabelEncoder()
        y_encoded = self.disease_encoder.fit_transform(y)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # Train the model with optimized hyperparameters
        self.model = RandomForestClassifier(
            n_estimators=200,  # Increased from 100
            max_depth=None,    # Allow trees to grow fully
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            bootstrap=True,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate model performance
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.4f}")
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'symptom_encoder': self.symptom_encoder,
                'disease_encoder': self.disease_encoder,
                'symptoms_list': self.symptoms_list
            }, f)
    
    def _train_with_hardcoded_data(self):
        # This is the original hardcoded dataset as fallback
        data = {
            'symptoms': [
                'fever,cough,fatigue,difficulty_breathing',
                'fever,cough,sore_throat',
                'headache,fever,body_ache',
                'rash,itching,fever',
                'abdominal_pain,diarrhea,nausea',
                'chest_pain,shortness_of_breath,dizziness',
                'frequent_urination,excessive_thirst,fatigue',
                'joint_pain,stiffness,swelling',
                'sore_throat,runny_nose,cough',
                'headache,sensitivity_to_light,nausea'
            ],
            'disease': [
                'COVID-19',
                'Common Cold',
                'Influenza',
                'Chickenpox',
                'Gastroenteritis',
                'Heart Attack',
                'Diabetes',
                'Arthritis',
                'Common Cold',
                'Migraine'
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Extract all unique symptoms
        all_symptoms = set()
        for symptom_list in df['symptoms']:
            all_symptoms.update(symptom_list.split(','))
        
        self.symptoms_list = sorted(list(all_symptoms))
        
        # Create feature matrix
        X = np.zeros((len(df), len(self.symptoms_list)))
        for i, symptom_list in enumerate(df['symptoms']):
            for symptom in symptom_list.split(','):
                j = self.symptoms_list.index(symptom)
                X[i, j] = 1
        
        # Encode diseases
        self.disease_encoder = LabelEncoder()
        y = self.disease_encoder.fit_transform(df['disease'])
        
        # Train the model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'symptom_encoder': self.symptom_encoder,
                'disease_encoder': self.disease_encoder,
                'symptoms_list': self.symptoms_list
            }, f)
    
    def predict(self, symptoms):
        # Create feature vector
        if isinstance(self.symptoms_list[0], str):
            # For CSV-based model
            X = np.zeros((1, len(self.symptoms_list)))
            for symptom in symptoms:
                if symptom in self.symptoms_list:
                    j = self.symptoms_list.index(symptom)
                    X[0, j] = 1
        else:
            # For hardcoded model (fallback)
            X = np.zeros((1, len(self.symptoms_list)))
            for symptom in symptoms:
                if symptom in self.symptoms_list:
                    j = self.symptoms_list.index(symptom)
                    X[0, j] = 1
        
        # Predict disease
        y_pred = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[0]
        
        # Get top 3 predictions with their confidence scores
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_diseases = [self.disease_encoder.inverse_transform([idx])[0] for idx in top_indices]
        top_confidences = [probabilities[idx] for idx in top_indices]
        
        # Return primary prediction and confidence
        disease_name = top_diseases[0]
        confidence = top_confidences[0]
        
        return disease_name, float(confidence)