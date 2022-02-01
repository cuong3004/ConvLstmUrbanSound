from custom_data import CustomData
import torch 
import albumentations as A
from albumentations.pytorch import ToTensorV2
from utils import *
import matplotlib.pyplot as plt
from tqdm import tqdm
import librosa.display
from model import CnnLstm, CNNModel
from torch.utils.data import DataLoader, random_split
import pytorch_lightning as pl
from litmodule import LitClassification
from torchvision.models import mobilenet_v2
import torch.nn as nn
import os
import pandas as pd
from glob import glob
from callbacks import input_monitor_train, input_monitor_valid, checkpoint_callback, early_stop_callback


batch_size = 32
num_classes = 10

npobj = np.load("normalize.npz")
mean, std = npobj['mean'], npobj['std']
print("mean, std : ", mean, std)

transform = A.Compose([
    A.Normalize(mean=mean, std=std, max_pixel_value=1),
    ToTensorV2()
])

dir_class = {
    0: "air_conditioner",
    1: "car_horn",
    2: "children_playing",
    3: "dog_bark",
    4: "drilling",
    5: "engine_idling",
    6: "gun_shot",
    7: "jackhammer",
    8: "siren",
    9:"street_music",
}

if not os.path.exists("data.csv"):
    listdata = glob("data/*/*.npz")
    df = pd.DataFrame()
    df["path"] = listdata
    df.to_csv("data.csv")

dataset = CustomData(
                csv_file="data.csv",
                transform=transform,
                )


train_len = int(len(dataset)*0.8)
valid_len = len(dataset)-train_len
data_train, data_valid = random_split(dataset,[train_len, valid_len])


train_loader = DataLoader(data_train, batch_size=batch_size, shuffle=True)
valid_loader = DataLoader(data_valid, batch_size=batch_size, shuffle=True)




# for id, (image, label) in tqdm(enumerate(dataset)):
    


# for id, (image, label) in tqdm(enumerate(dataset)):
#     # librosa.display.specshow(image)
#     # plt.savefig(f"image/{id}_{label}.png")
#     # plt.clf()
#     print(image.shape)
#     if id == 10:
#         break

# model_cnn = CnnLstm(cnn_model, lstm_model)
cnn_model = mobilenet_v2()
cnn_model.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
cnn_model.classifier[1] = torch.nn.Linear(1280,num_classes)
# cnn_model = CNNModel()

model_cnnlstm = CnnLstm(cnn_model)
model = LitClassification(model_cnnlstm)

callbacks = [input_monitor, checkpoint_callback, early_stop_callback]

trainer = pl.Trainer(
                gpus=1, 
                callbacks = callbacks, 
                # max_epochs=epoch,
                )
trainer.fit(model, train_loader, valid_loader)