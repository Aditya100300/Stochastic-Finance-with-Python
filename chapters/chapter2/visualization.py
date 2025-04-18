# chapter2/visualization.py
# Simple matplotlib-based plotting of stock prices & returns
import matplotlib.pyplot as plt
from typing import Any, Dict, List

def plot_security_prices(all_records: Dict[str, Any], security_type):
    """Plot prices; try seaborn style if available."""
    try:
        plt.style.use("seaborn")
    except OSError:
        pass    # fallback to default style if seaborn isn’t installed


    n = len(all_records)
    rows = n // 2 if n > 1 else 1
    cols = 2 if n > 1 else 1

    fig, ax = plt.subplots(rows, cols)
    security_names = list(all_records.keys())
    i = 0
    r = 0

    def _axis_plot_security_prices(df, col, name):
        """
        df: the DataFrame to plot
        col: subplot column index
        name: title for this subplot
        """
        if n == 1:
            ax.set_title(name)
            df.plot(ax=ax, x="time", y=security_type)
        elif n == 2:
            ax[col].set_title(name)
            df.plot(ax=ax[col], x="time", y=security_type)
        else:
            ax[r, col].set_title(name)
            df.plot(ax=ax[r, col], x="time", y=security_type)

    while i < n:
        _axis_plot_security_prices(all_records[security_names[i]], 0, security_names[i])
        i += 1
        if i < n:
            _axis_plot_security_prices(all_records[security_names[i]], 1, security_names[i])
            i += 1
        r += 1

    fig.tight_layout()
    plt.show()

def plot_returns_for_different_periods(ticker, periodic_returns: List[tuple]):
    """
    Plots returns side‐by‐side for different frequencies.
    periodic_returns: list of (label, DataFrame)
    """
    plt.style.use("seaborn")
    fig, ax = plt.subplots(len(periodic_returns), 1)
    for idx, (label, df) in enumerate(periodic_returns):
        df.plot(ax=ax[idx], x="time", y="Return")
        ax[idx].set_title(f"{ticker} - {label} Returns")
    fig.tight_layout()
    plt.show()
