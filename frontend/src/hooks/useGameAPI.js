// ~/override/frontend/src/hooks/useGameAPI.js
import { useState } from 'react';

// --- MOCK INITIAL STATE (Based on python Game class) ---
const mockRegions = [
  { name: "Elystrion", total_nodes: 800, infected_nodes: 50, defense: 5, trait: "CORPORATE VAULT" },
  { name: "Sylthara Bloom", total_nodes: 3000, infected_nodes: 500, defense: 2, trait: "IOT SWARM" },
  { name: "Saxxten-36", total_nodes: 500, infected_nodes: 10, defense: 9, trait: "HUNTER KILLER" },
];

const initialGameState = {
  credits: 100,
  compute: 50,
  trace: 25.5,
  turn: 1,
  ddos_timer: 0,
  regions: mockRegions,
  history_log: [
    "Welcome, Operator. System initialized.",
    "Targeting sequence available.",
  ],
};

// --- CORE HOOK ---
export const useGameAPI = () => {
  const [gameState, setGameState] = useState(initialGameState);
  const [isLoading, setIsLoading] = useState(false);

  // This function simulates calling the /game/status GET endpoint
  const fetchStatus = async () => {
    setIsLoading(true);
    // In a real app, this would be: await fetch('/api/game/status')
    // We just return the current state after a small delay
    await new Promise(resolve => setTimeout(resolve, 300));
    setIsLoading(false);
    return gameState;
  };

  // This function simulates calling a POST action endpoint (e.g., /game/action/spread)
  const sendAction = async (actionType, regionIndex = null) => {
    setIsLoading(true);
    // 1. Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 2. Simulate Backend Logic and State Update
    // *** NOTE: This is a highly simplified mock of the Python logic! ***
    let newLogEntry = `Action: ${actionType}`;
    let newTrace = gameState.trace;
    let newCompute = gameState.compute;
    let newRegions = [...gameState.regions];

    if (actionType === 'spread' && regionIndex !== null) {
      newRegions[regionIndex].infected_nodes += Math.floor(Math.random() * 50) + 10;
      newCompute -= 15;
      newTrace += 3.0;
      newLogEntry = `SUCCESS: Infected nodes in ${newRegions[regionIndex].name}.`;
    } else if (actionType === 'ransomware' && regionIndex !== null) {
      const gain = newRegions[regionIndex].infected_nodes * 0.5;
      newCompute -= 30;
      newTrace += 8.0;
      newLogEntry = `RANSOMWARE: Gained ${Math.floor(gain)} Credits from ${newRegions[regionIndex].name}.`;
    } else if (actionType === 'purge') {
      newTrace = Math.max(0, newTrace - 25);
      newLogEntry = `LOGS PURGED: Trace reduced.`;
    }
    
    // 3. Simulate End-of-Turn Ticks
    const passiveCompute = Math.floor(Math.random() * 5) + 10;
    newCompute += passiveCompute;
    const endTurnTraceLeak = gameState.trace > 50 ? 2.5 : 0.5;
    newTrace += endTurnTraceLeak;

    const newLog = [...gameState.history_log, newLogEntry];
    if (newLog.length > 6) newLog.shift(); // Keep only 6 logs

    // 4. Update the State
    const nextState = {
      ...gameState,
      compute: newCompute,
      trace: newTrace,
      turn: gameState.turn + 1,
      regions: newRegions,
      history_log: newLog,
    };

    setGameState(nextState);
    setIsLoading(false);
    return nextState;
  };

  return { 
    gameState, 
    isLoading, 
    fetchStatus, 
    sendAction,
    setGameState // Useful for quick debugging or initial load
  };
};