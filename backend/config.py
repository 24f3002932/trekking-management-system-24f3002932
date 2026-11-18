import os

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "development-secret-key-change-before-deployment"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-jwt-secret-change-before-deployment"
)

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "sqlite:///trek.db"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
