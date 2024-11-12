#Fitts Law by Deja, Amal, Aleks 
import tkinter as tk
import random #this will randomize the tasks for each participant
import math
import time
import sqlite3


# Circle diameters and distances
DIAMETERS = [20, 40, 80]  # Use values from your tasks table
DISTANCES = [100, 300]  # Use values from your tasks table
DIRECTIONS = ["left", "right"]  # Use values from your tasks table

# Initialize variables
click_data = []  # To store distance, time, and error data for each trial
start_time = None  # Start time for each target appearance
errors = 0  # Count of errors (misses)

# Database connection
conn = sqlite3.connect("fitts_law_experiment.db")
cursor = conn.cursor()

#main window
root = tk.Tk()
root.geometry("1200x1200") #sets the window size to a fixed size
root.title("Fitts Law Experiment")

def insert_block():
    started_at = time.time()
    cursor.execute('''INSERT INTO blocks (participant_id, started_at, finished_at)
                      VALUES (?, ?, ?)''', 
                   (1, started_at, None))  # Use a dummy participant_id (or set it manually)
    conn.commit()
    return cursor.lastrowid  # Return block ID

# Function to insert a task
def insert_task(diameter, distance, direction):
    cursor.execute('''INSERT INTO tasks (diameter, distance, direction)
                      VALUES (?, ?, ?)''', 
                   (diameter, distance, direction))
    conn.commit()
    return cursor.lastrowid  # Return task ID

# Function to insert a trial
def insert_trial(block_id, task_id, distance_travelled, errors):
    started_at = time.time()
    cursor.execute('''INSERT INTO trials (block_id, task_id, started_at, finished_at, distance_travelled, errors)
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                   (block_id, task_id, started_at, None, distance_travelled, errors))
    conn.commit()

# Thank you message function (Moved above)
def thank_you_message():
    welcome_frame.destroy()  # Gets rid of the welcome screen
    thank_you_label = tk.Label(root, text="Thank you for your time!", font=("Arial", 40))
    thank_you_label.pack(expand=True)
    thank_you_label.pack(padx=10, pady=10)

#begin experiment function
def experiment_begins():
    global block_id
    welcome_frame.destroy() #gets rid of the welcome screen 
    block_id = insert_block()
    experiment_label = tk.Label(root, text = "The experiment will begin now!", font = ("Arial", 40))
    experiment_label.pack(padx = 10, pady = 10)
    root.after(2000, experiment_label.destroy)  # Wait 2 seconds before starting
    next_trial()  # Start first trial

def next_trial():
    global start_time
    start_time = time.time()  # Record start time for each trial

 # Clear previous target
    for widget in root.winfo_children():
        if widget != welcome_frame:
            widget.destroy()

 # Randomize task parameters
    diameter = random.choice(DIAMETERS)
    distance = random.choice(DISTANCES)
    direction = random.choice(DIRECTIONS)
    
    # Insert task into database
    task_id = insert_task(diameter, distance, direction)
    
    # Position target
    x_position = 600 - distance if direction == "left" else 600 + distance
    y_position = 400  # Fixed vertical center

    # Create target button
    target = tk.Button(root, text="Target", bg="red", command=lambda: record_click(task_id, distance))
    target.place(x=x_position, y=y_position, width=diameter, height=diameter)

# Function to record the click
def record_click(task_id, distance):
    end_time = time.time()  # End time after click
    
    # Calculate time taken for trial
    time_taken = end_time - start_time
    distance_travelled = distance  # Modify if you want to calculate based on actual travel
    insert_trial(block_id, task_id, distance_travelled, errors)

    # Reset errors for next trial
    errors = 0
    
    # Proceed to the next trial or end experiment
    if len(click_data) < 10:  # Set the number of trials
        next_trial()
    else:
        end_experiment()

# Handle missed clicks to count errors
def missed_click(event):
    global errors
    errors += 1  # Increment error count if clicked outside target

# End experiment and show results
def end_experiment():
    for widget in root.winfo_children():
        widget.destroy()

    # Display summary of results
    results_label = tk.Label(root, text="Experiment Complete!", font=("Arial", 30))
    results_label.pack(pady=20)

    cursor.execute("SELECT * FROM trials")
    for row in cursor.fetchall():
        result_text = f"Task ID: {row[1]}, Time: {row[3]:.2f} s, Errors: {row[5]}"
        result_label = tk.Label(root, text=result_text, font=("Arial", 16))
        result_label.pack()


#welcome screen
welcome_frame = tk.Frame(root)
welcome_frame.pack(expand = True)

#welcome statement
welcome_label = tk.Label(welcome_frame, text = "Welcome to our Fitts Law Experiment!", font = ("Arial",50))
#adds padding around the welcome statement
welcome_label.pack(padx = 10, pady = 10 )
welcome_label.pack()

#instructions
instructions_text = ( "fjfjfjfjf.")
instructions_label = tk.Label(welcome_frame, text = instructions_text, font = ("Arial, 16"))
instructions_label.pack(padx = 15, pady = 15)

#informed consent add how long it takes to complete
consent_text = ("This experiment will study the ability to point and click on targets.\n"
                "Your participation is voluntary, and you may withdraw at any time.\n"
                "Your test results will be recorded anonymously and will remain confidential.\n"
                "By clicking 'I Agree', you consent to participate in this experiment.")


consent_label = tk.Label(welcome_frame, text = consent_text, font = ("Arial, 16"))
consent_label.pack(padx = 15, pady = 15)
welcome_frame.pack(expand = True)

#agree button
agree_button = tk.Button(welcome_frame, text = "I Agree", font = ("Arial, 18"), command = experiment_begins)
agree_button.pack(padx = 25, pady = 25)

#disagree button
disagree_button = tk.Button(welcome_frame, text = "I do not agree", font = ("Arial, 18"), command = thank_you_message)
disagree_button.pack(padx = 25, pady = 25)

#main loop
root.mainloop()


conn.close()