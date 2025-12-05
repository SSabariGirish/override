// frontend/src/components/RegionCard.jsx

import React, { useState } from 'react';
import './RegionCard.css'; // Create this CSS file

// Helper to determine status color (based on original game logic)
const getStatusColor = (isSolidified, percent) => {
    if (isSolidified) return 'gold';
    if (percent > 0) return 'green';
    return 'fail';
};

const RegionCard = ({ region, index, onAction }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [actionType, setActionType] = useState(null); // 'infect', 'ransom', 'ddos'

    const { name, defense, infected_nodes, total_nodes, trait, infection_pct, is_solidified } = region;
    const regionIndex = index; // 0-based index for the API payload

    const percent = infection_pct;
    const statusColor = getStatusColor(is_solidified, percent);
    const progressBarWidth = `${Math.min(100, percent)}%`;
    // const canProxy = !is_solidified; // Assume a check is handled by the backend, but we need the button

    // --- Action Submission Helpers ---
    const handleSelectAction = (type) => {
        setActionType(type);
        setIsMenuOpen(true);
    };

    const handleInfect = (intensity, proxy = false) => {
        onAction('infect', { region_index: regionIndex, intensity, proxy });
        setIsMenuOpen(false);
        setActionType(null);
    };

    const handleRansom = () => {
        onAction('ransom', { region_index: regionIndex });
        setIsMenuOpen(false);
        setActionType(null);
    };

    const handleDDoS = () => {
        onAction('ddos', { region_index: regionIndex });
        setIsMenuOpen(false);
        setActionType(null);
    };

    // --- Render Logic ---
    if (isMenuOpen && actionType === 'infect') {
        // Render the Infect Intensity Sub-Menu
        return (
            <div className={`region-card ${name.replace(/\s/g, '-')}-bg infect-menu`}>
                <h3>TARGETING: {name}</h3>
                <button onClick={() => handleInfect('low')}>[1] Signal Injection (Low)</button>
                <button onClick={() => handleInfect('med')}>[2] Packet Flood (Med)</button>
                <button onClick={() => handleInfect('high')}>[3] Logic Bomb (High)</button>
                <button onClick={() => handleInfect('proxy', true)} disabled={is_solidified}>
                    [4] PROXY ATTACK (Stealth)
                </button>
                <button onClick={() => setIsMenuOpen(false)} className="back-button">BACK</button>
            </div>
        );
    }
    
    // Render the main card view
    return (
        <div className={`region-card ${name.replace(/\s/g, '-')}-bg`}>
            <div className="region-info">
                <span className="region-name">[{index + 1}] {name}</span>
                <span className={`status-text ${statusColor}`}>
                    {is_solidified ? "DOMINATED" : `${infected_nodes}/${total_nodes}`}
                </span>
            </div>

            <div className="progress-bar-wrap">
                <div 
                    className={`progress-bar ${statusColor}`} 
                    style={{ width: progressBarWidth }}
                ></div>
            </div>

            <div className="region-meta">
                <span>Def: {defense}</span> | <span className="trait-text">Trait: {trait}</span>
            </div>

            <div className="action-buttons">
                {is_solidified ? (
                    <button disabled className="solidified-button">SOLIDIFIED</button>
                ) : (
                    <>
                        <button onClick={() => handleSelectAction('infect')}>WORM SPREAD</button>
                        <button onClick={handleRansom}>RANSOMWARE</button>
                        <button onClick={handleDDoS}>BOTNET DDOS</button>
                    </>
                )}
            </div>
        </div>
    );
};

export default RegionCard;