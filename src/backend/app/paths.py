from pathlib import Path


ROOT_DIR = Path(__file__).absolute().parent.parent
APP_DIR = ROOT_DIR / 'app'
LOGS_DIR = ROOT_DIR / 'logs'
PROD_LOGS_DIR = LOGS_DIR / 'prod'
