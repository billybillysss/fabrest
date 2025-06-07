import logging

logger = logging.getLogger("fabrest")
logger.setLevel(logging.INFO)  # or INFO, WARNING, etc.


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)


formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler.setFormatter(formatter)

# Add handler to logger (avoid adding multiple times)
if not logger.hasHandlers():
    logger.addHandler(console_handler)
