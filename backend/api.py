# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import os

# --- 1. CORE GAME LOGIC IMPORT ---
# This assumes you used the ABSOLUTE import fix:
from override2 import GameEngine, SAVE_FILE 

# --- 2. FASTAPI SETUP ---
app = FastAPI(title="Override Protocol API")

# Configure CORS to allow your React frontend (default is port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173"],  # Adjust as needed for your frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. GAME STATE MANAGEMENT ---
# Initialize the engine globally
game_engine = GameEngine()

# Try to load the game state on startup
if os.path.exists(SAVE_FILE):
    game_engine.load(SAVE_FILE)
    print(f"INFO: Loaded game state from {SAVE_FILE}.")
else:
    print(f"INFO: Starting new game. No save file found at {SAVE_FILE}.")

# --- 4. DATA SCHEMAS (Pydantic for validation) ---

# Schema for the action request body
class ActionRequest(BaseModel):
    action: str = Field(..., description="The game action to perform (e.g., 'infect', 'ransom', 'purge', 'wait').")
    # Payload can be any dict structure based on the action needed
    payload: dict = Field(default_factory=dict, description="Parameters required for the specific action.")

# --- 5. API ENDPOINTS ---

@app.get("/api/status")

def get_status():
    """Returns the complete current game state snapshot."""

    try:
        # Use the dedicated snapshot method to avoid triggering game events or advancing the turn
        return game_engine.get_state_snapshot()
    except Exception as e:
        print(f"ERROR getting status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve game state.")

@app.get("/")
def root():
    # This route will handle requests to http://127.0.0.1:8000/
    return {"message": "Override Protocol API is Operational"}

@app.post("/api/action")
def handle_action(request: ActionRequest):
    """Executes a game action and returns the new state and events."""
    
    action = request.action
    payload = request.payload
    
    print(f"INFO: Received action: {action} with payload: {payload}")

    try:
        # Call the core step function from the game engine
        result = game_engine.step(action, payload)
        
        # Save state after every action (excluding status_check and load)
        if action not in ["load", "status_check"]:
            game_engine.save(SAVE_FILE)
            
        return result

    except Exception as e:
        print(f"CRITICAL ERROR during action '{action}': {e}")
        # Raise an HTTP 500 error for the frontend
        raise HTTPException(status_code=500, detail=f"Game Logic Error: {e}")