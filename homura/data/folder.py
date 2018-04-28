from typing import Iterable, Dict
from pathlib import Path
from multiprocessing import Pool, cpu_count
from PIL import Image

import torch.utils.data as data


def has_allowed_extension(file: Path, extensions: Iterable[str]):
    return file.suffix.lower() in extensions


def find_classes(root: Path):
    classes = [d for d in root.iterdir() if d.is_dir()]
    classes.sort()
    class_to_idx = {d: i for i, d in enumerate(classes)}
    return classes, class_to_idx


def make_dataset(root: Path, class_to_idx: Dict[str, int], extensions: Iterable[str]):
    images = []
    for d in [d for d in root.iterdir() if d.is_dir()]:
        for f in [f for f in d.iterdir() if has_allowed_extension(f, extensions)]:
            images.append((d / f, class_to_idx[d]))
    return images


class ImageFolder(data.Dataset):
    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif']

    def __init__(self, root, transform=None, on_memory=False):
        classes, class_to_idx = find_classes(root)
        samples = make_dataset(root, class_to_idx, self.IMG_EXTENSIONS)
        if len(samples) == 0:
            raise RuntimeError(f"Found 0 image in subdirectories of {root}.")

        self.root = root
        self.classes = classes
        self.class_to_index = class_to_idx
        self.samples = samples
        self.length = len(self.samples)
        self.transforms = transform
        self.on_memory = on_memory

    def __getitem__(self, index):
        img, target = self.samples[index]
        if isinstance(img, Path):
            img, target = self.image_loader((img, target))
            self.samples[index] = (img, target)

        if self.transforms is not None:
            img = self.transforms(img)

        return img, target

    def __len__(self):
        return self.length

    @staticmethod
    def image_loader(args):
        path, idx = args
        with open(path, 'rb') as f:
            return Image.open(f).convert("RGB"), idx