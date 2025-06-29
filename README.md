# 🧥 Disease Prediction System using Django & Machine Learning

## 📖 Project Overview

The **Disease Prediction System** is a web-based application developed using **Django (Python)** integrated with **Machine Learning algorithms**. This system predicts potential diseases based on user-provided symptoms, helping patients get early awareness and supporting doctors/admins in managing predictions. The prediction is powered by a trained Random Forest Classifier model.

---

## 🔬 Technologies Used

* **Backend**: Django (Python)
* **Machine Learning**:

  * Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)
  * LabelEncoder (`sklearn.preprocessing.LabelEncoder`)
* **Frontend**: Django Templates (HTML, CSS, Bootstrap)
* **Data Handling**:

  * CSV files for training data
  * Pickle (`.pkl`) files for model persistence
* **Database**: SQLite (Django's default database)

---

## 🧮 Data Mining & AI Algorithms

* **Algorithm**: Random Forest Classifier
* **Encoding**:

  * One-Hot Encoding for symptom features
  * Label Encoding for disease classification
* **Model Training**:

  * Dataset split using `train_test_split`
  * 200 estimators used in Random Forest
  * Class balancing using `class_weight='balanced'`
* **Model Storage**: Model and encoders are saved using Python's `pickle` module for quick deployment and reuse.

---

## ⚙️ System Workflow

1. **User Input**: Patient selects symptoms via a web interface.
2. **Feature Encoding**: Converts symptoms into a feature vector.
3. **Prediction**: Random Forest model predicts possible diseases.
4. **Doctor/Admin**: Doctors review, update, and verify predictions; Admin manages users, data, and system operations.

---

## 👥 User Roles

* **Patient**:

  * Register and Login
  * Submit symptoms for prediction
  * View disease prediction result

* **Doctor**:

  * Review patient records
  * Add feedback or diagnosis

* **Admin**:

  * Manage all users (Patients/Doctors)
  * Monitor prediction records
  * Manage system data

---

## 🖥️ System Features

* Role-based access control for patients, doctors, and admins.
* Real-time prediction with top 3 disease confidence scores.
* Secure user authentication.
* User-friendly interface using Django templating.
* Easy model retraining for additional diseases or updated datasets.
* Extendable for future improvements.

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository

git clone [https://github.com/mrsushilshrestha/Disease-Prediction-System-Django-Machine\_learning-AI.git](https://github.com/mrsushilshrestha/Disease-Prediction-System-Django-Machine_learning-AI.git)
cd Disease-Prediction-System-Django-Machine\_learning-AI

### 2️⃣ Create Virtual Environment

python -m venv venv

* For Windows:

venv\Scripts\activate

* For Linux/Mac:

source venv/bin/activate

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Apply Migrations

python manage.py makemigrations
python manage.py migrate

### 5️⃣ Run the Development Server

python manage.py runserver

### 6️⃣ Access the Application

Open your browser and visit:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Project Structure

Disease-Prediction-System-Django-Machine_learning-AI/
│
├── templates/              # HTML Templates (Django frontend)
├── static/                 # CSS, JS, and static files
├── models/                 # Saved ML models (pickle files)
├── training_data/          # Dataset files (CSV)
├── core/                   # Django core app
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
└── README.md               # Project documentation

---

## 🔐 Security & Privacy Considerations

* User data is securely stored in the Django database.
* Model files and sensitive information are protected from public access.
* Further security can be implemented for production deployment (GDPR/HIPAA compliance).

---

## 📈 Future Enhancements

* Expand dataset for additional diseases.
* Deploy Explainable AI (XAI) methods for better model transparency.
* Add telemedicine & chatbot support.
* Build REST API support for mobile integration.
* Deploy full-scale admin dashboards using Plotly.js or Dash.
* Cloud deployment (AWS, Azure, GCP).

---

## 🔢 Dataset Sample

| Fever | Cough | Fatigue | Vomiting | Headache | Disease        |
| ----- | ----- | ------- | -------- | -------- | -------------- |
| 1     | 1     | 0       | 1        | 0        | Typhoid        |
| 1     | 0     | 1       | 0        | 1        | Flu            |
| 0     | 1     | 1       | 1        | 0        | Food Poisoning |

---

## 📄 References

1. [Scikit-learn Random Forest Classifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) [Visited: 2025-06-10]
2. [Django Official Documentation](https://docs.djangoproject.com/en/stable/) [Visited: 2025-06-10]
3. [Plotly.js JavaScript Graphing Library](https://plotly.com/javascript/) [Visited: 2025-06-09]
4. [Python Pickle Module](https://docs.python.org/3/library/pickle.html) [Visited: 2025-06-10]
5. [LabelEncoder - Scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html) [Visited: 2025-06-10]
6. [UCI Machine Learning Repository](https://archive.ics.uci.edu/) [Visited: 2025-06-08]
7. [Real Python - Flask vs Django](https://realpython.com/flask-vs-django/) [Visited: 2025-06-07]
8. [Healthline Symptom Reference](https://www.healthline.com/symptom) [Visited: 2025-06-05]
9. [AI in Healthcare - Research Paper (Example)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6616181/) [Visited: 2025-06-06]


---

## 🙏 Acknowledgements

Special thanks to:

* The open-source community
* Publicly available datasets
* Machine learning & Django documentation resources

---

## 📧 Contact

**Sushil Shrestha**

📩 Email: [mrsushilshresthaofficial@gmail.com](mailto:mrsushilshresthaofficial@gmail.com)

