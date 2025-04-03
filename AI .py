import pandas as pd
import numpy as np
import joblib
import speech_recognition as sr
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
import json

# -------------------------------
# Functions for reading/writing tasks.txt in JSON Lines format
# -------------------------------
def load_tasks_from_txt(file_path="/home/fady/SW/tasks.txt"):
    tasks = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        tasks.append(json.loads(line))  # Parse JSON safely
                    except json.JSONDecodeError:
                        print(f"Skipping invalid line: {line}")  # Debugging
    except FileNotFoundError:
        print("Error: Task file not found.")
    return tasks

def save_tasks_to_txt(tasks, file_path="/home/fady/SW/tasks.txt"):
    """Save tasks back to the text file in JSON Lines Format, converting np.int64 to int."""
    with open(file_path, "w") as file:
        for task in tasks:
            # Convert any numpy.int64 values to native Python int
            for key, value in task.items():
                if isinstance(value, np.int64):
                    task[key] = int(value)
            file.write(json.dumps(task) + "\n")

# -------------------------------
# Function for predicting priority from an existing task (from file)
# -------------------------------
def predict_priority_for_task(task, model):
    """Predict priority level using the trained Random Forest model for a given task."""
    feature_columns = ["Days_Left", "Task_Type", "Estimated_Duration", "Deadline_Time",
                       "Task_Importance", "Past_Completion_Rate", "Number_Of_Overdue_Tasks"]
    
    # Build a DataFrame using the expected columns
    df = pd.DataFrame([{
        "Days_Left": task["Days_Left"],
        "Task_Type": task["Task_Type"],
        "Estimated_Duration": task["Estimated_Duration"],
        "Deadline_Time": task["Deadline_Time"],
        "Task_Importance": task["Task_Importance"],
        "Past_Completion_Rate": task["Past_Completion_Rate"],
        "Number_Of_Overdue_Tasks": task["Number_Of_Overdue_Tasks"]
    }])
    
    # Preprocess categorical variable: convert Task_Type to numeric code
    df["Task_Type"] = df["Task_Type"].astype("category").cat.codes
    
    # For Deadline_Time, extract the hour (assumes format "hh:mm AM/PM")
    df["Deadline_Time"] = df["Deadline_Time"].apply(lambda x: int(x.split(":")[0]))
    
    # Predict (numeric label)
    prediction = model.predict(df)
    
    # Load label encoders to convert numeric label to text
    label_encoders = joblib.load("label_encoders.pkl")
    predicted_priority = label_encoders["Priority_Level"].inverse_transform(prediction)[0]
    
    return predicted_priority


# -------------------------------
# Main function for processing file-based tasks
# -------------------------------
def main():
    # Load trained model
    model = joblib.load("priority_model.pkl")
    
    # Load tasks from tasks.txt
    tasks = load_tasks_from_txt()
    if not tasks:
        return
    
    # Request Task ID from the user
    try:
        task_id = int(input("Enter the Task ID to predict priority: ").strip())
    except ValueError:
        print("Invalid Task ID. Must be an integer.")
        return
    
    # Find task by ID
    task = next((t for t in tasks if t.get("id") == task_id), None)
    
    if not task:
        print("Error: Task ID not found!")
        return
    
    # Predict priority for the found task
    predicted_priority = predict_priority_for_task(task, model)
    print(f"Predicted Priority for Task ID {task_id}: {predicted_priority}")
    
    # Update the task with the predicted priority and save back to file
    task["Priority_Level"] = predicted_priority
    save_tasks_to_txt(tasks)
    print("Priority updated in tasks.txt!")

# -------------------------------
# Run file-based prediction and manual input prediction
# -------------------------------
if __name__ == "__main__":
    # First, process a task from file based on its ID
    main()
