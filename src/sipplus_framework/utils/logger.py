from loguru import logger


def setup_logger(log_level: str) -> None:
    """Loguru-логгер для вывода в консоль."""

    logger.remove()
    logger.configure(extra={"request_id": "-"})
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan> | "
            "request_id=<magenta>{extra[request_id]}</magenta> | "
            "{message}\n"
        ),
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
