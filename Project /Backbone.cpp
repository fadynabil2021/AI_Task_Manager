#include <iostream>
#include <fstream>
#include <cstring>
#include <nlohmann/json.hpp> 
using json = nlohmann::json;
using namespace std;

const Password =12345;
const char* TASKS_FILE = "/home/fady/SW/tasks.txt";  
struct Task {
    int id; 
    char name[100];
    int daysLeft;
    char taskType[50];
    int estimatedDuration;
    char deadlineTime[20];
    int taskImportance;
    int pastCompletionRate;
    int numberOfOverdueTasks;
    char predictedPriority[50];
};
Task tasks[100];  
int taskCount = 0; 

void saveAllTasks() {
    ofstream file(TASKS_FILE);
    
    if (!file) {
        cerr << "Error: Could not open file for writing!" << endl;
        return;
    }

    for (int i = 0; i < taskCount; i++) {
        json taskJson = {
            {"id", tasks[i].id},
            {"name", tasks[i].name},
            {"Days_Left", tasks[i].daysLeft},
            {"Task_Type", tasks[i].taskType},
            {"Estimated_Duration", tasks[i].estimatedDuration},
            {"Deadline_Time", tasks[i].deadlineTime},
            {"Task_Importance", tasks[i].taskImportance},
            {"Past_Completion_Rate", tasks[i].pastCompletionRate},
            {"Number_Of_Overdue_Tasks", tasks[i].numberOfOverdueTasks},
            {"Priority_Level", tasks[i].predictedPriority}
        };
        file << taskJson.dump() << "\n"; // JSON per line
    }
    
    file.close();
    cout << "Tasks saved successfully to " << TASKS_FILE << endl;
}

int getNumber(const char* prompt) {
    int num;
    while (true) {
        cout << prompt;
        if (cin >> num && num >= 0) {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return num;
        }
        cout << "Invalid input. Please enter a valid number.\n";
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }
}

void createTask() {
    if (taskCount >= 100) {
        cout << "Task limit reached.\n";
        return;
    }

    Task newTask;
    newTask.id = taskCount + 1;

    cout << "Enter Task Name: ";
    cin.ignore();
    cin.getline(newTask.name, 100);

    newTask.daysLeft = getNumber("Days until due: ");

    cout << "Task Type: ";
    cin.getline(newTask.taskType, 50);

    newTask.estimatedDuration = getNumber("Estimated duration (hours): ");

    cout << "Deadline (e.g., 03:10 AM): ";
    cin.getline(newTask.deadlineTime, 20);

    newTask.taskImportance = getNumber("Importance (1-5): ");
    newTask.pastCompletionRate = getNumber("Completion rate (0-100%): ");
    newTask.numberOfOverdueTasks = getNumber("Number of overdue tasks: ");

    strcpy(newTask.predictedPriority, "Not Predicted");

    tasks[taskCount++] = newTask;
    saveAllTasks();
    cout << "Task added successfully!\n";
}

void showTasks() {
    if (taskCount == 0) {
        cout << "No tasks available.\n";
        return;
    }

    for (int i = 0; i < taskCount; i++) {
        cout << "\nTask ID: " << tasks[i].id
             << "\nName: " << tasks[i].name
             << "\nDays Left: " << tasks[i].daysLeft
             << "\nType: " << tasks[i].taskType
             << "\nDuration: " << tasks[i].estimatedDuration << " hours"
             << "\nDeadline: " << tasks[i].deadlineTime
             << "\nImportance: " << tasks[i].taskImportance
             << "\nCompletion Rate: " << tasks[i].pastCompletionRate << "%"
             << "\nOverdue Tasks: " << tasks[i].numberOfOverdueTasks
             << "\nPriority: " << tasks[i].predictedPriority
             << "\n--------------------------";
    }
}

void removeTask() {
    int id = getNumber("Enter task ID to delete: ");

    int index = -1;
    for (int i = 0; i < taskCount; i++) {
        if (tasks[i].id == id) {
            index = i;
            break;
        }
    }

    if (index == -1) {
        cout << "Task not found.\n";
        return;
    }

    for (int i = index; i < taskCount - 1; i++) {
        tasks[i] = tasks[i + 1];
    }
    
    taskCount--;
    saveAllTasks();
    cout << "Task deleted.\n";
}

void predictTaskPriority() {
    saveAllTasks();
    cout << "Running priority prediction script...\n";

    if (system("python3 task_scheduler.py") != 0) {
        cout << "Prediction script execution failed.\n";
    } else {
        loadTasks();
        cout << "Priority levels updated.\n";
    }
}

int main() {
    int pass;
    cout<<"Enter the password: ";
    cin >> pass;
    if (pass == Password)
    {
    ifstream file(TASKS_FILE);
    if (!file) {
        cout << "No previous tasks found. Starting fresh.\n";
        return;
    }

    taskCount = 0; 
    string line;

    while (getline(file, line)) {
        if (line.empty()) continue; 

        try {
            json taskJson = json::parse(line);
            Task& task = tasks[taskCount];

            task.id = taskJson["id"];
            strncpy(task.name, taskJson["name"].get<string>().c_str(), sizeof(task.name));
            task.daysLeft = taskJson["Days_Left"];
            strncpy(task.taskType, taskJson["Task_Type"].get<string>().c_str(), sizeof(task.taskType));
            task.estimatedDuration = taskJson["Estimated_Duration"];
            strncpy(task.deadlineTime, taskJson["Deadline_Time"].get<string>().c_str(), sizeof(task.deadlineTime));
            task.taskImportance = taskJson["Task_Importance"];
            task.pastCompletionRate = taskJson["Past_Completion_Rate"];
            task.numberOfOverdueTasks = taskJson["Number_Of_Overdue_Tasks"];
            strncpy(task.predictedPriority, taskJson["Priority_Level"].get<string>().c_str(), sizeof(task.predictedPriority));

            taskCount++;

        } catch (const json::parse_error& e) {
            cerr << "Skipping invalid JSON line: " << line << endl;
        }
    }

    file.close();
    int choice;
    do {
        cout << "\nTask Manager Menu:\n"
             << "1. Add Task\n"
             << "2. Show Tasks\n"
             << "3. Delete Task\n"
             << "4. Predict Priorities\n"
             << "5. Exit\n"
             << "Choose an option: ";

        if (!(cin >> choice)) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            continue;
        }

        switch (choice) {
            case 1: createTask(); break;
            case 2: showTasks(); break;
            case 3: removeTask(); break;
            case 4: predictTaskPriority(); break;
            case 5: cout << "Exiting...\n"; break;
            default: cout << "Invalid option. Try again.\n"; break;
        }
    } while (choice != 5);
}
}

    return 0;
}
