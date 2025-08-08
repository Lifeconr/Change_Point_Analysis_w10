// src/App.jsx
import React from "react";
import PriceChart from "./components/PriceChart";
import ParameterComparison from "./components/ParameterComparison";
import EventList from "./components/EventList";
import "./index.css";

function App() {
  return (
    <div className="container">
      <h1>Brent Oil Price Change Point Dashboard</h1>

      <div className="chart-container">
        <PriceChart />
      </div>

      <div className="chart-container">
        <ParameterComparison />
      </div>

      <div className="chart-container">
        <EventList />
      </div>
    </div>
  );
}

export default App;
