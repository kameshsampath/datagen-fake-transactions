#!/usr/bin/env python3
import argparse
import asyncio
import json
import os

from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

from log.logger import get_logger as _logger
from producer import tx_producer

load_dotenv()

logger = _logger("kafka_producer")


async def send_message(producer: AIOKafkaProducer, topic, delay: int = 1):
    # Create transaction generator
    transaction_generator = tx_producer.generate_transactions()

    # Generate transaction
    tx = next(transaction_generator)

    # Convert datetime to string for JSON serialization
    tx["timestamp"] = tx["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Send message
        await producer.send_and_wait(topic, value=tx)

        logger.info(
            f"Sent: Account: {tx['accountId']}, "
            f"Time: {tx['timestamp']}, "
            f"Amount: ${tx['amount']:.2f}, "
        )

        # Add small delay between messages
        await asyncio.sleep(delay)

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise e


async def produce_transactions(
    bootstrap_servers: str,
    topic: str,
    delay: float = 1,
    bounds: int = -1,
):
    """
    Asynchronously produce transactions to Kafka topic.
    """

    # Initialize producer
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        # Optional performance settings
        enable_idempotence=True,
        compression_type="gzip",
        linger_ms=100,
    )

    try:
        # Start the producer
        await producer.start()
        logger.info("Starting to generate and send transactions...")
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 80)

        if bounds == -1:
            while True:
                await send_message(producer, topic, delay)
        else:
            for _ in range(bounds):
                await send_message(producer, topic, delay)

    except KeyboardInterrupt:
        logger.warning("\nStopping transaction generation...")
    finally:
        # Cleanup
        await producer.stop()
        logger.info("Producer stopped")


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
        "-n",
        "--num-transactions",
        type=int,
        default=-1,
        help="Number of transactions to generate (-1 for infinite)",
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
        "-d",
        "--delay",
        type=float,
        default=1.0,
        help="Delay between messages in seconds",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        produce_transactions(
            bounds=args.num_transactions,
            topic=args.topic,
            bootstrap_servers=args.bootstrap_servers,
            delay=args.delay,
        )
    )
