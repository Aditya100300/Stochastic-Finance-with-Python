# chapter2/stock_price_dataset_adapters.py
# —————————————
# 1. Imports & setup
# —————————————
from yahoofinancials import YahooFinancials   # Official Yahoo Finance wrapper
from abc import ABC, abstractmethod, ABCMeta  # For defining abstract base classes
import pandas as pd                           # DataFrame handling
import enum                                   # For Frequency enum
import requests                               # For MarketStack API calls
from typing import List                       # Type hint for lists
import sys                                    # To get maxsize in pagination

# —————————————
# 2. Frequency enum
# —————————————
class Frequency(enum.Enum):
    """Predefined fetch intervals."""
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"

# —————————————
# 3. Adapter interface
# —————————————
class StockPriceDatasetAdapter(metaclass=ABCMeta):
    """
    Interface to access any stock‐price data source.
    Implementations must provide `training_set` & `validation_set`.
    """
    DEFAULT_TICKER = "PFE"  # Pfizer is the default if none provided

    @property
    @abstractmethod
    def training_set(self):
        """Return a DataFrame of (time, stock price) for model training."""
        ...

    @property
    @abstractmethod
    def validation_set(self):
        """Return a DataFrame of (time, stock price) for validation."""
        ...

# —————————————
# 4. Base class for adapters
# —————————————
class BaseStockPriceDatasetAdapter(StockPriceDatasetAdapter, ABC):
    """
    Holds common logic: storing ticker & datasets, copying on access.
    """
    def __init__(self, ticker: str = None):
        self._ticker = ticker
        self._training_set = None
        self._validation_set = None

    @abstractmethod
    def _connect_and_prepare(self, date_range: tuple):
        """Implementors fetch data between two dates and return a DataFrame."""
        ...

    @property
    def training_set(self):
        # Return a copy so the internal DataFrame isn’t accidentally mutated
        return self._training_set.copy()

    @property
    def validation_set(self):
        return self._validation_set.copy()

# —————————————
# 5. Yahoo Financials adapter
# —————————————
class YahooFinancialsAdapter(BaseStockPriceDatasetAdapter):
    """
    Fetches stock‐price data via yahoofinancials.
    """
    def __init__(
        self,
        ticker=StockPriceDatasetAdapter.DEFAULT_TICKER,
        frequency=Frequency.DAILY,
        training_set_date_range=("2020-01-01", "2021-12-31"),
        validation_set_date_range=("2013-07-01", "2013-08-31"),
    ):
        super().__init__(ticker=ticker)
        self._frequency = frequency
        self._yf = YahooFinancials(self._ticker)
        # Fetch & cache training/validation sets
        self._training_set   = self._connect_and_prepare(training_set_date_range)
        self._validation_set = self._connect_and_prepare(validation_set_date_range)

    def _connect_and_prepare(self, date_range: tuple):
        """
        Internal helper (leading `_` means “private”).
        Calls Yahoo API, converts JSON to DataFrame, renames columns.
        """
        records = self._yf.get_historical_price_data(
            date_range[0], date_range[1], self._frequency.value
        )[self._ticker]

        df = pd.DataFrame(data=records["prices"])[["formatted_date", "close"]]
        # Standardize column names
        df.rename(columns={"formatted_date": "time", "close": "stock price"},
                  inplace=True)
        return df

# —————————————
# 6. Market Stack adapter
# —————————————
class MarketStackAdapter(BaseStockPriceDatasetAdapter):
    """
    Fetches stock‐price data via MarketStack (licensed, paginated API).
    """
    _REQ_PARAMS   = { "access_key": "ce72d47022d573ffb1c47820c7e98f15", "limit": 500 }
    _EOD_API_URL  = "http://api.marketstack.com/v1/eod"
    _TICKER_API_URL = "http://api.marketstack.com/v1/tickers"

    class _PaginatedRecords:
        """
        Duck‐typed iterable to page through API responses.
        Implements __getitem__ so you can `for page in PaginatedRecords: …`
        """
        def __init__(self, api_url, req_params):
            self._req_params    = req_params
            self._offset        = 0
            self._total_records = sys.maxsize
            self._api_url       = api_url

        def __getitem__(self, index):
            # Stop when offset exceeds total
            if (self._offset + self._req_params["limit"]) >= self._total_records:
                raise StopIteration()
            self._req_params["offset"] = self._offset
            resp = requests.get(self._api_url, self._req_params).json()
            self._total_records = resp["pagination"]["total"]
            self._offset       += self._req_params["limit"] + 1
            return resp["data"]

    def __init__(
        self,
        training_set_date_range=("2020-01-01", "2021-12-31"),
        validation_set_date_range=("2013-07-01", "2013-08-31"),
        ticker: str = None,
    ):
        super().__init__(ticker=ticker)
        self._training_set = self._connect_and_prepare(training_set_date_range)
        # Note: validation_set not shown in this sample

    def _connect_and_prepare(self, date_range: tuple):
        """
        Loops through _PaginatedRecords, collects per‐symbol DataFrames.
        Inner helper merges pages into a single dict of DataFrames.
        """
        def _extract_stock_price_details(stock_price_records, page):
            symbol = page["symbol"]
            df = stock_price_records.get(symbol, pd.DataFrame())
            entry = {
                "stock price": [page["close"]],
                "time":        [page["date"].split("T")[0]]
            }
            stock_price_records[symbol] = pd.concat(
                [df, pd.DataFrame(entry)], ignore_index=True
            )
            return stock_price_records

        if self._ticker is None:
            return None

        params = MarketStackAdapter._REQ_PARAMS.copy()
        params["symbols"]    = self._ticker
        params["date_from"]  = date_range[0]
        params["date_to"]    = date_range[1]

        stock_price_records = {}
        for records in MarketStackAdapter._PaginatedRecords(
            api_url=MarketStackAdapter._EOD_API_URL, req_params=params
        ):
            for page in records:
                stock_price_records = _extract_stock_price_details(
                    stock_price_records, page
                )
        return stock_price_records

    @classmethod
    def get_samples_of_available_tickers(cls):
        """
        Fetches a sample list of all tickers from MarketStack.
        """
        resp = requests.get(
            MarketStackAdapter._TICKER_API_URL, MarketStackAdapter._REQ_PARAMS
        ).json()
        return [rec["symbol"] for rec in resp["data"]]
