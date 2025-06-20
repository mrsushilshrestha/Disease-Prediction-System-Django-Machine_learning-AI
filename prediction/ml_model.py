import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle
from sklearn.model_selection import cross_val_score

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
        # Load data from CSV
        try:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'training_data.csv')
            print(f"Attempting to load training data from: {data_path}")
            
            if not os.path.exists(data_path):
                print(f"Error: Training data file not found at {data_path}")
                self._train_with_hardcoded_data()
                return
                
            df = pd.read_csv(data_path)
            print(f"Successfully loaded training data with {len(df)} rows")
            
            # Check if the CSV has the expected format
            if 'prognosis' not in df.columns:
                print("Error: CSV file does not have 'prognosis' column")
                self._train_with_hardcoded_data()
                return
                
            # Remove duplicate entries to balance the dataset
            df = df.drop_duplicates()
            
            # Count occurrences of each disease
            disease_counts = df['prognosis'].value_counts()
            print(f"Found {len(disease_counts)} unique diseases in the dataset")
            
            # Limit the number of samples per disease to balance the dataset
            max_samples_per_disease = 50  # Increased from 10 to 50
            balanced_df = pd.DataFrame()
            
            for disease in disease_counts.index:
                disease_df = df[df['prognosis'] == disease]
                if len(disease_df) > max_samples_per_disease:
                    disease_df = disease_df.sample(max_samples_per_disease, random_state=42)
                balanced_df = pd.concat([balanced_df, disease_df])
            
            df = balanced_df
            print(f"Balanced dataset contains {len(df)} rows")
            
        except Exception as e:
            print(f"Error loading or processing training data: {e}")
            # Fall back to hardcoded data
            self._train_with_hardcoded_data()
            return
            
        # Get all symptoms (column names except the last one which is 'prognosis')
        self.symptoms_list = list(df.columns)[:-1]
        
        # Features (X) are all columns except 'prognosis'
        X = df[self.symptoms_list]
        
        # Target (y) is the 'prognosis' column
        y = df['prognosis']
        
        # Calculate feature importance to identify most relevant symptoms
        temp_model = RandomForestClassifier(n_estimators=100, random_state=42)
        temp_model.fit(X, y)
        
        # Get feature importances
        importances = temp_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Keep only the top 60 most important symptoms (increased from 40)
        top_symptoms_count = 60
        top_indices = indices[:top_symptoms_count]
        self.top_symptoms = [self.symptoms_list[i] for i in top_indices]
        
        # Print top symptoms for reference
        print("Top {} most important symptoms:".format(top_symptoms_count))
        for i, symptom in enumerate(self.top_symptoms):
            print(f"{i+1}. {symptom} (Importance: {importances[indices[i]]:.4f})")
        
        # Encode diseases
        self.disease_encoder = LabelEncoder()
        y_encoded = self.disease_encoder.fit_transform(y)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # Train the model with optimized hyperparameters
        self.model = RandomForestClassifier(
            n_estimators=500,  # Increased from 300
            max_depth=None,    # Allow trees to grow fully
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            bootstrap=True,
            random_state=42,
            class_weight='balanced',  # Handle class imbalance
            criterion='entropy'  # Use entropy instead of gini for better performance
        )
        self.model.fit(X_train, y_train)
        
        # After training the model
        feature_importances = self.model.feature_importances_

        # Create a threshold for feature importance - lowered to include more features
        importance_threshold = 0.002  # Reduced from 0.005

        # Create a mask for important features
        important_features_mask = feature_importances > importance_threshold

        # Filter X to only include important features
        X_important = X_train[:, important_features_mask]

        # Retrain the model with only important features
        self.model.fit(X_important, y_train)

        # Store the mask for prediction
        self.important_features_mask = important_features_mask

        # Perform cross-validation
        cv_scores = cross_val_score(self.model, X, y_encoded, cv=5)
        print(f"Cross-validation accuracy: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        # Evaluate model performance
        accuracy = self.model.score(X_test[:, important_features_mask], y_test)
        print(f"Model accuracy: {accuracy:.4f}")
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'symptom_encoder': self.symptom_encoder,
                'disease_encoder': self.disease_encoder,
                'symptoms_list': self.symptoms_list,
                'top_symptoms': self.top_symptoms,
                'important_features_mask': self.important_features_mask
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
        
        # Add these lines to create the missing attributes
        self.top_symptoms = self.symptoms_list  # Use all symptoms as top symptoms
        
        # Create a dummy mask that includes all features
        self.important_features_mask = np.ones(len(self.symptoms_list), dtype=bool)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'symptom_encoder': self.symptom_encoder,
                'disease_encoder': self.disease_encoder,
                'symptoms_list': self.symptoms_list,
                'top_symptoms': self.top_symptoms,  # Add this
                'important_features_mask': self.important_features_mask  # Add this
            }, f)
    
    def predict(self, symptoms):
        # Create feature vector
        X = np.zeros((1, len(self.symptoms_list)))
        symptom_indices = []  # Track which symptoms were found
        for symptom in symptoms:
            if symptom in self.symptoms_list:
                j = self.symptoms_list.index(symptom)
                X[0, j] = 1
                symptom_indices.append(j)
        
        # Apply feature importance mask if available
        if hasattr(self, 'important_features_mask'):
            X = X[:, self.important_features_mask]
        
        # Predict disease with probability calibration
        probabilities = self.model.predict_proba(X)[0]
        
        # Modified softmax function with temperature parameter
        def softmax_with_temp(x, temp=0.5):  # Lower temperature for sharper differences
            e_x = np.exp(x / temp - np.max(x / temp))
            return e_x / e_x.sum()
        
        # Apply modified softmax to get more differentiated probabilities
        calibrated_probs = softmax_with_temp(probabilities)
        
        # Check if any of the input symptoms are associated with each disease
        symptom_disease_relevance = np.zeros(len(self.disease_encoder.classes_))
        
        # For each tree in the forest
        for tree in self.model.estimators_:
            # Get the paths in the tree
            n_nodes = tree.tree_.node_count
            feature = tree.tree_.feature
            for i in range(n_nodes):
                # If this node splits on one of our symptoms
                if feature[i] >= 0 and feature[i] in symptom_indices:
                    # Find which class this path leads to
                    if tree.tree_.children_left[i] == -1:  # Leaf node
                        class_idx = np.argmax(tree.tree_.value[i][0])
                        symptom_disease_relevance[class_idx] += 1
        
        # Normalize the relevance scores
        if np.sum(symptom_disease_relevance) > 0:
            symptom_disease_relevance = symptom_disease_relevance / np.sum(symptom_disease_relevance)
            
            # Apply a stronger penalty to diseases that don't match any of the input symptoms
            relevance_threshold = 0.01
            for i in range(len(calibrated_probs)):
                if symptom_disease_relevance[i] < relevance_threshold:
                    calibrated_probs[i] *= 0.3  # Increased penalty from 0.5 to 0.3 (70% reduction)
        
        # Ensure diversity in predictions with stronger factor
        diversity_factor = 0.4  # Increased from 0.2
        
        # Get initial top prediction
        top_disease_idx = np.argmax(probabilities)
        top_disease = self.disease_encoder.inverse_transform([top_disease_idx])[0]
        
        # Apply diversity penalty to similar diseases
        for i, disease_idx in enumerate(range(len(probabilities))):
            if disease_idx != top_disease_idx:
                disease = self.disease_encoder.inverse_transform([disease_idx])[0]
                # If disease name contains part of top disease name or vice versa, apply penalty
                if top_disease.lower() in disease.lower() or disease.lower() in top_disease.lower():
                    calibrated_probs[disease_idx] *= (1 - diversity_factor)
        
        # Get top 3 predictions with their confidence scores
        top_indices = np.argsort(calibrated_probs)[::-1][:3]
        top_diseases = [self.disease_encoder.inverse_transform([idx])[0] for idx in top_indices]
        top_confidences = [calibrated_probs[idx] for idx in top_indices]
        
        # Get most relevant symptoms for the predicted disease
        if hasattr(self, 'top_symptoms'):
            # Get the predicted disease index
            disease_idx = top_indices[0]
            
            # Get feature importances for this specific prediction
            # This uses the per-tree feature contributions for this specific prediction
            importances = []
            for tree in self.model.estimators_:
                if hasattr(tree, 'tree_'):
                    # Get the decision path for this sample
                    decision_path = tree.decision_path(X)
                    # Get the feature used at each node in the decision path
                    node_indices = decision_path.indices
                    for node_idx in node_indices:
                        if node_idx < len(tree.tree_.feature) and tree.tree_.feature[node_idx] >= 0:
                            feature_idx = tree.tree_.feature[node_idx]
                            importances.append(feature_idx)
            
            # Count occurrences of each feature
            feature_counts = {}
            for idx in importances:
                if idx not in feature_counts:
                    feature_counts[idx] = 0
                feature_counts[idx] += 1
            
            # Get the most important features for this prediction
            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            relevant_symptoms = []
            for feature_idx, count in sorted_features[:5]:  # Top 5 most relevant symptoms
                if feature_idx < len(self.symptoms_list):
                    relevant_symptoms.append(self.symptoms_list[feature_idx])
            
            # Return all top predictions, confidences, and relevant symptoms
            return top_diseases, [float(conf) for conf in top_confidences], relevant_symptoms
        
        # Return all top predictions and confidences (backward compatibility)
        return top_diseases, [float(conf) for conf in top_confidences]