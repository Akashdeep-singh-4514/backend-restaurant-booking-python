import os 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT configuration
jwt_config = {
    "SECRET_KEY": os.getenv('SECRET_KEY'),
    "JWT_ALGORITHM": os.getenv('JWT_ALGORITHM'),
    "JWT_EXPIRATION_HOURS": int(os.getenv('JWT_EXPIRATION_HOURS', 24)),
    "JWT_EXPIRATION_MINUTES": int(os.getenv('JWT_EXPIRATION_MINUTES', 1440))  # 24 hours in minutes
}

