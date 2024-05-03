import dotenv
from pathlib import Path
import os

env_path = '.env'

def get_session():
    dotenv.load_dotenv(env_path)
    return os.getenv('SESS')

def get_auth():
    dotenv.load_dotenv(env_path)
    return os.getenv('AUTH')

def get_twid():
    dotenv.load_dotenv(env_path)
    return os.getenv('TWID')