# Standard library imports
import itertools
import random
from datetime import datetime, timedelta
from typing import Dict, Generator, List, Union

from dotenv import load_dotenv

# Third-party imports
from faker import Faker

from log.logger import get_logger as _logger

# load the dotenv file
load_dotenv()


logger = _logger("fake_tx_producer")


def generate_transactions(
    initial_timestamp: datetime = datetime(2025, 1, 1),
    time_increment: timedelta = timedelta(minutes=6),
    fraud_probability: float = 0.20,  # 20% chance of fraudulent transactions
) -> Generator[Dict[str, Union[int, datetime, float, bool]], None, None]:
    """
    Generate an infinite stream of credit card transactions with varied patterns
    suitable for fraud detection demos using Faker's pyfloat.

    Args:
        initial_timestamp (datetime): Starting timestamp for transactions
        time_increment (timedelta): Time difference between consecutive transactions
        fraud_probability (float): Probability of generating a fraudulent transaction

    Returns:
        Generator[Dict[str, Union[int, datetime, float, bool]], None, None]:
            A generator yielding dictionaries with transaction data containing:
            - accountId (int): Account identifier from a fixed set
            - timestamp (datetime): Transaction timestamp with constant increment
            - amount (float): Transaction amount in dollars
    """
    # Initialize Faker
    fake = Faker()
    Faker.seed(12345)

    # Define account IDs
    account_ids: List[int] = [1, 2, 3, 4, 5]

    # Define spending patterns per account
    spending_patterns = {
        1: {"min": 50, "max": 300},  # Regular consumer
        2: {"min": 200, "max": 800},  # High spender
        3: {"min": 20, "max": 200},  # Conservative spender
        4: {"min": 100, "max": 500},  # Moderate spender
        5: {"min": 200, "max": 600},  # Business account
    }

    # Create infinite cycle of account IDs
    account_cycle = itertools.cycle(account_ids)
    current_timestamp = initial_timestamp

    def generate_normal_amount(account_id: int) -> float:
        """Generate a normal transaction amount using fake.pyfloat."""
        pattern = spending_patterns[account_id]
        return round(
            fake.pyfloat(
                min_value=pattern["min"],
                max_value=pattern["max"],
                right_digits=2,
                positive=True,
            ),
            2,
        )

    def generate_fraudulent_amount(account_id: int) -> float:
        """Generate a fraudulent transaction amount using fake.pyfloat."""
        pattern = spending_patterns[account_id]

        # Fraudulent patterns
        fraud_types = [
            # Micro transactions
            lambda: fake.pyfloat(
                min_value=0.01, max_value=5.00, right_digits=2, positive=True
            ),
            # Unusually large purchases
            lambda: fake.pyfloat(
                min_value=pattern["max"] * 2,
                max_value=pattern["max"] * 5,
                right_digits=2,
                positive=True,
            ),
            # Round number purchases
            lambda: float(random.choice([50, 100, 500, 1000, 2000, 5000])),
        ]

        return round(random.choice(fraud_types)(), 2)

    while True:
        account_id = next(account_cycle)
        is_fraudulent = random.random() < fraud_probability

        amount = (
            generate_fraudulent_amount(account_id)
            if is_fraudulent
            else generate_normal_amount(account_id)
        )

        transaction = {
            "accountId": account_id,
            "timestamp": current_timestamp,
            "amount": amount,
        }

        current_timestamp += time_increment
        yield transaction
