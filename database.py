

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
     "sqlite+libsql:///embedded.db",
     connect_args={
         "sync_url": "libsql://coll-c766e74b4a974272b188e43d174331e7-mayson.aws-ap-south-1.turso.io",
         "auth_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NzcyOTE2MjMsInAiOnsicm9hIjp7Im5zIjpbIjAxOWRjZWQ1LWU0MDEtN2ZmNS1iNTU5LWU5NjAwZjNlOTU5NyJdfSwicnciOnsibnMiOlsiMDE5ZGNlZDUtZTQwMS03ZmY1LWI1NTktZTk2MDBmM2U5NTk3Il19fSwicmlkIjoiN2QxOGU2YmQtODliNS00ODYyLTgzOTItNzMxMjZiYzk1MjljIn0.lLTapG0Rfihf4NASfpM9mXQNlnptiFV457zf_CkJtz1LN2xajBQuTkgDdFHAwR_8NolvUMAXLdwb1v3tvP05Dw",
     },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()

