# chapter2/return_computation.py
# Computes simple returns (R_t = S_t / S_{t-1} − 1) at different frequencies
from stock_price_dataset_adapters import YahooFinancialsAdapter, Frequency
import visualization as vs

def compute_returns():
    # Monthly data
    monthly = YahooFinancialsAdapter(
        frequency=Frequency.MONTHLY
    ).training_set
    # Simple return: current / previous − 1
    monthly["Return"] = monthly["stock price"].shift(-0)  \
                        / monthly["stock price"].shift(1) - 1

    # Weekly data
    weekly = YahooFinancialsAdapter(
        frequency=Frequency.WEEKLY
    ).training_set
    weekly["Return"] = weekly["stock price"] / weekly["stock price"].shift(1) - 1

    # Daily data
    daily = YahooFinancialsAdapter(
        frequency=Frequency.DAILY
    ).training_set
    daily["Return"] = daily["stock price"] / daily["stock price"].shift(1) - 1

    # Package results for plotting: list of (label, DataFrame)
    periodic_returns = [
        ("Daily",  daily),
        ("Weekly", weekly),
        ("Monthy", monthly)
    ]
    return periodic_returns

def test_plot_periodic_returns():
    """
    A quick smoke‐test: fetch returns and call the plotting helper.
    """
    periodic_returns = compute_returns()
    vs.plot_returns_for_different_periods("Pfizer", periodic_returns)
