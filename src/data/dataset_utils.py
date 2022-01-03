"""This file contains all functions related to the dataset."""
# pylint: disable=import-error
import os
import torch
import torchvision.datasets as datasets

# Load and split training and validation dataset


def find_classes(directory):
    """Finds the class folders in a dataset.

    Args:
        directory (str): Root directory path

    Returns:
        (Tuple[List[str], Dict[str, int]]): Classe and dictionary mapping each class to an index
    """
    cls_name = os.path.basename(directory)
    class_to_idx = {cls_name: int(cls_name[:3])}
    return [cls_name], class_to_idx


def make_dataset(
    directory: str, class_to_idx=None, extensions=None
):  # pylint: disable=too-many-locals
    """Generates a list of samples of a form (path_to_sample, class).

    This can be overridden to e.g. read files from a compressed zip file instead of from the disk.

    Args:
        directory (str): root dataset directory, corresponding to ``self.root``.
        class_to_idx (Dict[str, int]): Dictionary mapping class name to class index.
        extensions (optional): A list of allowed extensions.
            Either extensions or is_valid_file should be passed. Defaults to None.
    Returns:
        List[Tuple[str, int]]: samples of a form (path_to_sample, class)
    """
    directory = os.path.expanduser(directory)

    if class_to_idx is None:
        _, class_to_idx = find_classes(directory)
    elif not class_to_idx:
        raise ValueError(
            "'class_to_index' must have at least one entry to collect any samples."
        )

    instances = []
    available_classes = set()
    for target_class in sorted(class_to_idx.keys()):
        class_index = class_to_idx[target_class]
        target_dir = os.path.join(directory)
        if not os.path.isdir(target_dir):
            continue
        for root, _, fnames in sorted(os.walk(target_dir, followlinks=True)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                item = path, class_index
                instances.append(item)

                if target_class not in available_classes:
                    available_classes.add(target_class)

    empty_classes = set(class_to_idx.keys()) - available_classes
    if empty_classes:
        msg = (
            f"Found no valid file for the classes {', '.join(sorted(empty_classes))}. "
        )
        if extensions is not None:
            msg += f"Supported extensions are: {', '.join(extensions)}"
        raise FileNotFoundError(msg)

    return instances


class ImageFolderReader(datasets.ImageFolder):
    """Load images in a folder."""

    def find_classes(
        self, directory: str
    ):  # pylint: disable=no-self-use, missing-function-docstring
        return find_classes(directory)

    @staticmethod
    def make_dataset(
        directory, class_to_idx, extensions=None, is_valid_file=None
    ):  # pylint: disable=no-self-use, missing-function-docstring, unused-argument
        if class_to_idx is None:
            raise ValueError("The class_to_idx parameter cannot be None.")
        return make_dataset(directory, class_to_idx, extensions=extensions)


def random_split_for_unbalanced_dataset(path_to_train, valid_ratio):
    """This function split each class according to a ratio to create
    validation and training dataset.

    Args:
        path_to_train (str): root directory path.
        valid_ratio (float): ratio of data for validation dataset.

    Returns:
        tuple[List, List]: training and validation datasets.
    """
    train_dataset_list = []
    valid_dataset_list = []

    for name in os.listdir(path_to_train):

        train_valid_dataset = ImageFolderReader(path_to_train + name)

        # Split it into training and validation sets
        nb_train = int((1.0 - valid_ratio) * len(train_valid_dataset))
        nb_valid = len(train_valid_dataset) - nb_train

        temp_train_dataset, temp_valid_dataset = torch.utils.data.dataset.random_split(
            dataset=train_valid_dataset, lengths=[nb_train, nb_valid]
        )

        train_dataset_list.append(temp_train_dataset)
        valid_dataset_list.append(temp_valid_dataset)

    train_dataset = torch.utils.data.ConcatDataset(train_dataset_list)
    valid_dataset = torch.utils.data.ConcatDataset(valid_dataset_list)

    return train_dataset, valid_dataset


def basic_random_split(path_to_train, valid_ratio):
    """This function split each class according to a ratio to create
    validation and training dataset.

    Args:
        path_to_train (str): root directory path.
        valid_ratio (float): ratio of data for validation dataset.

    Returns:
        tuple[List, List]: training and validation datasets.
    """

    train_valid_dataset = datasets.ImageFolder(path_to_train)

    # Split it into training and validation sets
    nb_train = int((1.0 - valid_ratio) * len(train_valid_dataset))
    nb_valid = len(train_valid_dataset) - nb_train

    train_dataset, valid_dataset = torch.utils.data.dataset.random_split(
        dataset=train_valid_dataset, lengths=[nb_train, nb_valid]
    )

    return train_dataset, valid_dataset