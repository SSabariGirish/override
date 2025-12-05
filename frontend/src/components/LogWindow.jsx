// frontend/src/components/LogWindow.jsx (Update the formatLogMessage function)

import React, { useRef, useEffect } from 'react';
import './LogWindow.css'; 

const LogWindow = ({ events }) => {
    const logRef = useRef(null);

    // Auto-scroll to the bottom when new events arrive
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [events]);

    const formatLogMessage = (message) => {
        // 1. Strip all complex ANSI codes (e.g., \033[92m or \033[0m)
        const strippedMessage = message.replace(/\x1b\[[0-9;]*m/g, '');

        // 2. Map keywords to simple CSS classes based on common ANSI colors
        let colorClass = '';
        
        const lowerMsg = strippedMessage.toLowerCase();

        if (lowerMsg.includes('success') || lowerMsg.includes('extracted') || lowerMsg.includes('logs purged')) {
            colorClass = 'log-green';
        } else if (lowerMsg.includes('fail') || lowerMsg.includes('sacrifice') || lowerMsg.includes('hunter')) {
            colorClass = 'log-fail';
        } else if (lowerMsg.includes('warning') || lowerMsg.includes('insufficient') || lowerMsg.includes('alert') || lowerMsg.includes('leak')) {
            colorClass = 'log-warning';
        } else if (lowerMsg.includes('ddos') || lowerMsg.includes('idle') || lowerMsg.includes('system reset') || lowerMsg.includes('dividends')) {
            colorClass = 'log-cyan';
        } else if (lowerMsg.includes('solidified') || lowerMsg.includes('proxy success')) {
            colorClass = 'log-gold';
        }

        // Return the stripped message wrapped in the determined class
        return <span className={colorClass}>{strippedMessage}</span>;
    };

    return (
        <div className="log-window">
            <h3>LATEST LOGS</h3>
            <div className="log-content" ref={logRef}>
                {events.map((msg, index) => (
                    // We must use the index for the key here, since the message can change
                    <p key={index} className="log-entry">
                        &gt; {formatLogMessage(msg)}
                    </p>
                ))}
            </div>
        </div>
    );
};

export default LogWindow;