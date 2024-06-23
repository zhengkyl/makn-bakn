from sqlmodel import SQLModel
from dotenv import load_dotenv
load_dotenv()

from db import engine

def main() -> None:
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    main()
