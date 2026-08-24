# db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./detections.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    role = Column(String)  # "Farmer" or "Researcher"
    detections = relationship("Detection", back_populates="owner")

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    #timestamp = Column(DateTime, server_default=func.now())
    timestamp = Column(DateTime, default=datetime.now)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    media_type = Column(String)   # "image" | "live_frame"
    media_path = Column(String)   # path to saved processed output
    raw_results = Column(JSON)    # YOLO prediction data
    main_weeds = Column(String)   # comma-separated weed names
    total_detections = Column(Integer, default=0) 
    
    owner = relationship("User", back_populates="detections")

def init_db():
    Base.metadata.create_all(bind=engine)