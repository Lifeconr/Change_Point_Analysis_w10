import pandas as pd
import numpy as np
import pymc as pm
import matplotlib.pyplot as plt
import seaborn as sns
import arviz as az
from datetime import datetime

def load_and_preprocess_data(file_path):
    try:
        data = pd.read_csv(file_path)
        print("Data loaded successfully.")
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None

    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    data = data.sort_values('Date').reset_index(drop=True)
    data = data.set_index('Date')

    data['log_price'] = np.log(data['Price'])
    data['log_returns'] = data['log_price'].diff().fillna(0)

    print("Data preprocessed and log returns calculated.")
    return data

def research_events():
    events = pd.DataFrame({
        'Date': [
            '2003-03-20', '2008-09-15', '2014-11-27', '2016-01-20',
            '2020-03-08', '2022-02-24'
        ],
        'Event': [
            'US-led invasion of Iraq', 'Lehman Brothers collapse (Global Financial Crisis)',
            'OPEC refuses to cut production', 'Crude oil price hits 12-year low',
            'Saudi-Russia price war begins', 'Russia invades Ukraine'
        ],
        'Description': [
            'Major conflict in a key oil-producing region.',
            'Triggered a major global recession, reducing oil demand.',
            'OPEC shifts strategy to protect market share, leading to a price crash.',
            'Market oversupply fears intensify.',
            'Saudi Arabia and Russia fail to agree on production cuts, leading to a massive supply glut.',
            'Introduces significant geopolitical risk and supply chain disruptions.'
        ]
    })
    events['Date'] = pd.to_datetime(events['Date'])
    return events

def build_pymc_model(data):
    series = data.values
    n_series = len(series)

    with pm.Model() as oil_model:
        tau = pm.DiscreteUniform('tau', lower=0, upper=n_series)

        mu_1 = pm.Normal('mu_1', mu=0, sigma=1)
        mu_2 = pm.Normal('mu_2', mu=0, sigma=1)

        sigma_1 = pm.HalfNormal('sigma_1', sigma=1)
        sigma_2 = pm.HalfNormal('sigma_2', sigma=1)

        idx = np.arange(n_series)
        mu_latent = pm.math.switch(tau > idx, mu_1, mu_2)
        sigma_latent = pm.math.switch(tau > idx, sigma_1, sigma_2)

        returns = pm.Normal('returns', mu=mu_latent, sigma=sigma_latent, observed=series)

    print("PyMC model built successfully.")
    return oil_model, tau

def run_mcmc(model, draws=2000, chains=4, tune=1000):
    with model:
        trace = pm.sample(draws=draws, tune=tune, chains=chains, target_accept=0.9, random_seed=42)
    return trace

def plot_change_point_posterior(trace, dates):
    tau_samples = trace.posterior['tau'].values.flatten()
    plt.figure(figsize=(12, 6))

    unique_taus, counts = np.unique(tau_samples, return_counts=True)
    prob_density = counts / len(tau_samples)

    change_point_dates = dates[unique_taus].values
    plt.bar(change_point_dates, prob_density, width=10, alpha=0.7)

    plt.xlabel('Date of Change Point')
    plt.ylabel('Posterior Probability Density')
    plt.title('Posterior Distribution of the Change Point (tau)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    most_probable_tau = unique_taus[np.argmax(counts)]
    most_probable_date = dates[most_probable_tau]

    print(f"Most probable change point date: {most_probable_date.strftime('%Y-%m-%d')}")
def plot_price_and_returns(data):
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    data['Price'].plot(title='Brent Oil Prices')
    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.subplot(1, 2, 2)
    data['log_returns'].plot(title='Log Returns')
    plt.xlabel('Date')
    plt.ylabel('Log Return')

    plt.tight_layout()
    plt.show()

def plot_parameter_comparison(trace, param_before, param_after, param_name):
    before = trace.posterior[param_before].values.flatten()
    after = trace.posterior[param_after].values.flatten()

    plt.figure(figsize=(10, 5))
    sns.kdeplot(before, label=f'{param_name} Before Change Point', shade=True, alpha=0.5)
    sns.kdeplot(after, label=f'{param_name} After Change Point', shade=True, alpha=0.5)

    plt.xlabel(param_name)
    plt.ylabel('Posterior Probability Density')
    plt.title(f'Comparison of {param_name} Before and After Change Point')
    plt.legend()
    plt.show()

    hdi_before = az.hdi(before, hdi_prob=0.95)
    hdi_after = az.hdi(after, hdi_prob=0.95)

    print(f"95% HDI for {param_name} Before: {hdi_before}")
    print(f"95% HDI for {param_name} After: {hdi_after}")

def plot_model_fit(data, trace, dates):
    plt.figure(figsize=(15, 7))
    plt.plot(dates, data, 'k.', alpha=0.3, label='Log Returns')

    mu_1_mean = trace.posterior['mu_1'].values.flatten().mean()
    mu_2_mean = trace.posterior['mu_2'].values.flatten().mean()

    tau_samples = trace.posterior['tau'].values.flatten()
    unique_taus, counts = np.unique(tau_samples, return_counts=True)
    most_probable_tau = unique_taus[np.argmax(counts)]

    change_point_date = dates[most_probable_tau]

    fitted_series = np.concatenate([
        np.full(most_probable_tau, mu_1_mean),
        np.full(len(data) - most_probable_tau, mu_2_mean)
    ])

    plt.plot(dates, fitted_series, 'r-', lw=2, label='Posterior Mean Fit')
    plt.axvline(change_point_date, color='orange', linestyle='--', label='Most Probable Change Point')

    plt.xlabel('Date')
    plt.ylabel('Log Returns')
    plt.title('Bayesian Change Point Model Fit on Log Returns')
    plt.legend()
    plt.tight_layout()
    plt.show()
