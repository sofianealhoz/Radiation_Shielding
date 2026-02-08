import torch
import torch.nn as nn
import pytorch_lightning as pl

class ShieldTransformer(pl.LightningModule):
    def __init__(self, embed_dim=32, n_heads=2, n_layers=2):
        super().__init__()
        self.save_hyperparameters()

        self.mat_embedding = nn.Embedding(num_embeddings=10, embedding_dim=embed_dim//2)

        self.thick_proj = nn.Linear(1, embed_dim//2)

        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=n_heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        flatten_dim = 5 * embed_dim

        self.head = nn.Sequential(
            nn.Linear(flatten_dim + 1, 64),
            nn.ReLU(),
            nn.Linear(64,1),
            nn.Sigmoid()
        )

        self.criterion = nn.MSELoss()

    def forward(self, energy, sequence):
        mats_ids = sequence[:, :, 0].long()
        thick_val = sequence[:, :, 1].unsqueeze()

        emb_mat = self.mat_embedding(mats_ids)
        emb_thick = self.thick_proj(thick_val)

        x = torch.cat([emb_mat, emb_thick], dim=-1)

        x = self.transformer(x)

        x = x.view(x.size(0), -1)
                
        x = torch.cat([x, energy], dim=1)
        return self.head(x)
    
    def training_step(self, batch, batch_idx):
        y_hat = self(batch['energy'],batch['sequence'])
        loss=self.criterion(y_hat)
        self.log(loss)
        return(loss)

    def configure_optimizers(self):
            return torch.optim.Adam(self.parameters(), lr=1e-3)        
