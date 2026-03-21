"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Swimming": {
        "description": "Train in freestyle, backstroke, breaststroke, and butterfly events",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Track and Field": {
        "description": "Sprint, jump, and throw in various athletic disciplines",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gymnastics": {
        "description": "Practice floor, vault, beam, and bar routines",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Fencing": {
        "description": "Learn foil, epee, and sabre techniques and compete in bouts",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Archery": {
        "description": "Develop precision and focus in target and recurve archery",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Rowing": {
        "description": "Train in singles, doubles, and team rowing on the water",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Judo": {
        "description": "Learn throws, holds, and competition techniques in judo",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Volleyball": {
        "description": "Practice serves, spikes, and team strategies for indoor volleyball",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Table Tennis": {
        "description": "Sharpen reflexes and spin techniques in singles and doubles play",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["harper@mergington.edu", "james@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
     # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

     # Validate activity is not full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")
    activity["participants"].remove(email)
    return {"message": f"Removed {email} from {activity_name}"}
