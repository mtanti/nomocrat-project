#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2

# --- Set device (global) ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("🖥️ Using device:", device)
# device = torch.device("cpu")
# print("🧠 Using CPU (safe mode)")


# --- Dataset Class ---
class SegmentationDataset(Dataset):
    def __init__(self, image_dir, mask_dir):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.image_files = [f for f in os.listdir(image_dir) if f.endswith(".png")]

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_name = self.image_files[idx]
        image_path = os.path.join(self.image_dir, image_name)
        mask_path = os.path.join(self.mask_dir, image_name)

        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)

        mask = Image.open(mask_path).convert("L")
        mask = mask.resize((256, 256), resample=Image.NEAREST)
        mask = torch.from_numpy(np.array(mask)).long()

        return image, mask


# --- Tiny UNet Model ---
class UNet(nn.Module):
    def __init__(self, in_channels=3, out_classes=10):
        super().__init__()

        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
                nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
            )

        self.enc1 = conv_block(in_channels, 32)
        self.enc2 = conv_block(32, 64)
        self.enc3 = conv_block(64, 128)
        self.enc4 = conv_block(128, 256)
        self.pool = nn.MaxPool2d(2)

        self.bottleneck = conv_block(256, 512)

        self.up4 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec4 = conv_block(512, 256)
        self.up3 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec3 = conv_block(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec2 = conv_block(128, 64)
        self.up1 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec1 = conv_block(64, 32)

        self.out = nn.Conv2d(32, out_classes, kernel_size=1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        b = self.bottleneck(self.pool(e4))

        d4 = self.dec4(torch.cat([self.up4(b), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        return self.out(d1)


# --- Training Function ---
def train_model(image_dir, mask_dir, num_classes=10, epochs=20, batch_size=2, lr=1e-4):
    dataset = SegmentationDataset(image_dir, mask_dir)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = UNet(in_channels=3, out_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        running_loss = 0

        for images, masks in loader:
            images, masks = images.to(device), masks.to(device)

            outputs = model(images)
            loss = criterion(outputs, masks)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(loader):.4f}")

    return model


# # --- Prediction + Visualization ---
# ID_TO_COLOR = {
#     0: (0, 0, 0),
#     1: (255, 0, 0),
#     2: (0, 255, 0),
#     3: (0, 0, 255),
#     4: (255, 255, 0),
#     5: (255, 0, 255),
#     6: (0, 255, 255),
#     7: (128, 128, 0),
#     8: (128, 0, 128),
#     9: (0, 128, 128),
# }

# def mask_to_color(mask):
#     h, w = mask.shape
#     color_mask = np.zeros((h, w, 3), dtype=np.uint8)
#     for class_id, color in ID_TO_COLOR.items():
#         color_mask[mask == class_id] = color
#     return color_mask

# def predict_and_visualize(model, image_path):
#     model.eval()

#     image = Image.open(image_path).convert("RGB")
#     original = np.array(image)

#     transform = transforms.Compose([
#         transforms.Resize((256, 256)),
#         transforms.ToTensor(),
#     ])

#     input_tensor = transform(image).unsqueeze(0).to(device)

#     with torch.no_grad():
#         output = model(input_tensor)
#         pred_mask = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()

#     # Resize prediction back to original
#     pred_mask_resized = Image.fromarray(pred_mask.astype(np.uint8)).resize(image.size, Image.NEAREST)
#     pred_mask_resized = np.array(pred_mask_resized)

#     color_mask = mask_to_color(pred_mask_resized)
#     overlay = cv2.addWeighted(original, 0.6, color_mask, 0.4, 0)

#     # Display
#     plt.figure(figsize=(15, 5))
#     plt.subplot(1, 3, 1)
#     plt.imshow(original)
#     plt.title("Original")
#     plt.axis("off")

#     plt.subplot(1, 3, 2)
#     plt.imshow(color_mask)
#     plt.title("Predicted Mask")
#     plt.axis("off")

#     plt.subplot(1, 3, 3)
#     plt.imshow(overlay)
#     plt.title("Overlay")
#     plt.axis("off")
#     plt.tight_layout()
#     plt.show()


# --- Run Everything ---
if __name__ == "__main__":
    image_dir = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_resized_images_v3"
    mask_dir = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_resized_masks_v3"
    
    
    
    num_classes = 11

    # Train model
    model = train_model(image_dir, mask_dir, num_classes=num_classes)

    # # Pick sample image
    # sample_image = sorted(os.listdir(image_dir))[0]
    # sample_image_path = os.path.join(image_dir, sample_image)

    # print(f"🔍 Predicting on: {sample_image_path}")
    # predict_and_visualize(model, sample_image_path)

