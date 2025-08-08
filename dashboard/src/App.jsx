// frontend/src/App.jsx (or dashboard/src/App.jsx)
import React, { useState, useEffect, useCallback } from 'react';
import PriceChart from './components/PriceChart.jsx'; // Changed to .jsx
import ParameterComparison from './components/ParameterComparison.jsx'; // Changed to .jsx
import EventList from './components/EventList.jsx'; // Changed to .jsx
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';

// IMPORTANT: Ensure your Flask backend is running on this URL
const API_BASE_URL = 'http://127.0.0.1:5000';

function App() {
  const [oilData, setOilData] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [dataResponse, analysisResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/data`),
        fetch(`${API_BASE_URL}/api/analysis_results`)
      ]);

      if (!dataResponse.ok) throw new Error(`HTTP error! status: ${dataResponse.status} from /api/data`);
      if (!analysisResponse.ok) throw new Error(`HTTP error! status: ${analysisResponse.status} from /api/analysis_results`);

      const data = await dataResponse.json();
      const analysis = await analysisResponse.json();

      // Convert dates to Date objects for charting
      const formattedData = data.map(d => ({
        ...d,
        Date: new Date(d.Date)
      }));

      // Sort data by date for chronological display
      formattedData.sort((a, b) => a.Date - b.Date);

      setOilData(formattedData);
      setAnalysisResults(analysis);
    } catch (e) {
      console.error("Failed to fetch data:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedEvent(null);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-text">Loading analysis data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-title">Error: {error}</div>
        <p className="error-message">Please ensure the Flask backend is running at {API_BASE_URL}.</p>
      </div>
    );
  }

  const mostProbableChangePointDate = analysisResults?.most_probable_change_point_date
    ? new Date(analysisResults.most_probable_change_point_date)
    : null;

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <h1>Brent Oil Price Analysis Dashboard</h1>
          <p>Insights from Birhan Energies</p>
        </div>
      </header>

      <main className="main-content">
        {/* Project Overview */}
        <section className="section-card">
          <h2>Project Overview</h2>
          <p>
            This dashboard presents the results of a Bayesian Change Point analysis on historical Brent oil prices. Our goal is to identify statistically significant shifts in price behavior and correlate them with major geopolitical and economic events. This provides Birhan Energies' stakeholders with actionable insights to understand market volatility and inform strategic decisions.
          </p>
        </section>

        {/* Main Price Chart */}
        <section className="section-card">
          <h2>Historical Brent Oil Prices & Log Returns</h2>
          <p>
            Explore the historical trends of Brent oil prices and their daily log returns. The orange dashed line indicates the most probable change point detected by our Bayesian model, suggesting a significant shift in market dynamics around that time.
          </p>
          <PriceChart
            data={oilData}
            changePointDate={mostProbableChangePointDate}
            events={analysisResults?.events || []}
            onEventClick={handleEventClick}
          />
        </section>

        {/* Key Indicators & Parameter Comparison */}
        <section className="section-card">
          <h2>Key Indicators & Model Parameter Shifts</h2>
          <p>
            Our model detected significant changes in both the mean daily log return and the volatility (standard deviation) of Brent oil prices before and after the identified change point. These charts illustrate the posterior distributions of these parameters, providing probabilistic insights into the market's new regime.
          </p>
          <div className="param-comparison-grid">
            <ParameterComparison
              paramName="Mean Log Return"
              paramBeforeHDI={analysisResults?.parameter_hdis?.mu_1}
              paramAfterHDI={analysisResults?.parameter_hdis?.mu_2}
              summary={analysisResults?.summary?.mu_1}
              summaryAfter={analysisResults?.summary?.mu_2}
              description="Average daily percentage change in oil prices."
            />
            <ParameterComparison
              paramName="Volatility (Sigma)"
              paramBeforeHDI={analysisResults?.parameter_hdis?.sigma_1}
              paramAfterHDI={analysisResults?.parameter_hdis?.sigma_2}
              summary={analysisResults?.summary?.sigma_1}
              summaryAfter={analysisResults?.summary?.sigma_2}
              description="Measure of daily price fluctuation (risk)."
            />
          </div>
        </section>

        {/* Event List */}
        <section className="section-card">
          <h2>Key Geopolitical & Economic Events</h2>
          <p>
            This list compiles major events that could have influenced Brent oil prices. Click on an event to see its details.
          </p>
          <EventList events={analysisResults?.events || []} onEventClick={handleEventClick} />
        </section>
      </main>

      {/* Event Details Modal */}
      <Transition appear show={isModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeModal}>
          <Transition.Child
            as={Fragment}
            enter="modal-enter-from"
            enterTo="modal-enter-to"
            leave="modal-leave-from"
            leaveTo="modal-leave-to"
          >
            <div className="modal-overlay" />
          </Transition.Child>

          <div className="modal-container">
            <div className="modal-center-items">
              <Transition.Child
                as={Fragment}
                enter="modal-panel-enter-from"
                enterTo="modal-panel-enter-to"
                leave="modal-panel-leave-from"
                leaveTo="modal-panel-leave-to"
              >
                <Dialog.Panel className="modal-panel">
                  <Dialog.Title
                    as="h3"
                    className="modal-title"
                  >
                    {selectedEvent?.Event}
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="modal-description-date">
                      Date: {selectedEvent?.Date}
                    </p>
                    <p className="modal-description-text">
                      {selectedEvent?.Description}
                    </p>
                  </div>

                  <div className="mt-4">
                    <button
                      type="button"
                      className="modal-close-button"
                      onClick={closeModal}
                    >
                      Got it, thanks!
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}

export default App;
