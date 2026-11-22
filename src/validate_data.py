from __future__ import annotations

import json
from pathlib import Path
from PIL import Image
#
import typing

EXPECTED_SPLITS = {"train": 1034, "validation": 133, "test": 128}
EXPECTED_CLASSES = {"angular_leaf_spot", "bean_rust", "healthy"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# These typed dict classes allows working with dicts know what there is inside
# I absolutely hate treating python like it was simply ugly javascript. 
# If the function was not used in other places, I would use data classes instead. 
class validate_dataset_result_split_class_object(typing.TypedDict):
    images: int
    class_counts: typing.Mapping[str, int]

class validate_dataset_result_object(typing.TypedDict):
    status: typing.Literal["PASS"]
    classes: typing.Sequence[str]
    splits: typing.Mapping[str, validate_dataset_result_split_class_object]
    total_images: int # because it is the sum of expected counts, so it is expected too

def validate_dataset(raw_root: Path) -> validate_dataset_result_object:
    """Validate the raw dataset and return a deterministic quality report.

    Required Core checks:
      1. required splits exist;
      2. exactly the expected classes exist in every split;
      3. expected image counts are present;
      4. every image can be fully decoded by Pillow (`Image.load()` or equivalent);
      5. no split or class is empty.
    """
    
    # if this is not a directory, it will raise an error as well
    if not set(path.name for path in raw_root.iterdir()).issuperset(EXPECTED_SPLITS.keys()):
        raise FileNotFoundError("missing split in data")
    
    all_images: dict[str, dict[str, dict[str, Image.Image]]] = {}
    
    for split_name in EXPECTED_SPLITS.keys():
        split_path = raw_root / split_name
        
        if not set(path.name for path in split_path.iterdir()) == EXPECTED_CLASSES:
            raise FileNotFoundError(f"bad classes for split {split_name}")
        
        split_images: dict[str, dict[str, Image.Image]] = {}
        
        for class_name in EXPECTED_CLASSES:
            class_images: dict[str, Image.Image] = {}
            class_path = split_path / class_name
            
            for image_path in class_path.iterdir():
                class_images[image_path.name] = (img:=Image.open(image_path))
                
                img.load() # ensures that all pixels can be read
            
            if len(class_images) == 0:
                raise FileNotFoundError(f"empty class : {split_name}>{class_name}")
            
            split_images[class_name] = class_images
        
        total_split_images_count = sum(len(split_images[class_name]) for class_name in EXPECTED_CLASSES)
        if total_split_images_count != EXPECTED_SPLITS[split_name]:
            raise RuntimeError(f"images count does not match for split {split_name}, expected {EXPECTED_SPLITS[split_name]}, got {total_split_images_count}")

        all_images[split_name] = split_images
    
    return {
        "status": "PASS",
        "classes": list(EXPECTED_CLASSES),
        "splits": {
            split_name: {
                "images": EXPECTED_SPLITS[split_name],
                "class_counts": {
                    class_name: len(all_images[split_name][class_name])
                    for class_name in EXPECTED_CLASSES
                }
            }
            
            for split_name in EXPECTED_SPLITS.keys()
        },
        "total_images": sum(sum(len(all_images[split_name][class_name]) for class_name in EXPECTED_CLASSES) for split_name in EXPECTED_SPLITS.keys())
    }
    

def main() -> None:
    report = validate_dataset(Path("data/raw"))
    Path("reports").mkdir(exist_ok=True)
    Path("reports/data_quality.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
