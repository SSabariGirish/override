// frontend/src/components/RegionCard.jsx

import React, { useState } from 'react';
import './RegionCard.css'; 

// Helper to determine status color (based on original game logic)
const getStatusColor = (isSolidified, percent) => {
    if (isSolidified) return 'gold';
    if (percent > 0) return 'green';
    return 'fail';
};

const RegionCard = ({ region, index, onAction }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [actionType, setActionType] = useState(null); // 'infect', 'ransom', 'ddos', 'ransom_sub', 'ddos_sub'

    const { name, defense, infected_nodes, total_nodes, trait, infection_pct, is_solidified } = region;
    const regionIndex = index; // 0-based index for the API payload

    const percent = infection_pct;
    const statusColor = getStatusColor(is_solidified, percent);
    const progressBarWidth = `${Math.min(100, percent)}%`;

    // --- Core Submission Logic (Maps human names to backend keys) ---
    const handleInfectSubmit = (intensity, isProxy = false) => {
        let backendIntensity;
        
        // Map friendly intensity names to backend keys ('1', '2', '3', 'P')
        if (isProxy) {
            backendIntensity = 'P';
        } else if (intensity === 'low') {
            backendIntensity = '1';
        } else if (intensity === 'med') {
            backendIntensity = '2';
        } else if (intensity === 'high') {
            backendIntensity = '3';
        } else {
            return; // Invalid selection
        }

        onAction('infect', { 
            region_index: regionIndex, 
            intensity: backendIntensity, 
            proxy: isProxy 
        });
        setIsMenuOpen(false);
        setActionType(null);
    };

    // --- Action Selection Helpers (For Ransom/DDoS sub-menus, they will show prices/reqs) ---

    // Primary action selection (opens the sub-menu)
    const handleSelectAction = (type) => {
        setActionType(type);
        setIsMenuOpen(true);
    };
    
    // RANSOMWARE SUBMISSION (uses 1, 2, 3 as intensity)
    const handleRansomSubmit = (intensity) => {
        onAction('ransom', { region_index: regionIndex, intensity });
        setIsMenuOpen(false);
        setActionType(null);
    };
    
    // DDOS SUBMISSION (uses 1, 2, 3, 4 as intensity)
    const handleDDoSSubmit = (intensity) => {
        onAction('ddos', { region_index: regionIndex, intensity });
        setIsMenuOpen(false);
        setActionType(null);
    };


    // --- Render Logic ---
    
    // 1. Render Infect Intensity Sub-Menu
    if (isMenuOpen && actionType === 'infect') {
        return (
            <div className={`region-card ${name.replace(/\s/g, '-')}-bg infect-menu`}>
                <h3>TARGETING: {name} - WORM SPREAD</h3>
                {/* *** FIXED: CALLING handleInfectSubmit with string keys *** */}
                <button onClick={() => handleInfectSubmit('low')}>[1] Signal Injection (Low)</button>
                <button onClick={() => handleInfectSubmit('med')}>[2] Packet Flood (Med)</button>
                <button onClick={() => handleInfectSubmit('high')}>[3] Logic Bomb (High)</button>
                <button onClick={() => handleInfectSubmit('proxy', true)} disabled={is_solidified}>
                    [P] PROXY ATTACK (Stealth)
                </button>
                <button onClick={() => setIsMenuOpen(false)} className="back-button">BACK</button>
            </div>
        );
    }
    
    // 2. Render Ransomware Intensity Sub-Menu (NEW, based on terminal logic)
    if (isMenuOpen && actionType === 'ransom') {
        return (
            <div className={`region-card ${name.replace(/\s/g, '-')}-bg ransom-menu`}>
                <h3>TARGETING: {name} - RANSOMWARE</h3>
                <button onClick={() => handleRansomSubmit('1')}>[1] Data Siphon (Low CPU/Trace)</button>
                <button onClick={() => handleRansomSubmit('2')}>[2] Encryption Ware (Med CPU/Trace)</button>
                <button onClick={() => handleRansomSubmit('3')}>[3] Infrastructure Lock (High CPU/Trace)</button>
                <button onClick={() => setIsMenuOpen(false)} className="back-button">BACK</button>
            </div>
        );
    }
    
    // 3. Render DDoS Intensity Sub-Menu (NEW, based on terminal logic)
    if (isMenuOpen && actionType === 'ddos') {
        return (
            <div className={`region-card ${name.replace(/\s/g, '-')}-bg ddos-menu`}>
                <h3>TARGETING: {name} - BOTNET DDOS</h3>
                <button onClick={() => handleDDoSSubmit('1')}>[1] Simple DoS (5 CRD | 25% Mask)</button>
                <button onClick={() => handleDDoSSubmit('2')}>[2] Distributed DoS (20 CRD | 50% Mask)</button>
                <button onClick={() => handleDDoSSubmit('3')}>[3] Botnet Swarm (50 CRD | 75% Mask)</button>
                <button onClick={() => handleDDoSSubmit('4')}>[4] Global Blackout (150 CRD | 95% Mask)</button>
                <button onClick={() => setIsMenuOpen(false)} className="back-button">BACK</button>
            </div>
        );
    }

    // 4. Render the main card view
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
                    // When solidified, only show the Ransom button (as it's repeatable)
                    <button onClick={() => handleSelectAction('ransom')}>RANSOMWARE</button>
                ) : (
                    <>
                        <button onClick={() => handleSelectAction('infect')}>WORM SPREAD</button>
                        <button onClick={() => handleSelectAction('ransom')}>RANSOMWARE</button>
                        <button onClick={() => handleSelectAction('ddos')}>BOTNET DDOS</button>
                    </>
                )}
            </div>
        </div>
    );
};

export default RegionCard;