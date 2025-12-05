// frontend/src/components/GameOverModal.jsx

import React from 'react';
import './GameOverModal.css';

const GameOverModal = ({ terminal, onRestart }) => {
    
    const isSuccess = terminal.outcome === 'singularity';
    const title = isSuccess ? "GLOBAL SINGULARITY ACHIEVED" : "CRITICAL FAILURE DETECTED";
    const colorClass = isSuccess ? 'success-text' : 'failure-text';
    
    const handleRestartClick = () => {
        // Call the parent function to execute the 'restart' action via API
        onRestart(); 
    };

    return (
        <div className="game-over-modal-overlay">
            <div className="game-over-modal-content">
                <h2 className={colorClass}>{title}</h2>
                <p className="message-text">{terminal.message}</p>
                
                <p className="instruction">
                    The current operational cycle is terminated. Initiate a new session?
                </p>
                
                <button 
                    className="restart-button"
                    onClick={handleRestartClick}
                >
                    INITIATE SYSTEM RESET (RESTART)
                </button>
            </div>
        </div>
    );
};

export default GameOverModal;