import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'change_this_to_a_random_secret'
    DATABASE = os.path.join(BASE_DIR, 'parking.db')
