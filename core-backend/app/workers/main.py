import asyncio

from app.core.logging import configure_logging
from app.workers.outbox_worker import worker


def main() -> None:
    configure_logging()
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()