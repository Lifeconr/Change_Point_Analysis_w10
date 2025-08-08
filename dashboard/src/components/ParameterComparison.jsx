// dashboard/src/components/ParameterComparison.js)
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ParameterComparison = ({ paramName, paramBeforeHDI, paramAfterHDI, summary, summaryAfter, description }) => {
  // Create data for Recharts BarChart to represent HDIs and means
  const data = [
    {
      name: `Before Change Point`,
      mean: summary?.mean,
      hdi_low: paramBeforeHDI ? paramBeforeHDI[0] : null,
      hdi_high: paramBeforeHDI ? paramBeforeHDI[1] : null,
    },
    {
      name: `After Change Point`,
      mean: summaryAfter?.mean,
      hdi_low: paramAfterHDI ? paramAfterHDI[0] : null,
      hdi_high: paramAfterHDI ? paramAfterHDI[1] : null,
    },
  ].filter(d => d.mean !== null); // Filter out if data is not available

  return (
    <div className="section-card param-comparison-item">
      <h3>{paramName} Comparison</h3>
      <p className="description-text">{description}</p>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={data}
            margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip
              formatter={(value, name, props) => {
                if (name === 'Mean') return [value.toFixed(5), name];
                if (name === 'HDI Range') return [`[${props.payload.hdi_low.toFixed(5)}, ${props.payload.hdi_high.toFixed(5)}]`, name];
                return [value, name];
              }}
            />
            <Legend />
            <Bar dataKey="mean" fill="#6f42c1" name="Mean" /> {/* Using a standard purple */}
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <p className="no-data-text">No data available for this parameter comparison.</p>
      )}

      {/* Display HDIs as text for clarity */}
      <div className="hdi-text-container">
        {paramBeforeHDI && (
          <p>
            <span className="hdi-label">Before Change Point:</span> Mean = {summary?.mean?.toFixed(5) || 'N/A'}, 95% HDI = [{paramBeforeHDI[0]?.toFixed(5)}, {paramBeforeHDI[1]?.toFixed(5)}]
          </p>
        )}
        {paramAfterHDI && (
          <p>
            <span className="hdi-label">After Change Point:</span> Mean = {summaryAfter?.mean?.toFixed(5) || 'N/A'}, 95% HDI = [{paramAfterHDI[0]?.toFixed(5)}, {paramAfterHDI[1]?.toFixed(5)}]
          </p>
        )}
      </div>
    </div>
  );
};

export default ParameterComparison;
