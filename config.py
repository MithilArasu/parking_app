import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'change_this_to_a_random_secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'parking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
