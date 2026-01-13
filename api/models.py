from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class Simulation(Base):
    __tablename__ = "simulations"

    # Clé primaire (UUID)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Paramètres d'entrée globaux
    energy_mev = Column(Float, nullable=False)
    photons = Column(Integer, nullable=False)
    
    # Résultats globaux
    transmission = Column(Float)
    buildup_factor = Column(Float)
    dose_transmitted = Column(Float)
    uncertainty = Column(Float)
    status = Column(String, default="COMPLETED")

    # Relation : Une simulation a plusieurs couches
    # cascade="all, delete" signifie que si on supprime la simu, on supprime ses couches
    layers = relationship("SimulationLayer", back_populates="simulation", cascade="all, delete-orphan")


class SimulationLayer(Base):
    __tablename__ = "simulation_layers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Clé étrangère : Lien vers la table 'simulations'
    simulation_id = Column(String, ForeignKey("simulations.id"), nullable=False)
    
    # Détails de la couche
    order_index = Column(Integer, nullable=False) # Important pour garder l'ordre (1ère couche, 2ème...)
    material = Column(String, nullable=False)
    thickness_cm = Column(Float, nullable=False)
    density = Column(Float, nullable=False)

    # Relation inverse
    simulation = relationship("Simulation", back_populates="layers")