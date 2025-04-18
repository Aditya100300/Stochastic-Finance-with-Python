# chapter2/test/test_dataset_adapters.py

"""
Smokescreen test: fetch AAPL & GOOG prices, print summaries, and plot them.
Run via:
    python -m chapter2.test.test_dataset_adapters
"""

from chapter2.stock_price_dataset_adapters import YahooFinancialsAdapter
import chapter2.visualization as vs

def test_yahoo_financials_adapter():
    # Build a dict of ticker→DataFrame for two symbols
    records = {
        'Apple Inc': YahooFinancialsAdapter(
            ticker="AAPL",
            training_set_date_range=("2021-02-01", "2021-04-30"),
        ).training_set,
        'Google':    YahooFinancialsAdapter(
            ticker="GOOG",
            training_set_date_range=("2021-02-01", "2021-04-30"),
        ).training_set
    }

    # Print out basic info for each DataFrame
    for name, df in records.items():
        print(f"\n=== {name} ===")
        # Shape: (rows, columns)
        print("Shape:", df.shape)
        # First 5 rows
        print(df.head().to_string(index=False))

    # Now plot them all
    vs.plot_security_prices(records, 'stock price')

# When run as a script, execute the test function
if __name__ == "__main__":
    test_yahoo_financials_adapter()
