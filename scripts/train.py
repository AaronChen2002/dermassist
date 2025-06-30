import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from PIL import Image
import pandas as pd
import logging
from sklearn.preprocessing import LabelEncoder

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
DATA_DIR = "data"
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
MODEL_DIR = "models"
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "dermassist_mobilenet_v2.pt")

# --- Hyperparameters ---
LEARNING_RATE = 0.001
BATCH_SIZE = 32
NUM_EPOCHS = 15
IMAGE_SIZE = 224

# Ensure the models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# --- Dataset Definition ---
class SkinLesionDataset(Dataset):
    """Custom dataset for HAM10000 skin lesions."""
    def __init__(self, csv_file, root_dir, transform=None):
        self.annotations = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform
        
        # Encode labels
        self.annotations['dx'] = LabelEncoder().fit_transform(self.annotations['dx'])

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        img_id = self.annotations.iloc[index]['image_id']
        # The images are in two subfolders. We need to check both.
        img_path_1 = os.path.join(self.root_dir, "HAM10000_images_part_1", f"{img_id}.jpg")
        img_path_2 = os.path.join(self.root_dir, "HAM10000_images_part_2", f"{img_id}.jpg")
        
        img_path = img_path_1 if os.path.exists(img_path_1) else img_path_2
        
        image = Image.open(img_path).convert("RGB")
        label = torch.tensor(int(self.annotations.iloc[index]['dx']))

        if self.transform:
            image = self.transform(image)

        return image, label

# --- Data Augmentation and Transforms ---
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# --- Dataloaders ---
def get_dataloaders():
    """Creates and returns the training and validation dataloaders."""
    logging.info("Loading datasets...")
    train_dataset = SkinLesionDataset(
        csv_file=os.path.join(PROCESSED_DATA_DIR, "train.csv"),
        root_dir=RAW_DATA_DIR,
        transform=data_transforms['train']
    )
    val_dataset = SkinLesionDataset(
        csv_file=os.path.join(PROCESSED_DATA_DIR, "val.csv"),
        root_dir=RAW_DATA_DIR,
        transform=data_transforms['val']
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    
    return train_loader, val_loader

# --- Model Definition ---
def get_model(num_classes=7):
    """Initializes a pretrained MobileNetV2 model and adapts it for our classification task."""
    logging.info("Initializing MobileNetV2 model...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    
    # Freeze all the parameters in the pre-trained model
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace the classifier with a new one for our specific number of classes
    model.classifier[1] = nn.Sequential(
        nn.Linear(model.last_channel, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, num_classes)
    )
    return model

# --- Training Loop ---
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=NUM_EPOCHS):
    """The main training and validation loop."""
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    best_val_acc = 0.0

    for epoch in range(num_epochs):
        logging.info(f"Epoch {epoch+1}/{num_epochs}")
        
        # --- Training Phase ---
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = running_corrects.double() / len(train_loader.dataset)
        logging.info(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
        
        # --- Validation Phase ---
        model.eval()
        val_running_loss = 0.0
        val_running_corrects = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                val_running_loss += loss.item() * inputs.size(0)
                val_running_corrects += torch.sum(preds == labels.data)

        val_epoch_loss = val_running_loss / len(val_loader.dataset)
        val_epoch_acc = val_running_corrects.double() / len(val_loader.dataset)
        logging.info(f"Val Loss: {val_epoch_loss:.4f} Acc: {val_epoch_acc:.4f}")

        # Save the model if it has the best validation accuracy so far
        if val_epoch_acc > best_val_acc:
            best_val_acc = val_epoch_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            logging.info(f"Best model saved to {MODEL_SAVE_PATH} with accuracy: {best_val_acc:.4f}")
            
    logging.info("Training complete.")

def main():
    """Main function to run the training process."""
    train_loader, val_loader = get_dataloaders()
    
    # There are 7 classes in the HAM10000 dataset
    model = get_model(num_classes=7)
    
    criterion = nn.CrossEntropyLoss()
    
    # We only want to train the parameters of the new classifier
    optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)
    
    train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=NUM_EPOCHS)

if __name__ == "__main__":
    main()
