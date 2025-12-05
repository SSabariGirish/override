📡 Override Protocol: Expansion v2.0

A strategic, text-driven cyber-warfare game reinvented for the web.

Override Protocol is a full-stack rebuild of the original CLI game:

FastAPI backend → deterministic game engine, state machine, persistence

React + Vite frontend → modern UI consuming REST endpoints

This v2.0 architecture cleanly decouples UI and engine logic, enabling future feature expansion (AI-driven enemies, WebSocket live events, etc.).

🚀 Getting Started
1. Project Structure
.
├── backend/
│   ├── api.py               # FastAPI application (exposes game engine)
│   ├── override2.py         # Core game engine
│   └── synthfall_trial.py   # Legacy/testing module
│
├── cyber_save.json          # Auto-generated game persistence file
│
└── frontend/
    ├── src/                 # React components & UI logic
    ├── package.json         # React/Vite dependencies
    └── ...                  # Additional frontend assets

⚙️ Backend Setup (FastAPI)

The backend exposes the game engine via REST on port 8000.

Install Dependencies
cd backend
pip install fastapi uvicorn python-json-logger pydantic

Run the API Server
uvicorn api:app --reload --port 8000


API will be available at:
http://localhost:8000

Backend automatically loads and updates cyber_save.json.

🖥️ Frontend Setup (React + Vite)

The frontend SPA communicates with the backend on port 8000 while running on port 5173 (default Vite dev port).

Install Dependencies
cd frontend
npm install

Run Dev Server
npm run dev


Frontend will typically start at:
http://localhost:5173

🔌 Core Architecture & API Endpoints

Game logic lives entirely in Python; React is purely a renderer and input layer.

Backend Endpoints
Method	Endpoint	Description
GET	/api/status	Returns current game snapshot (no turn advancement, no trace increases).
POST	/api/action	Executes a turn: infect, ransom, purge, wait. Returns updated state + event log.
POST	/api/restart	(Planned) Resets engine and clears state for a fresh run.
Game Engine Principles

State Container: A global GameEngine instance within api.py.

Persistence: State syncs into cyber_save.json after every action.

Trace Discipline: UI must use get_state_snapshot()—this prevents passive trace increases from non-actions.

🎨 UI/UX Phase 1.2 – Strategic Improvements

You have a clean CSS base. Now it’s time to level up the UX so players aren’t wrestling the interface like it’s a 90s sysadmin terminal.

1. Terminal State (Game Over Handling)

Current pain: When gameState.terminal === true, the UI just vibes silently.
Solution: Implement a Game Over Modal.

Modal behavior:

Freeze interaction

Display terminal.message (Trace 100% / Singularity achieved)

Add Restart Game → calls POST /api/restart

Dim background / animate failure glow

This creates an actual “finality moment,” not a silent soft-lock.

2. Region Card Interaction – Reduce Friction

The two-step Infect flow works but feels like telling an intern to fetch a USB stick from the basement.

Upgrade:
Introduce a unified Action Panel that appears when selecting a region.

Flow:

Click region → highlight

Action Panel slides in (side or bottom)

Shows all valid actions & costs:

Infect (with intensity slider/options)

Ransom

Purge

Wait (contextual)

This makes the game feel intentional, not procedural.

3. Visual Enhancements

Leverage your existing palette; just tighten the signal-to-noise.

Element	Enhancement
Log Window	Gold entries for DOMINATED & SOLIDIFIED should visually pop—increase saturation slightly.
Status Header	Wrap entire Trace Bar container in a neon border to reinforce “danger meter” psychology.
Region Cards	Add trait icons/emojis (🏦 Corporate Vault, ⚙️ IoT Swarm, 💊 Pharma Nexus, etc.) for instant contextual recognition.
🧠 Future-Proofing (Optional but Recommended)

Add WebSocket streaming for turn-by-turn event pushes

Implement seed-based deterministic mode for debugging

Package engine as a pip-installable module for automated testing

Add difficulty presets (Aggressive Trace, Slow Spread, Hardline Defence AI)

👥 Credits

Game designed and engineered by SGS and RBK.
Web implementation and architecture overhaul driven in collaboration with React/FastAPI refactoring efforts.