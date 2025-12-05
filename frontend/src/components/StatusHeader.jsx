// frontend/src/components/StatusHeader.jsx

import React from 'react';
import './StatusHeader.css'; // Create this CSS file

const StatusHeader = ({ credits, compute, trace, ddosTimer, traceMultiplier, onAction, isLoading }) => {
    
    // Determine trace bar style and color based on trace percentage
    const traceWidth = `${trace}%`;
    let traceColorClass = 'trace-green';
    if (trace > 40) traceColorClass = 'trace-warning';
    if (trace > 80) traceColorClass = 'trace-fail';

    // Determine multiplier color
    let multipleColorClass = 'multiple-green';
    if (traceMultiplier > 3.0) multipleColorClass = 'multiple-warning';
    if (traceMultiplier > 8.0) multipleColorClass = 'multiple-fail';
    
    return (
        <div className="status-header">
            <div className="resource-bar">
                <span className="resource">CAPACITY: <span className="cpu">{compute} CPU</span></span>
                <span className="resource">FUNDS: <span className="credits">{credits} CRD</span></span>
                <span className={`resource ${multipleColorClass}`}>SIGNATURE: {traceMultiplier.toFixed(2)}x</span>
            </div>
            
            <div className="global-trace">
                <span>GLOBAL TRACE:</span>
                <div className="trace-bar-container">
                    <div className={`trace-bar ${traceColorClass}`} style={{ width: traceWidth }}></div>
                </div>
                <span className="trace-percent">{trace.toFixed(1)}%</span>
            </div>
            
            <div className="status-indicators">
                {ddosTimer > 0 && (
                    <span className="status-ddos">TRAFFIC MASKED (DDoS: {ddosTimer})</span>
                )}
                {/* Global Actions */}
                <button 
                    onClick={() => onAction('purge')} 
                    disabled={isLoading}
                    className="action-button purge-button"
                >
                    [C] Purge Logs
                </button>
                <button 
                    onClick={() => onAction('wait')} 
                    disabled={isLoading}
                    className="action-button wait-button"
                >
                    [W] Wait/Idle
                </button>
            </div>
        </div>
    );
};

export default StatusHeader;