// frontend/src/components/LogWindow.jsx

import React, { useRef, useEffect } from 'react';
import './LogWindow.css'; // Create this CSS file

const LogWindow = ({ events }) => {
    const logRef = useRef(null);

    // Auto-scroll to the bottom when new events arrive
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [events]);

    const formatLogMessage = (message) => {
        // Map ANSI colors (from override2.py) to CSS classes for styling
        if (message.includes('SUCCESS') || message.includes('Extracted') || message.includes('DIVIDENDS') || message.includes('SOLIDIFIED')) {
            return <span className="log-green" dangerouslySetInnerHTML={{ __html: message.replace(/\*\*\*/g, '<b>').replace(/\*\*\*/g, '</b>') }} />;
        }
        if (message.includes('FAILURE') || message.includes('Trace spiked') || message.includes('SACRIFICE') || message.includes('HUNTER')) {
            return <span className="log-fail">{message}</span>;
        }
        if (message.includes('WARNING') || message.includes('ALERT') || message.includes('Insufficient')) {
            return <span className="log-warning">{message}</span>;
        }
        if (message.includes('IDLE') || message.includes('DDoS')) {
            return <span className="log-cyan">{message}</span>;
        }
        return <span>{message}</span>;
    };

    return (
        <div className="log-window">
            <h3>LATEST LOGS</h3>
            <div className="log-content" ref={logRef}>
                {events.map((msg, index) => (
                    <p key={index} className="log-entry">
                        &gt; {formatLogMessage(msg)}
                    </p>
                ))}
            </div>
        </div>
    );
};

export default LogWindow;