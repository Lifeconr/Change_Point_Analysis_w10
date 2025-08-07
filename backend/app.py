# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import pymc3 as pm
import os
import sys

# Add the project root to the sys.path to import from src

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import functions from existing oil_analysis.py
from src.oil_analysis import (
    load_data,
    preprocess_data,
    research_events,
    build_pymc3_model,
    run_mcmc
)

app = Flask(__name__)
CORS(app) # Enable CORS for communication with React frontend

# --- Global variables to store processed data and model results ---
# In a production app, you would load these from saved files after analysis
oil_data = None
events_df = None
trace_summary = None
most_probable_change_point_date = None
mu_1_hdi = None
mu_2_hdi = None
sigma_1_hdi = None
sigma_2_hdi = None

def run_analysis_and_store_results():
    """
    Runs the full analysis pipeline to get data and model results.
    This is called once when the Flask app starts.
    """
    global oil_data, events_df, trace_summary, most_probable_change_point_date
    global mu_1_hdi, mu_2_hdi, sigma_1_hdi, sigma_2_hdi

    print("Running initial analysis for Flask backend...")
    
    # Define the path to your data file
    data_path = os.path.join(project_root, 'data', 'BrentOilPrices.csv')

    # Load and preprocess the data
    raw_data = load_data(data_path)
    if raw_data is None:
        print("Failed to load raw data. Exiting analysis setup.")
        return

    oil_data = preprocess_data(raw_data)
    if oil_data is None:
        print("Failed to preprocess data. Exiting analysis setup.")
        return

    # Load curated global events
    events_df = research_events()

    # Prepare log returns for modeling
    log_returns_series = oil_data['log_returns']

    # Build Bayesian change point model
    # Note: Using a smaller number of draws/tune for faster startup in this example
    # In a real scenario, you'd use the full trace from your notebook.
    try:
        oil_model, tau = build_pymc3_model(log_returns_series)
        trace = run_mcmc(oil_model, draws=1000, tune=500, chains=2) # Reduced for quick demo
        
        # Get model summary
        summary_df = pm.summary(trace, hdi_prob=0.95, round_to=5)
        trace_summary = summary_df.to_dict(orient='index')

        # Extract most probable change point date
        tau_samples = trace['tau']
        unique_taus, counts = np.unique(tau_samples, return_counts=True)
        most_probable_tau_idx = unique_taus[np.argmax(counts)]
        most_probable_change_point_date = oil_data.index[most_probable_tau_idx].strftime('%Y-%m-%d')

        # Extract HDIs for parameters
        mu_1_hdi = pm.stats.hdi(trace['mu_1'], hdi_prob=0.95).tolist()
        mu_2_hdi = pm.stats.hdi(trace['mu_2'], hdi_prob=0.95).tolist()
        sigma_1_hdi = pm.stats.hdi(trace['sigma_1'], hdi_prob=0.95).tolist()
        sigma_2_hdi = pm.stats.hdi(trace['sigma_2'], hdi_prob=0.95).tolist()

        print("Analysis results stored.")

    except Exception as e:
        print(f"Error during analysis setup: {e}")
        # Set results to None to indicate failure
        trace_summary = None
        most_probable_change_point_date = None
        mu_1_hdi, mu_2_hdi, sigma_1_hdi, sigma_2_hdi = None, None, None, None


@app.route('/api/data', methods=['GET'])
def get_data():
    """
    API endpoint to serve historical oil price data and log returns.
    """
    if oil_data is None:
        return jsonify({"error": "Data not loaded or processed."}), 500
    
    # Convert DataFrame to a list of dicts for JSON serialization
    # Ensure datetime index is converted to string
    data_for_json = oil_data.reset_index().to_dict(orient='records')
    
    # Format dates as strings for JSON
    for record in data_for_json:
        record['Date'] = record['Date'].strftime('%Y-%m-%d')

    return jsonify(data_for_json)

@app.route('/api/analysis_results', methods=['GET'])
def get_analysis_results():
    """
    API endpoint to serve change point analysis results.
    """
    if trace_summary is None:
        return jsonify({"error": "Analysis results not available."}), 500

    results = {
        "summary": trace_summary,
        "most_probable_change_point_date": most_probable_change_point_date,
        "parameter_hdis": {
            "mu_1": mu_1_hdi,
            "mu_2": mu_2_hdi,
            "sigma_1": sigma_1_hdi,
            "sigma_2": sigma_2_hdi,
        },
        "events": events_df.to_dict(orient='records') if events_df is not None else []
    }
    # Ensure event dates are strings
    if results["events"]:
        for event in results["events"]:
            event['Date'] = event['Date'].strftime('%Y-%m-%d')

    return jsonify(results)

if __name__ == '__main__':
    run_analysis_and_store_results() # Run analysis once on startup
    app.run(debug=True, port=5000)

