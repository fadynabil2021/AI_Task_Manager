import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load the dataset
data_file = "synthetic_task_data_balanced.csv"
df = pd.read_csv(data_file)

# --- Preprocessing Updates ---
label_encoders = {}

# 1. Encode categorical features
categorical_columns = ["Task_Type"]
for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # Store encoder

# 2. Encode target variable ("Priority_Level") using LabelEncoder
le_priority = LabelEncoder()
df["Priority_Level"] = le_priority.fit_transform(df["Priority_Level"])
label_encoders["Priority_Level"] = le_priority  # Critical for predictions

# Convert time into minutes
def time_to_minutes(time_str):
    time_parts = time_str.split()
    hours, minutes = map(int, time_parts[0].split(":"))
    if "PM" in time_parts[1] and hours != 12:
        hours += 12
    if "AM" in time_parts[1] and hours == 12:
        hours = 0
    return hours * 60 + minutes

df["Deadline_Time"] = df["Deadline_Time"].apply(time_to_minutes)

# Define features and target
X = df.drop(columns=["Priority_Level"])
y = df["Priority_Level"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# --- Save Files Correctly ---
# Save model separately
with open("priority_model.pkl", "wb") as f:
    pickle.dump(model, f)  # Only the model

# Save label encoders separately
with open("label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)  # Both Task_Type and Priority_Level encoders

print("Model and encoders saved successfully!")