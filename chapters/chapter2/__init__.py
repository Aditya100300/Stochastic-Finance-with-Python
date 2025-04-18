# chapter2/__init__.py
# This file makes `chapter2` a package and controls what’s imported
# when you do `from chapter2 import *`.
__all__ = [
    "stock_price_dataset_adapters",  # the adapter module
    "return_computation",            # the returns logic
    "visualization"                  # the plotting helpers
]
