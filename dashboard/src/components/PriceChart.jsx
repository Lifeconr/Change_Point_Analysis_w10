// frontend/src/components/PriceChart.js (or dashboard/src/components/PriceChart.js)
import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

const PriceChart = ({ data, changePointDate, events, onEventClick }) => {
  // Filter events to only show those within the chart's date range for clarity
  const relevantEvents = (events || []).filter(event => {
    const eventDate = new Date(event.Date);
    // Check if the eventDate exists in the data's dates
    return data.some(d => d.Date.getTime() === eventDate.getTime());
  });

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="Date"
          type="category"
          tickFormatter={(tick) => new Date(tick).getFullYear()}
          minTickGap={50}
          angle={-45}
          textAnchor="end"
        />
        <YAxis yAxisId="left" domain={['auto', 'auto']} />
        <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} />
        <Tooltip
          labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
          formatter={(value, name, props) => {
            if (name === 'Brent Oil Price (USD)') return [`$${value.toFixed(2)}`, name];
            if (name === 'Daily Log Returns') return [value.toFixed(4), name];
            return [value, name];
          }}
        />
        <Legend />

        {/* Price Line */}
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="Price"
          stroke="#007bff" /* Using a standard blue */
          strokeWidth={2}
          dot={false}
          name="Brent Oil Price (USD)"
        />
        {/* Log Returns Line */}
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="log_returns"
          stroke="#dc3545" /* Using a standard red */
          strokeWidth={1}
          dot={false}
          name="Daily Log Returns"
          opacity={0.6}
        />

        {/* Change Point Reference Line */}
        {changePointDate && (
          <ReferenceLine
            x={changePointDate.toISOString().split('T')[0]} // Match date format
            stroke="orange"
            strokeDasharray="5 5"
            label={{ value: 'Change Point', position: 'insideTopRight', fill: 'orange', fontSize: 12 }}
          />
        )}

        {/* Event Highlights */}
        {relevantEvents.map((event, index) => (
          <ReferenceLine
            key={event.Event + index}
            x={new Date(event.Date).toISOString().split('T')[0]} // Match date format
            stroke="green"
            strokeDasharray="3 3"
            label={{
              value: event.Event,
              position: 'insideBottomLeft',
              fill: 'green',
              fontSize: 10,
              angle: -90,
              offset: 10,
              onClick: () => onEventClick(event), // Make label clickable
              style: { cursor: 'pointer' }
            }}
          >
            {/* Invisible rect for larger clickable area */}
            <rect x={-5} y={0} width={10} height="100%" fill="transparent" onClick={() => onEventClick(event)} />
          </ReferenceLine>
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;
