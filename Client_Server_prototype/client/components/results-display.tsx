import type React from 'react';
import './results-display.css';

interface ResultsDisplayProps {
  results?: any[];
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  if (!results || results.length === 0) {
    return null;
  }

  // Check for a single value result
  const isSingleValue = results.length === 1 && Object.keys(results[0]).length === 1;

  if (isSingleValue) {
    const key = Object.keys(results[0])[0];
    const value = results[0][key];
    return (
      <div className="stat-card">
        <div className="stat-value">{String(value)}</div>
        {/* Only show a label if it's descriptive, otherwise default to "Result" */}
        <div className="stat-label">{key.includes('(') || /^\d+$/.test(key) ? 'Result' : key}</div>
      </div>
    );
  }

  // Render a full table for other cases
  return (
    <div className="message-results-table">
      <table>
        <thead>
          <tr>
            {Object.keys(results[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((row, rIndex) => (
            <tr key={rIndex}>
              {Object.values(row).map((val, cIndex) => (
                <td key={cIndex}>{String(val)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}