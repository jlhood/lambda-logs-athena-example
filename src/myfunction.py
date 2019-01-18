"""Lambda function handler."""

# must be the first import in files with lambda function handlers
import lambdainit  # noqa: F401

import decimal
import json
import random

SYMBOLS = [
    'AMZN',
    'AAPL',
    'GOOG',
    'TSLA',
    'FB',
]
SECTOR = [
    'HEALTHCARE',
    'TECH',
    'FINANCE'
]


def handler(event, context):
    """Lambda function handler."""
    for _ in range(10):
        # using print so the log is only JSON data
        print(json.dumps(_generate_json_data()))


def _generate_json_data():
    return {
        'ticker_symbol': random.choice(SYMBOLS),
        'sector': random.choice(SECTOR),
        'change': float(_random_decimal_between(1.12, 3.13)),
        'price': float(_random_decimal_between(23.45, 98.76))
    }


def _random_decimal_between(a, b):
    return decimal.Decimal(random.randrange(int(a * 100), int(b * 100))) / 100
