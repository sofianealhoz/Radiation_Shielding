import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from sqlalchemy import create_engine
import os
import numpy as np

# Mapping des matériaux vers des entiers (Tokenization)
MATERIAL_MAP = {"Lead": 1, "Concrete": 2, "Steel": 3, "Water": 4}
MAX_LAYERS = 5  # On paddera avec des 0 si moins de couches

class ShieldDataset(Dataset):
    def __init__(self, db_url):
        engine = create_engine(db_url)
        
        # Requête SQL pour joindre les tables et obtenir le format liste
        query = """
        SELECT 
            s.id, s.energy_mev, s.transmission,
            l.material, l.thickness_cm, l.order_index
        FROM simulations s
        JOIN simulation_layers l ON s.id = l.simulation_id
        ORDER BY s.id, l.order_index
        """
        df = pd.read_sql(query, engine)

        self.samples = []
        self.samples = []
        grouped = df.groupby('id')

        for sim_id, group in grouped:
            # Features globales (Energie)
            energy = group.iloc[0]['energy_mev']
            target = group.iloc[0]['transmission']
            
            # Features séquentielles (Couches)
            layers_seq = []
            for _, row in group.iterrows():
                mat_id = MATERIAL_MAP.get(row['material'], 0)
                thick = row['thickness_cm']
                layers_seq.append([mat_id, thick])
            
            self.samples.append({
                'energy': energy,
                'layers': layers_seq,
                'target': target
            })