import os
import subprocess
import pandas as pd
from sklearn.model_selection import train_test_split
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
DATASET_NAME = "kmader/skin-cancer-mnist-ham10000"
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
ZIP_FILE_PATH = os.path.join(DATA_DIR, "skin-cancer-mnist-ham10000.zip")
METADATA_FILE = os.path.join(RAW_DATA_DIR, "HAM10000_metadata.csv")


def setup_directories():
    """Create necessary directories if they don't exist."""
    logging.info("Setting up directories...")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    logging.info("Directory setup complete.")


def download_data():
    """Downloads the HAM10000 dataset using the Kaggle CLI."""
    if os.path.exists(ZIP_FILE_PATH):
        logging.info("Dataset zip file already exists. Skipping download.")
        return

    logging.info(f"Downloading dataset '{DATASET_NAME}' from Kaggle...")
    command = [
        "kaggle", "datasets", "download",
        "-d", DATASET_NAME,
        "-p", DATA_DIR,
        "--unzip"
    ]

    try:
        # Before downloading, let's move the unzipped files to a raw directory
        # The --unzip flag from kaggle cli will extract to the -p path.
        # We will restructure it after.
        subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info("Dataset downloaded and unzipped successfully.")
        restructure_unzipped_files()
    except FileNotFoundError:
        logging.error("Kaggle CLI not found. Please ensure it's installed and in your PATH.")
        exit()
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download dataset. Error: {e.stderr}")
        exit()

def restructure_unzipped_files():
    """
    Moves the unzipped files from the data directory to the raw data directory.
    The kaggle cli unzips everything into the directory specified by -p, so we clean it up.
    """
    logging.info("Restructuring unzipped files...")
    files_to_move = [f for f in os.listdir(DATA_DIR) if not f.endswith('.zip') and os.path.isfile(os.path.join(DATA_DIR, f))]
    image_dirs_to_move = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d)) and d not in ['raw', 'processed']]

    for file_name in files_to_move:
        os.rename(os.path.join(DATA_DIR, file_name), os.path.join(RAW_DATA_DIR, file_name))
    
    for dir_name in image_dirs_to_move:
        os.rename(os.path.join(DATA_DIR, dir_name), os.path.join(RAW_DATA_DIR, dir_name))
    
    # The zip file is downloaded anyway, let's move it too.
    if os.path.exists(f"{DATASET_NAME.split('/')[1]}.zip"):
         os.rename(f"{DATASET_NAME.split('/')[1]}.zip", ZIP_FILE_PATH)

    logging.info("File restructuring complete.")


def create_splits():
    """
    Reads the metadata, creates stratified train/validation splits,
    and saves them as CSV files.
    """
    if os.path.exists(os.path.join(PROCESSED_DATA_DIR, "train.csv")) and os.path.exists(os.path.join(PROCESSED_DATA_DIR, "val.csv")):
        logging.info("Train/validation splits already exist. Skipping creation.")
        return

    logging.info("Creating train/validation splits...")
    try:
        df = pd.read_csv(METADATA_FILE)
    except FileNotFoundError:
        logging.error(f"Metadata file not found at '{METADATA_FILE}'. Make sure download was successful.")
        return

    # Stratify by lesion type ('dx') to ensure balanced classes in splits
    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df['dx']
    )

    train_csv_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    val_csv_path = os.path.join(PROCESSED_DATA_DIR, "val.csv")

    train_df.to_csv(train_csv_path, index=False)
    val_df.to_csv(val_csv_path, index=False)

    logging.info(f"Train split ({len(train_df)} samples) saved to '{train_csv_path}'")
    logging.info(f"Validation split ({len(val_df)} samples) saved to '{val_csv_path}'")


def main():
    """Main execution function to prepare all data."""
    setup_directories()
    download_data()
    create_splits()
    logging.info("Data preparation complete.")


if __name__ == "__main__":
    main()
