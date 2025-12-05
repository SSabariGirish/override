// frontend/src/App.jsx

import React, { useState, useEffect, useCallback } from 'react';
import StatusHeader from './components/StatusHeader';
import RegionList from './components/RegionList';
import LogWindow from './components/LogWindow';
import './App.css'; // Assume you'll create a simple CSS file

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
    // Game state: will hold the structure returned by /api/status
    const [gameState, setGameState] = useState(null);
    // Events log: stores messages returned by /api/action
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
            setError("Failed");
        } finally {
            setLoading(false);
        }
    }, []);

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
                // Read error message from backend
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // 1. Update the main game state
            setGameState(result.state);
            
            // 2. Update the events log, keeping only the max allowed history length 
            //    (the backend returns all events for the latest turn)
            const newEvents = result.events || [];
            setEvents(prev => [...prev.slice(newEvents.length), ...newEvents]); // Simple log rotation
            
            if (result.state.terminal) {
                alert(`Game Over! ${result.state.terminal.message}`);
            }

        } catch (e) {
            console.error("Action failed:", e);
            setError(`Action Error: ${e.message}`);
        } finally {
            setLoading(false);
        }
    };

    // Load state on component mount
    useEffect(() => {
        fetchState();
    }, [fetchState]);


    if (loading && !gameState) {
        return <h1>Establishing Uplink...</h1>;
    }

    if (error) {
        return <h1 style={{ color: 'red' }}>Error: {error}</h1>;
    }

    if (!gameState) {
        return <h1>Waiting for Game State...</h1>;
    }
    
    // Deconstruct necessary data for props
    const { regions, credits, compute, trace, ddos_timer, trace_multiplier } = gameState;

    return (
        <div className="override-app">
            <h1>Override Protocol v2.0</h1>
            
            <StatusHeader 
                credits={credits} 
                compute={compute} 
                trace={trace} 
                ddosTimer={ddos_timer} 
                traceMultiplier={trace_multiplier}
                onAction={handleAction}
                isLoading={loading}
            />

            <div className="main-layout">
                <RegionList 
                    regions={regions} 
                    onAction={handleAction} 
                />
                
                <LogWindow events={events} />
            </div>
            
            <p className="footer">Turn: {gameState.turn}</p>

            {loading && <div className="loading-overlay">PROCESSING...</div>}
        </div>
    );
}

export default App;