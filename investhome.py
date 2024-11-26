import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from PIL import Image


def format_in_millions_billions_trillions(value):
    if value >= 1_000_000_000_000:  # If value is 1 trillion or more
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:  # If value is 1 billion or more
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:  # If value is 1 million or more
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.2f}"  # For values less than 1 million, format normally

# Fetch stock data for annual growth calculation
def get_stock_return(stock_symbol):
    try:
        stock_data = yf.Ticker(stock_symbol)
        # Fetch data for the last 10 years
        hist = stock_data.history(period="10y")  # Last 10 years
        # Calculate annualized return for 10 years
        annual_return = (hist['Close'][-1] / hist['Close'][0]) ** (1 / 10) - 1
        return annual_return
    except Exception as e:
        print(f"Error: {e}")
        return 0.07  # Default 7% for equity

# Inflation adjustment
def adjust_for_inflation(rate, inflation_rate):
    return rate - inflation_rate

# Cap growth assumptions
def cap_growth_assumption(rate, min_rate=0.02, max_rate=0.2):
    return max(min(rate, max_rate), min_rate)






# Load and display the image in the sidebar
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

# Feature Selection with Selectbox
features = ["Retirement Calculator"]
selected_feature = st.sidebar.selectbox("Topics:", features)

# Load the selected feature
if selected_feature == "Retirement Calculator":
    st.title("Retirement Savings Calculator")
    # (Retirement Calculator code goes here)

    # Sidebar Inputs
    st.sidebar.header("Inputs")
    current_age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=30, step=1)
    retirement_age = st.sidebar.number_input("Retirement Age", min_value=current_age + 1, max_value=100, value=65, step=1)
    current_savings = st.sidebar.number_input("Current Savings ($)", min_value=0, value=10000, step=1000)

    contribution_frequency = st.sidebar.selectbox("Contribution Frequency", ["Monthly", "Biweekly", "Quarterly", "Annual"])
    contribution_value = st.sidebar.number_input(f"{contribution_frequency} Contribution ($)", min_value=0, value=500, step=50)

    # Calculate annual contribution based on frequency
    if contribution_frequency == "Biweekly":
        annual_contribution = contribution_value * 26
    elif contribution_frequency == "Quarterly":
        annual_contribution = contribution_value * 4
    elif contribution_frequency == "Annual":
        annual_contribution = contribution_value
    else:
        annual_contribution = contribution_value * 12

    investment_options = {
        "S&P 500 Index Fund (ETF)": lambda: get_stock_return("SPY"),
        "Nasdaq ETF (QQQ)": lambda: get_stock_return("QQQ"),
        "Bitcoin (BTC)": lambda: get_stock_return("BTC-USD"),
        "Ethereum (ETH)": lambda: get_stock_return("ETH-USD"),
        "Government Bond (10-year)": lambda: 0.03,
        "Corporate Bond (10-year)": lambda: 0.05,
        "Custom": None
    }

    selected_option = st.sidebar.selectbox("Select Investment Option", list(investment_options.keys()))
    manual_return = 0.0
    if selected_option == "Custom":
        manual_return = st.sidebar.number_input("Enter Expected Annual Return (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1) / 100
    else:
        manual_return = investment_options[selected_option]()

    # # Apply growth capping
    # manual_return = cap_growth_assumption(manual_return)

    # Inflation Adjustment
    adjust_for_inflation_option = st.sidebar.checkbox("Adjust for Inflation")
    inflation_rate = st.sidebar.number_input("Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100
    if adjust_for_inflation_option:
        manual_return = adjust_for_inflation(manual_return, inflation_rate)

    # Projection
    years_to_invest = retirement_age - current_age
    savings = [current_savings]
    contributions = [0]
    growth = [0]

    for year in range(1, years_to_invest + 1):
        annual_growth = savings[-1] * manual_return
        contributions.append(annual_contribution)
        growth.append(annual_growth)
        savings.append(savings[-1] + annual_contribution + annual_growth)

    # Data Visualization
    years = list(range(current_age, retirement_age + 1))
    df = pd.DataFrame({
        "Year": years,
        "Total Savings": savings,
        "Contributions": pd.Series(contributions).cumsum(),
        "Growth": pd.Series(growth).cumsum()
    })

    st.subheader("Savings Projection")
    st.line_chart(df.set_index("Year")[["Contributions", "Total Savings"]])

    # Key Metrics
    total_contributions = sum(contributions)
    total_growth = savings[-1] - total_contributions - current_savings

    # CAGR
    start_value = current_savings
    end_value = savings[-1]
    cagr = ((end_value / start_value) ** (1 / years_to_invest) - 1) if start_value > 0 else 0

    st.subheader("Key Metrics")
    st.metric("Total Savings at Retirement", format_in_millions_billions_trillions(savings[-1]))
    st.metric("Total Contributions", format_in_millions_billions_trillions(total_contributions))
    st.metric("Total Returns", format_in_millions_billions_trillions(total_growth))
    st.metric("Compound Annual Growth Rate (CAGR)", f"{cagr * 100:.2f}%")
    st.metric("Annual Return (%)", f"{manual_return * 100:.2f}%")
    # Yearly Breakdown
    st.subheader("Yearly Breakdown")
    st.write(df)


    # Comparison Tool
    st.subheader("Multiple Investment Options")
    comparison_options = st.multiselect(
        "Select Investment Options to Compare",
        list(investment_options.keys()),
        default=[selected_option]
    )

    comparison_data = pd.DataFrame({"Year": years})
    comparison_metrics = []

    for option in comparison_options:
        return_rate = investment_options[option]() if option != "Custom" else manual_return
        option_savings = [current_savings]
        for year in range(1, years_to_invest + 1):
            option_savings.append(option_savings[-1] * (1 + return_rate) + annual_contribution)
        total_option_contributions = annual_contribution * years_to_invest
        total_option_savings = option_savings[-1]
        total_option_returns = total_option_savings - total_option_contributions - current_savings
        comparison_data[option] = option_savings
        option_cagr = ((total_option_savings / current_savings) ** (1 / years_to_invest) - 1) if current_savings > 0 else 0
        comparison_metrics.append({
        "Option": option,
        "Annual Return (%)": f"{return_rate * 100:.2f}%",
        "Total contributions": format_in_millions_billions_trillions(total_option_contributions),  # Format contributions
        "Total Savings": format_in_millions_billions_trillions(total_option_savings),  # Format savings
        "CAGR": f"{option_cagr * 100:.2f}%",
    })
    if comparison_metrics:
        # Display Comparison
        st.line_chart(comparison_data.set_index("Year"))
        st.write(pd.DataFrame(comparison_metrics))

    # Export as CSV
    st.subheader("Export Data")
    csv = df.to_csv(index=False)
    st.download_button(label="Download Projection as CSV", data=csv, file_name="savings_projection.csv", mime="text/csv")

    # Responsive Design
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
    col1, col2, col3,col4 = st.columns(4)

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
