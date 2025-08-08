# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import pymc as pm # Changed from pymc3
import arviz as az # Import arviz
import os
import sys

# Add the project root to the sys.path to import from src
# Assuming this script is in Change_Point_Analysis_w10/backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import functions from your existing oil_analysis.py
from src.oil_analysis import (
    load_and_preprocess_data, # Use the consolidated function
    research_events,
    build_pymc_model, # Corrected model builder function name as per your oil_analysis.py
    run_mcmc
)

app = Flask(__name__)
CORS(app) # Enable CORS for communication with React frontend

# --- Global variables to store processed data and model results ---
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
    Runs the full analysis pipeline to get data and model results using PyMC v4+.
    This is called once when the Flask app starts.
    """
    global oil_data, events_df, trace_summary, most_probable_change_point_date
    global mu_1_hdi, mu_2_hdi, sigma_1_hdi, sigma_2_hdi

    print("Running initial analysis for Flask backend...")
    
    data_path = os.path.join(project_root, 'data', 'BrentOilPrices.csv')

    # Load and preprocess the data using the consolidated function
    oil_data = load_and_preprocess_data(data_path)
    if oil_data is None:
        print("Failed to load or preprocess data. Exiting analysis setup.")
        return

    events_df = research_events()
    log_returns_series = oil_data['log_returns']

    try:
        oil_model, tau_variable = build_pymc_model(log_returns_series) # Corrected function call
        
        # Run MCMC sampling - result is an InferenceData object
        trace = run_mcmc(oil_model, draws=2000, tune=1000, chains=2) 
        
        # Check if InferenceData object is valid
        if trace is None or not hasattr(trace, 'posterior'):
            raise ValueError("PyMC InferenceData object is invalid after sampling.")

        # Get model summary using ArviZ
        summary_df = az.summary(trace, hdi_prob=0.95, round_to=5)
        trace_summary = summary_df.to_dict(orient='index')

        # Initialize most_probable_tau_idx to None outside the conditional block
        most_probable_tau_idx = None 

        # Extract most probable change point date from InferenceData
        tau_samples = trace.posterior['tau'].values.flatten() # Access samples from InferenceData
        
        if tau_samples.size > 0:
            unique_taus, counts = np.unique(tau_samples, return_counts=True)
            if unique_taus.size > 0: 
                temp_most_probable_tau_idx = unique_taus[np.argmax(counts)] 
                
                if temp_most_probable_tau_idx < len(oil_data.index):
                    most_probable_tau_idx = int(temp_most_probable_tau_idx) # Ensure integer index
                    most_probable_change_point_date = oil_data.index[most_probable_tau_idx].strftime('%Y-%m-%d')
                else:
                    most_probable_change_point_date = None
                    print(f"Warning: Most probable tau index {temp_most_probable_tau_idx} out of bounds ({len(oil_data.index)}). Setting date to None.")
            else:
                most_probable_change_point_date = None
                print("Warning: No unique tau samples found after processing. Setting date to None.")
        else:
            most_probable_change_point_date = None
            print("Warning: No tau samples available for most probable date calculation. Setting date to None.")

        # Extract HDIs for parameters using ArviZ
        try:
            mu_1_hdi = az.hdi(trace.posterior['mu_1'].values.flatten(), hdi_prob=0.95).tolist()
            mu_2_hdi = az.hdi(trace.posterior['mu_2'].values.flatten(), hdi_prob=0.95).tolist()
            sigma_1_hdi = az.hdi(trace.posterior['sigma_1'].values.flatten(), hdi_prob=0.95).tolist()
            sigma_2_hdi = az.hdi(trace.posterior['sigma_2'].values.flatten(), hdi_prob=0.95).tolist()
        except Exception as hdi_e:
            print(f"Warning: Could not compute HDI for some parameters: {hdi_e}. Setting HDIs to [None, None].")
            mu_1_hdi, mu_2_hdi, sigma_1_hdi, sigma_2_hdi = [None,None], [None,None], [None,None], [None,None]

        print("Analysis results stored and ready to be served.")

    except Exception as e:
        print(f"Error during analysis setup: {e}")
        # Ensure all global variables are reset on error
        trace_summary = None
        most_probable_change_point_date = None
        mu_1_hdi, mu_2_hdi, sigma_1_hdi, sigma_2_hdi = None, None, None, None


@app.route('/api/data', methods=['GET'])
def get_data():
    """
    API endpoint to serve historical oil price data and log returns.
    """
    if oil_data is None:
        print("Error: /api/data called but oil_data is None.")
        return jsonify({"error": "Data not loaded or processed. Check backend logs."}), 500
    
    data_for_json = oil_data.reset_index().to_dict(orient='records')
    
    for record in data_for_json:
        record['Date'] = record['Date'].strftime('%Y-%m-%d')

    return jsonify(data_for_json)

@app.route('/api/analysis_results', methods=['GET'])
def get_analysis_results():
    """
    API endpoint to serve change point analysis results.
    """
    if trace_summary is None:
        print("Error: /api/analysis_results called but trace_summary is None.")
        return jsonify({"error": "Analysis results not available. Check backend logs."}), 500

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
    if results["events"]:
        for event in results["events"]:
            if isinstance(event['Date'], pd.Timestamp): # Ensure 'Date' is a Timestamp before formatting
                event['Date'] = event['Date'].strftime('%Y-%m-%d')

    return jsonify(results)

if __name__ == '__main__':
    run_analysis_and_store_results() 
    app.run(debug=True, port=5000)

