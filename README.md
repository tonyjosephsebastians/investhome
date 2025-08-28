# InvestHome - Retirement Savings Calculator

InvestHome is a user-friendly web application built with Streamlit that helps you project your retirement savings based on various investment scenarios. It provides a comprehensive set of tools to visualize your financial future, compare different investment options, and make informed decisions about your retirement plan.

![InvestHome Screenshot](assets/home.jpg)

## Features

- **Retirement Savings Projection:** Calculate the future value of your savings based on your current age, retirement age, savings, and contributions.
- **Customizable Investment Options:** Choose from a wide range of investment options, including:
    - **Major Indices:** S&P 500 (SPY) and Nasdaq (QQQ)
    - **Cryptocurrencies:** Bitcoin (BTC) and Ethereum (ETH)
    - **Bonds:** 10-Year Government and Corporate Bonds
    - **Individual Stocks:** Dynamically fetches and includes stocks from NASDAQ, TSX, and NYSE.
    - **Custom Returns:** Manually enter an expected annual return for personalized scenarios.
- **Inflation Adjustment:** Account for inflation to get a more realistic projection of your future purchasing power.
- **Visualizations:** Interactive charts and data tables to help you understand your savings growth over time.
- **Investment Comparison:** Compare the potential outcomes of multiple investment strategies side-by-side.
- **Data Export:** Download your savings projection data as a CSV file for further analysis.
- **Recommended Reading:** Discover highly-rated investment books to expand your financial knowledge.

## How It Works

The application uses the `yfinance` library to fetch historical stock data and calculates the compounded annual growth rate (CAGR) over the last five years to estimate annual returns. For bonds and custom inputs, it uses predefined or user-specified rates.

The core of the application is a projection loop that iteratively calculates your savings growth year by year, factoring in your annual contributions and the expected investment returns.

## Installation

To run this application locally, you'll need to have Python installed. Follow these steps to get started:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tonyjosephsebastians/investhome.git
   cd investhome
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run investhome.py
   ```

The application will open in your default web browser.

## Usage

1. **Input Your Details:** Use the sidebar to enter your current age, desired retirement age, current savings, and contribution details.
2. **Select an Investment:** Choose an investment exchange (e.g., NASDAQ, NYSE) and then select a specific investment option from the dropdown menu.
3. **Adjust for Inflation (Optional):** Check the "Adjust for Inflation" box to see how inflation might impact your savings.
4. **Analyze the Projections:** Review the savings projection chart, key metrics, and yearly breakdown to understand your financial forecast.
5. **Compare Scenarios:** Use the "Multiple Investment Options" tool to compare different investment strategies.
6. **Export Your Data:** Download your projection data as a CSV file for your personal records.

## File Structure

- `investhome.py`: The main Python script containing the Streamlit application code.
- `nasdaqlist.xlsx`, `nyse.xlsx`, `crypto.xlsx`: Excel files containing lists of stocks and cryptocurrencies for the investment options.
- `requirements.txt`: A list of the Python libraries required to run the application.
- `README.md`: This documentation file.
- `assets/`: Directory containing images and other static assets.

## Contributing

Contributions are welcome! If you have any ideas for improvements or new features, feel free to open an issue or submit a pull request.
