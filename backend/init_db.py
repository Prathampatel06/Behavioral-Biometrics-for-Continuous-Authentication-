from backend.database import Base, engine

"""Initialize the database tables for the backend."""

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
