import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torchvision import transforms
import pytorch_lightning as pl
import torchmetrics

class LitClassification(pl.LightningModule):
    def __init__(self, model, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()
        self.model = model
        self.train_acc = torchmetrics.Accuracy()
        self.valid_acc = torchmetrics.Accuracy()

    def forward(self, x):
        x = self.model(x)
        return x

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.hparams.lr)
        return optimizer

    def training_step(self, train_batch, batch_idx):

        x, y = train_batch
        out = self.model(x) 
        loss = F.cross_entropy(out, y)
        # print(loss)
        self.log('train_loss', loss.item())
        self.train_acc(out, y)
        self.log('train_acc', self.train_acc, on_step=True, on_epoch=False)

        return loss

    def validation_step(self, val_batch, batch_idx):

        x, y = val_batch
        out = self.model(x)    
        loss = F.cross_entropy(out, y)
        self.log('valid_loss', loss.item())
        self.valid_acc(out, y)
        self.log('valid_acc', self.valid_acc, on_step=False, on_epoch=True)