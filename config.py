import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'air-ticket-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///airline.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

