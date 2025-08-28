import streamlit as st
import pandas as pd
import yfinance as yf
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt

# Suppress yfinance console logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

@retry(stop=stop_after_attempt(3))
@lru_cache(maxsize=128)
def get_stock_return(stock_symbol):
    """
    Fetches historical stock data to calculate the compounded annual growth rate (CAGR).
    
    Args:
        stock_symbol (str): The stock symbol to fetch data for (e.g., "SPY").
        
    Returns:
        float: The calculated annual return. Returns a default of 7% if an error occurs.
    """
    try:
        stock_data = yf.Ticker(stock_symbol)
        # Fetch data for the last 5 years
        hist = stock_data.history(period="5y")
        if hist.empty:
            st.warning(f"No historical data found for {stock_symbol}. Using default return rate.")
            return 0.07
            
        hist = hist['Close'].dropna()  # Remove NaN values
        if len(hist) < 2:
            st.warning(f"Not enough data for {stock_symbol} to calculate returns. Using default rate.")
            return 0.07

        initial_price = hist.iloc[0]
        final_price = hist.iloc[-1]
        
        # Calculate the number of years from the actual data for a more accurate CAGR
        num_years = (hist.index[-1] - hist.index[0]).days / 365.25
        if num_years < 1:
            st.warning(f"Investment period for {stock_symbol} is less than a year. Using default rate.")
            return 0.07

        annual_return = (final_price / initial_price) ** (1 / num_years) - 1
        return annual_return
    except Exception as e:
        st.warning(f"Error fetching data for {stock_symbol}: {e}. Using default return rate.")
        return 0.07  # Default 7% for equity

def format_in_millions_billions_trillions(value):
    """
    Formats a numerical value into a string representation in millions, billions, or trillions.
    
    Args:
        value (float): The numerical value to format.
        
    Returns:
        str: A formatted string with 'M', 'B', or 'T' suffix for millions, billions, or trillions.
    """
    if value >= 1_000_000_000_000:  # If value is 1 trillion or more
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:  # If value is 1 billion or more
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:  # If value is 1 million or more
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.2f}"  # For values less than 1 million, format normally


def adjust_for_inflation(rate, inflation_rate):
    """
    Adjusts a given rate for inflation.
    
    Args:
        rate (float): The rate to adjust.
        inflation_rate (float): The inflation rate.
        
    Returns:
        float: The inflation-adjusted rate.
    """
    return rate - inflation_rate

def cap_growth_assumption(rate, min_rate=0.02, max_rate=0.2):
    """
    Caps the growth assumption to a specified min/max range.
    
    Args:
        rate (float): The growth rate to cap.
        min_rate (float): The minimum allowed rate.
        max_rate (float): The maximum allowed rate.
        
    Returns:
        float: The capped growth rate.
    """
    return max(min(rate, max_rate), min_rate)

def get_Investmentoption(exchange):
    """
    Retrieves a dictionary of investment options based on the selected stock exchange.
    
    Args:
        exchange (str): The stock exchange to get options for ("NASDAQ", "TSX TORONTO", "NYSE", "CRYPTO").
        
    Returns:
        dict: A dictionary of investment options with their corresponding return calculation functions.
    """
    # Start with a base set of common investment options
    investment_options = {
        "S&P 500 Index Fund (ETF)": lambda: get_stock_return("SPY"),
        "Nasdaq ETF (QQQ)": lambda: get_stock_return("QQQ"),
        "Bitcoin (BTC)": lambda: get_stock_return("BTC-USD"),
        "Ethereum (ETH)": lambda: get_stock_return("ETH-USD"),
        "Government Bond (10-year)": lambda: 0.03,
        "Corporate Bond (10-year)": lambda: 0.05,
        "Custom": None
    }

    # Helper function to load and process data from Excel files
    def load_options_from_excel(filepath, sheet, parser_func):
        try:
            df = pd.read_excel(filepath, sheet_name=sheet, header=None)
            for _, row in df.iterrows():
                try:
                    symbol, description = parser_func(row)
                    if symbol and description:
                        # Use a lambda with a default argument to correctly capture the symbol
                        investment_options[description] = lambda s=symbol: get_stock_return(s)
                except (IndexError, ValueError):
                    # Skip rows that are malformed
                    continue
        except FileNotFoundError:
            st.warning(f"Data file not found: {filepath}. Some investment options may be missing.")
        except Exception as e:
            st.error(f"Error reading {filepath}: {e}")

    # Define parsers for different file formats
    def parse_nasdaq(row):
        parts = row[0].split("|")
        return parts[0], parts[1]

    def parse_nyse(row):
        return str(row[0]).strip(), str(row[1]).strip()

    def parse_crypto(row):
        symbol = str(row[0]).strip()
        description = str(row[1]).strip()
        return f"{symbol}-USD", description

    # Load additional options based on the selected exchange
    if exchange == "NASDAQ":
        load_options_from_excel("nasdaqlist.xlsx", "Sheet1", parse_nasdaq)
    elif exchange == "TSX TORONTO":
        load_options_from_excel("nasdaqlist.xlsx", "Sheet2", parse_nasdaq)
    elif exchange == "NYSE":
        load_options_from_excel("nyse.xlsx", "nyse", parse_nyse)
    elif exchange == "CRYPTO":
        load_options_from_excel("crypto.xlsx", "coinmarketcap", parse_crypto)

    return investment_options




# --- Streamlit UI Configuration ---

# Sidebar Title and Icon
st.sidebar.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
    <div style="display: flex; align-items: center; gap: 10px;">
        <i class="bi bi-house-fill" style="font-size: 1.5em;  color: #000000;"></i>
        <h1 style="font-size: 20px; margin: 0;">InvestHome</h1>
    </div>
    """,
    unsafe_allow_html=True
)

#st.sidebar.markdown("Home for Smarter Investment Choices.")

# --- Feature Selection ---
features = ["Retirement Calculator"]
selected_feature = st.sidebar.selectbox("Topics:", features)

# --- Retirement Calculator Feature ---
if selected_feature == "Retirement Calculator":
    st.title("Retirement Savings Calculator")

    # --- Sidebar Inputs for Retirement Calculator ---
    st.sidebar.header("Inputs")
    current_age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=30, step=1)
    retirement_age = st.sidebar.number_input("Retirement Age", min_value=current_age + 1, max_value=100, value=65, step=1)
    current_savings = st.sidebar.number_input("Current Savings ($)", min_value=0, value=10000, step=1000)

    contribution_frequency = st.sidebar.selectbox("Contribution Frequency", ["Monthly", "Biweekly", "Quarterly", "Annual"])
    contribution_value = st.sidebar.number_input(f"{contribution_frequency} Contribution ($)", min_value=0, value=500, step=50)

    # Calculate annual contribution based on the selected frequency
    if contribution_frequency == "Biweekly":
        annual_contribution = contribution_value * 26
    elif contribution_frequency == "Quarterly":
        annual_contribution = contribution_value * 4
    elif contribution_frequency == "Annual":
        annual_contribution = contribution_value
    else:  # Monthly
        annual_contribution = contribution_value * 12

    # Investment option selection
    selected_exchange = st.sidebar.selectbox("Select Exchange", ["NASDAQ", "TSX TORONTO", "NYSE", "CRYPTO"])
    investment_options = get_Investmentoption(selected_exchange)
    selected_option = st.sidebar.selectbox("Search and Select Investment option", list(investment_options.keys()))
    manual_return = 0.0
    if selected_option == "Custom":
        manual_return = st.sidebar.number_input("Enter Expected Annual Return (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1) / 100
    else:
        manual_return = investment_options[selected_option]()

    # # Apply growth capping (currently commented out)
    # manual_return = cap_growth_assumption(manual_return)

    # Inflation adjustment based on user input
    adjust_for_inflation_option = st.sidebar.checkbox("Adjust for Inflation")
    inflation_rate = st.sidebar.number_input("Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100
    if adjust_for_inflation_option:
        manual_return = adjust_for_inflation(manual_return, inflation_rate)

    # --- Savings Projection Calculation ---
    years_to_invest = retirement_age - current_age
    savings = [current_savings]
    contributions = [0]
    growth = [0]

    # Loop through each year to calculate savings growth
    for year in range(1, years_to_invest + 1):
        annual_growth = savings[-1] * manual_return
        contributions.append(annual_contribution)
        growth.append(annual_growth)
        savings.append(savings[-1] + annual_contribution + annual_growth)

    # --- Data Visualization and Metrics ---
    years = list(range(current_age, retirement_age + 1))
    df = pd.DataFrame({
        "Year": years,
        "Total Savings": savings,
        "Contributions": pd.Series(contributions).cumsum(),
        "Growth": pd.Series(growth).cumsum()
    })

    # Display the savings projection chart
    st.subheader("Savings Projection")
    st.line_chart(df.set_index("Year")[["Contributions", "Total Savings"]])

    # --- Key Metrics Display ---
    total_contributions = sum(contributions)
    total_growth = savings[-1] - total_contributions - current_savings

    # Calculate Compound Annual Growth Rate (CAGR)
    start_value = current_savings
    end_value = savings[-1]
    if start_value > 0 and years_to_invest > 0:
        cagr = ((end_value / start_value) ** (1 / years_to_invest)) - 1
    else:
        cagr = 0

    st.subheader("Key Metrics")
    st.metric("Total Savings at Retirement", format_in_millions_billions_trillions(savings[-1]))
    st.metric("Total Contributions", format_in_millions_billions_trillions(total_contributions))
    st.metric("Total Returns", format_in_millions_billions_trillions(total_growth))
    st.metric("Compound Annual Growth Rate (CAGR)", f"{cagr * 100:.2f}%")
    st.metric("Annual Return (%)", f"{manual_return * 100:.2f}%")
    
    # Display the yearly breakdown in a table
    st.subheader("Yearly Breakdown")
    st.write(df)

    # --- Investment Comparison Tool ---
    st.subheader("Multiple Investment Options")
    comparison_options = st.multiselect(
        "Select Investment Options to Compare",
        list(investment_options.keys()),
        default=[selected_option]
    )

    comparison_data = pd.DataFrame({"Year": years})
    comparison_metrics = []

    # Calculate projections for each selected comparison option
    for option in comparison_options:
        return_rate = investment_options[option]() if option != "Custom" else manual_return
        option_savings = [current_savings]
        for year in range(1, years_to_invest + 1):
            option_savings.append(option_savings[-1] * (1 + return_rate) + annual_contribution)
        total_option_contributions = annual_contribution * years_to_invest
        total_option_savings = option_savings[-1]
        total_option_returns = total_option_savings - total_option_contributions - current_savings
        comparison_data[option] = option_savings
        if current_savings > 0 and years_to_invest > 0:
            option_cagr = ((total_option_savings / current_savings) ** (1 / years_to_invest)) - 1
        else:
            option_cagr = 0
        comparison_metrics.append({
            "Option": option,
            "Annual Return (%)": f"{return_rate * 100:.2f}%",
            "Total contributions": format_in_millions_billions_trillions(total_option_contributions),
            "Total Savings": format_in_millions_billions_trillions(total_option_savings),
            "CAGR": f"{option_cagr * 100:.2f}%",
        })
        
    if comparison_metrics:
        # Display comparison chart and metrics table
        st.line_chart(comparison_data.set_index("Year"))
        st.write(pd.DataFrame(comparison_metrics))

    # --- Data Export ---
    st.subheader("Export Data")
    csv = df.to_csv(index=False)
    st.download_button(label="Download Projection as CSV", data=csv, file_name="savings_projection.csv", mime="text/csv")

    # --- Styling and Layout ---
    # Custom CSS for responsive design
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 20%;
        }
        [data-testid="stAppViewContainer"] {
            max-width: 90%;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Recommended Books Section ---
    st.markdown(
    """
    <h4 style="color: black;">
        <i class="bi bi-book" style="color: black; font-size: 30px; margin-right: 10px;"></i>Recommended Investment Books
    </h4>
    """, unsafe_allow_html=True
)

    # Book details (title, image, affiliate link)
    books = [
        {
            "title": "The Intelligent Investor",
            "image": "https://images-na.ssl-images-amazon.com/images/I/91+t0Di07FL.jpg",
            "link": "https://amzn.to/3Z3lShD"
        },
        {
            "title": "Rich Dad Poor Dad",
            "image": "https://images-na.ssl-images-amazon.com/images/I/81bsw6fnUiL.jpg",
            "link": "https://amzn.to/3CMcWWk"
        },
        {
            "title": "The Psychology of Money",
            "image": "https://m.media-amazon.com/images/I/41UjwN3DzVL._SY445_SX342_.jpg",
            "link": "https://amzn.to/3Z5W2cD"
        }
    ]

    # Display books in a grid
    col1, col2, col3 = st.columns(3)

    for col, book in zip([col1, col2, col3], books):
        with col:
            st.image(book["image"], width=150)
            st.markdown(f"##### {book['title']}")
            st.markdown(
                f'<a href="{book["link"]}" target="_blank">'
                f'<button style="background-color: green; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px;">Buy on Amazon</button>'
                f'</a>',
                unsafe_allow_html=True
            )
