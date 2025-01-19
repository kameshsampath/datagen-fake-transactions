#!/usr/bin/env python3
import argparse
import asyncio
import json

from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv

from log.logger import get_logger as _logger

# load the dotenv file
load_dotenv()

logger = _logger("fake_tx_consumer")


async def consume_transactions(topic: str, bootstrap_servers: str, group_id: str):
    """
    Asynchronously consume transactions from Kafka topic.
    """
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=group_id,
        auto_offset_reset="earliest",
    )

    try:
        await consumer.start()

        async for msg in consumer:
            tx = msg.value
            logger.info(
                f"Received: Account: {tx['accountId']}, "
                f"Time: {tx['timestamp']}, "
                f"Amount: ${tx['amount']:.2f}, "
            )

    finally:
        await consumer.stop()


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate and send credit card transactions to Kafka topic",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-t", "--topic", type=str, default="transactions", help="Kafka topic name"
    )

    parser.add_argument(
        "-b",
        "--bootstrap-servers",
        type=str,
        default="localhost:9092",
        help="Kafka bootstrap servers",
    )

    parser.add_argument(
        "-g",
        "--group-id",
        type=str,
        default="fake-tx-group",
        help="Kafka consumer group",
    )

    return parser.parse_args()


# Run consumer
if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        consume_transactions(
            topic=args.topic,
            bootstrap_servers=args.bootstrap_servers,
            group_id=args.group_id,
        )
    )
