// frontend/src/App.jsx

import React, { useState, useEffect, useCallback } from 'react';
import StatusHeader from './components/StatusHeader';
import RegionList from './components/RegionList';
import LogWindow from './components/LogWindow';
import GameOverModal from './components/GameOverModal'; // NEW
import './App.css'; 

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
    // --- 1. HOOKS (MUST be at the top) ---
    const [gameState, setGameState] = useState(null);
    const [events, setEvents] = useState([]); 
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // --- Core API Fetching Function ---
    const fetchState = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/status`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setGameState(data);
            // Initialize events log with history from the state
            setEvents(data.history || []); 
        } catch (e) {
            console.error("Error fetching initial state:", e);
            setError("Failed to connect to the game server. Check the backend console.");
        } finally {
            setLoading(false);
        }
    }, []);

    // Load state on component mount (MUST be a top-level hook call)
    useEffect(() => {
        fetchState();
    }, [fetchState]);


    // --- Core Action Submission Function ---
    const handleAction = async (action, payload = {}) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${API_BASE_URL}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, payload }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // 1. Update the main game state
            setGameState(result.state);
            
            // 2. Update the events log. 
            // Note: If action is 'restart', result.state.history will be small.
            const newEvents = result.events || [];
            // We'll update the events list based on what the backend returned
            setEvents(newEvents); 
            
        } catch (e) {
            console.error("Action failed:", e);
            setError(`Action Error: ${e.message}`);
        } finally {
            setLoading(false);
        }
    };


    // --- 2. CONDITIONAL EARLY EXIT (Rendering Checks) ---

    if (error) {
        // Render error state if connection fails
        return <h1 style={{ color: 'red', textAlign: 'center', paddingTop: '50px' }}>Error: {error}</h1>;
    }

    if (!gameState) {
        // Render loading state if gameState is null (initial fetch)
        return <div className="loading-overlay">ESTABLISHING UPLINK...</div>;
    }
    
    // --- 3. DESTRUCTURING (SAFE TO CALL HERE) ---
    // This must come AFTER you confirm gameState is not null.
    const { regions, credits, compute, trace, ddos_timer, trace_multiplier } = gameState;

    
    // --- 4. MAIN RENDER ---
    return (
        <div className="override-app">
            <h1>Override Protocol v2.7</h1>
            
            <StatusHeader 
                credits={credits} 
                compute={compute} 
                trace={trace} 
                ddosTimer={ddos_timer} 
                traceMultiplier={trace_multiplier}
                onAction={handleAction}
                isLoading={loading}
                // Lock UI interaction if game is over
                isGameOver={!!gameState.terminal} 
            />

            <div className="main-layout">
                <RegionList 
                    regions={regions} 
                    onAction={handleAction} 
                    isGameOver={!!gameState.terminal}
                />
                
                <LogWindow events={events} />
            </div>
            
            <p className="footer">Turn: {gameState.turn}</p>

            {/* Render a processing overlay if loading */}
            {loading && <div className="loading-overlay">PROCESSING...</div>}
            
            {/* Game Over Modal Display */}
            {gameState.terminal && (
                <GameOverModal 
                    terminal={gameState.terminal} 
                    onRestart={() => handleAction('restart')} 
                />
            )}
        </div>
    );
}

export default App;