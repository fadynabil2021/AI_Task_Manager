import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

data_file = "Dataset.csv"
df = pd.read_csv(data_file)
label_encoders = {}
categorical_columns = ["Task_Type"]
for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # Store encoder
le_priority = LabelEncoder()
df["Priority_Level"] = le_priority.fit_transform(df["Priority_Level"])
label_encoders["Priority_Level"] = le_priority  # Critical for predictions

def time_to_minutes(time_str):
    time_parts = time_str.split()
    hours, minutes = map(int, time_parts[0].split(":"))
    if "PM" in time_parts[1] and hours != 12:
        hours += 12
    if "AM" in time_parts[1] and hours == 12:
        hours = 0
    return hours * 60 + minutes
df["Deadline_Time"] = df["Deadline_Time"].apply(time_to_minutes)

X = df.drop(columns=["Priority_Level"])
y = df["Priority_Level"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

with open("priority_model.pkl", "wb") as f:
    pickle.dump(model, f) 

with open("label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)  

print("Model and encoders saved successfully!")
