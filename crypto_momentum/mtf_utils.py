import pandas as pd


def get_htf_interval(interval: str) -> str:
    mapping = {
        "1m": "5m",
        "2m": "15m",
        "5m": "15m",
        "15m": "1h",
        "30m": "1h",
        "60m": "4h",
        "1h": "4h",
        "90m": "1d",
        "1d": "1wk",
        "5d": "1mo",
        "1wk": "1mo",
        "1mo": "3mo",
    }
    return mapping.get(interval, "1wk")


def get_htf_period(period: str) -> str:
    mapping = {
        "1d": "5d",
        "5d": "1mo",
        "1mo": "6mo",
        "3mo": "1y",
        "6mo": "2y",
        "1y": "5y",
        "2y": "max",
        "5y": "max",
        "10y": "max",
        "ytd": "max",
        "max": "max",
    }
    return mapping.get(period, "max")
