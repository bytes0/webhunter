from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Optional
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bugbounty.db")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Database Models
class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(String(36), primary_key=True)  # scan_id - UUID string
    target = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="started")  # started, running, completed, failed
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    scan_type = Column(String(50), default="recon")
    results = Column(JSON, nullable=True)
    
    # Relationships
    subdomains = relationship("Subdomain", back_populates="scan", cascade="all, delete-orphan")
    ports = relationship("Port", back_populates="scan", cascade="all, delete-orphan")
    technologies = relationship("Technology", back_populates="scan", cascade="all, delete-orphan")
    whois_records = relationship("WhoisRecord", back_populates="scan", cascade="all, delete-orphan")
    dns_records = relationship("DnsRecord", back_populates="scan", cascade="all, delete-orphan")
    wayback_urls = relationship("WaybackUrl", back_populates="scan", cascade="all, delete-orphan")


class Subdomain(Base):
    __tablename__ = "subdomains"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    subdomain = Column(String(255), nullable=False)
    source = Column(String(100), default="sublist3r")
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="subdomains")


class Port(Base):
    __tablename__ = "ports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)
    service = Column(String(100), nullable=True)
    version = Column(String(100), nullable=True)
    state = Column(String(20), default="open")
    
    # Relationship
    scan = relationship("Scan", back_populates="ports")


class Technology(Base):
    __tablename__ = "technologies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    technology = Column(String(255), nullable=False)
    version = Column(String(100), nullable=True)
    confidence = Column(String(20), default="high")
    source = Column(String(100), default="nuclei")
    
    # Relationship
    scan = relationship("Scan", back_populates="technologies")


# OSINT-specific models
class WhoisRecord(Base):
    __tablename__ = "whois_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    domain = Column(String(255), nullable=False)
    registrar = Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    name_servers = Column(JSON, nullable=True)  # Store as JSON array
    emails = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="whois_records")


class DnsRecord(Base):
    __tablename__ = "dns_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    domain = Column(String(255), nullable=False)
    record_type = Column(String(10), nullable=False)  # A, AAAA, MX, NS, TXT, CNAME
    record_value = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="dns_records")


class WaybackUrl(Base):
    __tablename__ = "wayback_urls"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    domain = Column(String(255), nullable=False)
    url = Column(String(1000), nullable=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="wayback_urls")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine) 