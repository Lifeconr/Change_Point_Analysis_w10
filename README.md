## Brent Oil Price Change Point Analysis 

This project analyzes historical Brent oil prices to detect significant shifts in market behavior using Bayesian modeling with PyMC. It features an interactive React dashboard to visualize price trends, change points, and correlated geopolitical/economic events, providing actionable insights for energy market stakeholders.
The dashboard is accessible locally at: http://localhost:5173

✨ Features

Bayesian Change Point Detection: Identifies shifts in price behavior (mean and volatility) using PyMC.
Interactive Charts: Displays Brent oil prices and log returns with Recharts.
Change Point Visualization: Highlights the most probable change point on the price chart.
Parameter Comparison: Shows changes in mean returns and volatility before and after the change point.
Event Correlation: Lists key events with clickable details in a modal.
Responsive Design: Built with custom CSS for accessibility across devices.

📂 Project Structure
``` Change_Point_Analysis_w10/
├── data/
│   └── BrentOilPrices.csv       # Historical Brent oil price data
├── src/
│   └── oil_analysis.py          # Data processing and PyMC analysis
├── backend/
│   ├── app.py                   # Flask API server
│   └── requirements.txt         # Python dependencies
├── dashboard/
│   ├── public/
│   │   └── index.html           # Main HTML file
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── App.css              # Custom CSS styling
│   │   ├── main.jsx             # React entry point
│   │   └── components/
│   │       ├── PriceChart.jsx   # Price and returns chart
│   │       ├── ParameterComparison.jsx # Parameter visualization
│   │       └── EventList.jsx    # Event list with modal
│   ├── package.json             # Node.js dependencies
│   └── vite.config.js           # Vite configuration
└── README.md                    # Project documentation
```

🛠️ Setup & Installation
1. Clone the Repository
```git clone <repository_url>
cd Change_Point_Analysis_w10
```

2. Prepare Data
  Place BrentOilPrices.csv in the data/ directory.
3. Backend Setup (Flask)
  Navigate to the backend:
  cd backend
  
  Create and activate a virtual environment:
  ```# Windows
  python -m venv venv
  .\venv\Scripts\activate
  ```
  Install dependencies:
  
    ```pip install -r requirements.txt ```

4. Frontend Setup (React)
Navigate to the dashboard:

```cd ../dashboard```

Install Node.js dependencies:

```npm install ```

▶️ Running the Application
1. Start the Backend
  In the backend/ directory, run:
  ```python app.py ```
The Flask server will run at http://127.0.0.1:5000.
2. Start the Frontend
  In a new terminal, navigate to dashboard/ and run:
  
  ```npm run dev```
  Open http://localhost:5173 in your browser.
📊 Usage

  View Trends: Explore Brent oil prices and log returns.
  Identify Change Points: See the detected change point marked on the chart.
  Compare Parameters: Review shifts in mean returns and volatility.
  Explore Events: Click events in the list or chart for detailed descriptions.

🚧 Challenges & Solutions

  PyMC Migration: Updated from PyMC3 to PyMC v4+, adapting posterior access and ArviZ integration.
  JSX Parsing: Renamed .js files to .jsx to fix Vite’s JSX parsing errors.
  Styling: Replaced problematic Tailwind CSS with custom CSS in App.css for a stable, responsive design.

🔮 Future Enhancements

  Enhance Bayesian models with multiple change points or covariates.
  Add interactive filters and forecasting to the dashboard.
  Deploy the application using Docker on a cloud platform.

🤝 Contributing
  Fork the repository, suggest improvements, or submit pull requests. For issues, please include detailed steps to reproduce.
