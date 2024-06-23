import os
from sqlmodel import create_engine

# import all models before initializing db
from models import User, Badge, Meal

engine = create_engine(os.environ.get("DATABASE_URL"))
