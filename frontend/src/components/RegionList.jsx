// frontend/src/components/RegionList.jsx

import React from 'react';
import RegionCard from './RegionCard';
import './RegionList.css'; // Create this CSS file

const RegionList = ({ regions, onAction }) => {
    if (!regions || !Array.isArray(regions)) {
        return <div>Loading sectors...</div>;
    }
    return (
        <div className="region-list">
            <h2>SECTORS</h2>
            {regions.map((region, index) => (
                <RegionCard 
                    key={region.name} 
                    region={region} 
                    index={index} 
                    onAction={onAction} 
                />
            ))}
        </div>
    );
};

export default RegionList;