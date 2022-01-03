"""This module aims to load and process the data."""
# pylint: disable=import-error
import argparse
import os
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import yaml

from torch.utils.data import DataLoader

from preprocessing import DatasetTransformer, apply_preprocessing
from dataset_utils import random_split_for_unbalanced_dataset, basic_random_split


def main(cfg):
    """Main function to call to load and process data

    Args:
        cfg (dict): configuration file

    Returns:
        tuple[DataLoader, DataLoader, DataLoader]: train, validation and test DataLoader
    """
    # Set path
    path_to_train = os.path.join(cfg["DATA_DIR"], "train/")
    path_to_test = os.path.join(cfg["DATA_DIR"], "test/")

    # Load the dataset for the training/validation sets
    if cfg["DATASET"]["SMART_SPLIT"]:
        train_dataset, valid_dataset = random_split_for_unbalanced_dataset(
            path_to_train=path_to_train, valid_ratio=cfg["DATASET"]["VALID_RATIO"]
        )
    else:
        train_dataset, valid_dataset = basic_random_split(
            path_to_train=path_to_train, valid_ratio=cfg["DATASET"]["VALID_RATIO"]
        )

    # Load the test set
    test_dataset = datasets.ImageFolder(path_to_test)

    # DatasetTransformer
    data_transforms = apply_preprocessing(cfg=cfg["DATASET"]["PREPROCESSING"])

    train_dataset = DatasetTransformer(
        train_dataset, transforms.Compose(data_transforms["train"])
    )
    valid_dataset = DatasetTransformer(
        valid_dataset, transforms.Compose(data_transforms["valid"])
    )
    test_dataset = DatasetTransformer(
        test_dataset, transforms.Compose(data_transforms["test"])
    )

    # Dataloaders
    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=cfg["DATASET"]["BATCH_SIZE"],
        shuffle=True,
        num_workers=cfg["DATASET"]["NUM_THREADS"],
    )

    valid_loader = DataLoader(
        dataset=valid_dataset,
        batch_size=cfg["DATASET"]["BATCH_SIZE"],
        shuffle=False,
        num_workers=cfg["DATASET"]["NUM_THREADS"],
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=cfg["DATASET"]["BATCH_SIZE"],
        shuffle=False,
        num_workers=cfg["DATASET"]["NUM_THREADS"],
    )

    if cfg["DATASET"]["VERBOSITY"]:
        print(
            f"The train set contains {len(train_loader.dataset)} images,"
            f" in {len(train_loader)} batches"
        )
        print(
            f"The validation set contains {len(valid_loader.dataset)} images,"
            f" in {len(valid_loader)} batches"
        )
        print(
            f"The test set contains {len(test_loader.dataset)} images,"
            f" in {len(test_loader)} batches"
        )

    return train_loader, valid_loader, test_loader


if __name__ == "__main__":
    # Init the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    # Add path to config file to the command line arguments
    parser.add_argument(
        "--path_to_config", type=str, required=True, help="path to config file"
    )

    # Parse arguments
    args = parser.parse_args()

    with open(args.path_to_config, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.CFullLoader)
    main(cfg=config)
