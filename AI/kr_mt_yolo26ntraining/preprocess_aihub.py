"""Convert the selected AI Hub wildfire dataset to Ultralytics YOLO format.

The source images and JSON annotations are treated as read-only. The converter
creates a new dataset with two target classes that match the existing AI branch
terminology:

    0: fire
    1: smoke

Cloud, fog/haze, and chimney-smoke annotations are intentionally removed while
their images remain in the dataset as hard-negative/background samples.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - environment-specific guard
    raise SystemExit(
        "Pillow is required. Install dependencies in the approved AI environment first."
    ) from exc


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = {0: "fire", 1: "smoke"}


def normalize_source_class(name: str) -> str:
    """Normalize insignificant spacing and separator differences in class names."""

    return "".join(str(name).strip().lower().split()).replace("·", "/")


SOURCE_CLASS_TO_TARGET = {
    normalize_source_class("화염"): 0,
    normalize_source_class("흑색연기"): 1,
    normalize_source_class("백색/회색연기"): 1,
}
IGNORED_SOURCE_CLASSES = {
    normalize_source_class("구름"),
    normalize_source_class("안개/연무"),
    normalize_source_class("굴뚝연기"),
}


class DataPreparationError(RuntimeError):
    """Raised when source data is unsafe to convert or train on."""


@dataclass(frozen=True)
class YoloBox:
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float

    def as_line(self) -> str:
        return (
            f"{self.class_id} {self.x_center:.8f} {self.y_center:.8f} "
            f"{self.width:.8f} {self.height:.8f}"
        )


@dataclass(frozen=True)
class ConvertedSample:
    split: str
    image_path: Path
    annotation_path: Path
    source_group: str
    source_folder: str
    width: int
    height: int
    boxes: tuple[YoloBox, ...]
    source_annotation_counts: tuple[tuple[str, int], ...]
    ignored_annotation_counts: tuple[tuple[str, int], ...]
    metadata_warnings: tuple[str, ...]

    @property
    def target_count(self) -> int:
        return len(self.boxes)


def bbox_xywh_to_yolo(
    bbox: Iterable[float], image_width: int, image_height: int
) -> tuple[float, float, float, float]:
    """Convert an absolute COCO xywh box to normalized YOLO xywh."""

    values = list(bbox)
    if len(values) != 4:
        raise DataPreparationError(f"bbox must have four values, got: {values!r}")
    try:
        x, y, width, height = (float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise DataPreparationError(f"bbox contains a non-numeric value: {values!r}") from exc

    if image_width <= 0 or image_height <= 0:
        raise DataPreparationError(
            f"invalid image dimensions: {image_width}x{image_height}"
        )
    if width <= 0 or height <= 0:
        raise DataPreparationError(f"bbox width and height must be positive: {values!r}")

    epsilon = 1e-4
    if (
        x < -epsilon
        or y < -epsilon
        or x + width > image_width + epsilon
        or y + height > image_height + epsilon
    ):
        raise DataPreparationError(
            f"bbox is outside {image_width}x{image_height}: {values!r}"
        )

    x_center = (x + width / 2.0) / image_width
    y_center = (y + height / 2.0) / image_height
    normalized_width = width / image_width
    normalized_height = height / image_height
    normalized = (x_center, y_center, normalized_width, normalized_height)
    if not all(0.0 <= value <= 1.0 for value in normalized):
        raise DataPreparationError(f"normalized bbox is outside [0, 1]: {normalized!r}")
    return normalized


def discover_images(root: Path) -> list[Path]:
    images = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not images:
        raise DataPreparationError(f"no images found under: {root}")
    return images


def build_annotation_index(
    annotation_root: Path, wanted_stems: set[str]
) -> dict[str, Path]:
    """Index only annotations needed by the selected image set."""

    index: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}
    for annotation_path in annotation_root.rglob("*.json"):
        stem = annotation_path.stem
        if stem not in wanted_stems:
            continue
        if stem in index:
            duplicates.setdefault(stem, [index[stem]]).append(annotation_path)
        else:
            index[stem] = annotation_path

    if duplicates:
        examples = "\n".join(
            f"  {stem}: {', '.join(str(path) for path in paths)}"
            for stem, paths in list(duplicates.items())[:10]
        )
        raise DataPreparationError(
            f"duplicate JSON annotations found for {len(duplicates)} images:\n{examples}"
        )

    missing = sorted(wanted_stems - set(index))
    if missing:
        examples = "\n".join(f"  {stem}.json" for stem in missing[:20])
        raise DataPreparationError(
            f"missing JSON annotations for {len(missing)} images. "
            f"Do not treat these images as backgrounds. Examples:\n{examples}"
        )
    return index


def _load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataPreparationError(f"cannot read annotation JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DataPreparationError(f"annotation root must be an object: {path}")
    return data


def _actual_image_size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            size = image.size
            image.verify()
    except (OSError, ValueError) as exc:
        raise DataPreparationError(f"invalid or corrupt image: {path}: {exc}") from exc
    return size


def _source_group(annotation: dict, image_stem: str) -> str:
    info = annotation.get("info") or {}
    environment = annotation.get("environment") or {}
    filename_parts = image_stem.rsplit("_", 2)
    fuel = filename_parts[-2] if len(filename_parts) >= 3 else "unknown"
    address = str(environment.get("address") or "unknown")
    camera_id = str(info.get("camera_id") or "unknown")
    video_id = str(info.get("video_id") or "unknown")
    return "|".join((address, camera_id, video_id, fuel))


def convert_sample(
    image_path: Path,
    annotation_path: Path,
    image_root: Path,
    split: str,
) -> ConvertedSample:
    annotation = _load_json(annotation_path)
    actual_width, actual_height = _actual_image_size(image_path)

    image_entries = annotation.get("images")
    if not isinstance(image_entries, list) or len(image_entries) != 1:
        raise DataPreparationError(
            f"expected exactly one images entry in {annotation_path}, got {image_entries!r}"
        )
    image_entry = image_entries[0]
    json_width = int(image_entry.get("width", 0))
    json_height = int(image_entry.get("height", 0))
    json_filename = Path(str(image_entry.get("file_name", ""))).stem
    metadata_warnings: list[str] = []
    if json_filename != image_path.stem:
        if annotation_path.stem != image_path.stem:
            raise DataPreparationError(
                f"image/JSON filename mismatch: {image_path.name} vs "
                f"{image_entry.get('file_name')!r}"
            )
        metadata_warnings.append(
            f"internal file_name typo: {image_entry.get('file_name')!r}"
        )
    if (actual_width, actual_height) != (json_width, json_height):
        raise DataPreparationError(
            f"image/JSON size mismatch for {image_path.name}: "
            f"actual={actual_width}x{actual_height}, JSON={json_width}x{json_height}"
        )

    categories = annotation.get("categories")
    if not isinstance(categories, list):
        raise DataPreparationError(f"categories must be a list: {annotation_path}")
    category_names: dict[int, str] = {}
    for category in categories:
        try:
            category_id = int(category["id"])
            category_name = str(category["name"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DataPreparationError(
                f"invalid category in {annotation_path}: {category!r}"
            ) from exc
        category_names[category_id] = category_name

    annotations = annotation.get("annotations")
    if not isinstance(annotations, list):
        raise DataPreparationError(f"annotations must be a list: {annotation_path}")

    boxes: list[YoloBox] = []
    raw_counts: Counter[str] = Counter()
    ignored_counts: Counter[str] = Counter()
    for item in annotations:
        try:
            source_class = category_names[int(item["category_id"])]
            bbox = item["bbox"]
        except (KeyError, TypeError, ValueError) as exc:
            raise DataPreparationError(
                f"invalid annotation in {annotation_path}: {item!r}"
            ) from exc

        normalized_source_class = normalize_source_class(source_class)
        raw_counts[source_class] += 1
        if normalized_source_class in IGNORED_SOURCE_CLASSES:
            ignored_counts[source_class] += 1
            continue
        if normalized_source_class not in SOURCE_CLASS_TO_TARGET:
            raise DataPreparationError(
                f"unmapped source class {source_class!r} in {annotation_path}"
            )

        class_id = SOURCE_CLASS_TO_TARGET[normalized_source_class]
        x_center, y_center, width, height = bbox_xywh_to_yolo(
            bbox, actual_width, actual_height
        )
        boxes.append(YoloBox(class_id, x_center, y_center, width, height))

    relative_parts = image_path.relative_to(image_root).parts
    source_folder = relative_parts[0] if len(relative_parts) > 1 else image_path.parent.name
    return ConvertedSample(
        split=split,
        image_path=image_path,
        annotation_path=annotation_path,
        source_group=_source_group(annotation, image_path.stem),
        source_folder=source_folder,
        width=actual_width,
        height=actual_height,
        boxes=tuple(boxes),
        source_annotation_counts=tuple(sorted(raw_counts.items())),
        ignored_annotation_counts=tuple(sorted(ignored_counts.items())),
        metadata_warnings=tuple(metadata_warnings),
    )


def prepare_split(
    split: str, image_root: Path, annotation_root: Path
) -> list[ConvertedSample]:
    image_paths = discover_images(image_root)
    stems: dict[str, Path] = {}
    duplicate_stems: list[tuple[str, Path, Path]] = []
    for path in image_paths:
        if path.stem in stems:
            duplicate_stems.append((path.stem, stems[path.stem], path))
        else:
            stems[path.stem] = path
    if duplicate_stems:
        examples = "\n".join(
            f"  {stem}: {first} / {second}"
            for stem, first, second in duplicate_stems[:10]
        )
        raise DataPreparationError(
            f"duplicate image stems found in {split}: {len(duplicate_stems)}\n{examples}"
        )

    annotation_index = build_annotation_index(annotation_root, set(stems))
    records: list[ConvertedSample] = []
    errors: list[str] = []
    for index, image_path in enumerate(image_paths, start=1):
        try:
            records.append(
                convert_sample(
                    image_path,
                    annotation_index[image_path.stem],
                    image_root,
                    split,
                )
            )
        except DataPreparationError as exc:
            errors.append(str(exc))
        if index % 5000 == 0:
            print(f"[{split}] validated {index}/{len(image_paths)} images", flush=True)

    if errors:
        examples = "\n".join(f"  {error}" for error in errors[:20])
        raise DataPreparationError(
            f"{split} contains {len(errors)} invalid samples. Examples:\n{examples}"
        )
    return records


def summarize(records: list[ConvertedSample]) -> dict:
    class_counts: Counter[str] = Counter()
    raw_counts: Counter[str] = Counter()
    ignored_counts: Counter[str] = Counter()
    source_folders: Counter[str] = Counter()
    backgrounds = 0
    metadata_warning_examples: list[str] = []
    metadata_warning_count = 0
    for record in records:
        source_folders[record.source_folder] += 1
        if not record.boxes:
            backgrounds += 1
        for box in record.boxes:
            class_counts[CLASS_NAMES[box.class_id]] += 1
        raw_counts.update(dict(record.source_annotation_counts))
        ignored_counts.update(dict(record.ignored_annotation_counts))
        metadata_warning_count += len(record.metadata_warnings)
        for warning in record.metadata_warnings:
            if len(metadata_warning_examples) < 20:
                metadata_warning_examples.append(f"{record.image_path.name}: {warning}")

    return {
        "images": len(records),
        "background_images": backgrounds,
        "target_objects": sum(class_counts.values()),
        "target_class_counts": dict(sorted(class_counts.items())),
        "source_annotation_counts": dict(sorted(raw_counts.items())),
        "ignored_annotation_counts": dict(sorted(ignored_counts.items())),
        "source_folder_counts": dict(sorted(source_folders.items())),
        "unique_source_groups": len({record.source_group for record in records}),
        "metadata_warning_count": metadata_warning_count,
        "metadata_warning_examples": metadata_warning_examples,
    }


def resolve_cross_split(
    train: list[ConvertedSample],
    val: list[ConvertedSample],
    overlap_policy: str,
) -> tuple[list[ConvertedSample], dict]:
    """Reject duplicate files and resolve same-sequence validation leakage."""

    train_stems = {record.image_path.stem for record in train}
    val_stems = {record.image_path.stem for record in val}
    duplicate_stems = sorted(train_stems & val_stems)
    if duplicate_stems:
        examples = "\n".join(f"  {stem}" for stem in duplicate_stems[:20])
        raise DataPreparationError(
            f"train/val contain {len(duplicate_stems)} duplicate image names:\n{examples}"
        )

    train_groups = {record.source_group for record in train}
    val_groups = {record.source_group for record in val}
    overlapping_groups = sorted(train_groups & val_groups)
    overlapping_group_set = set(overlapping_groups)
    overlapping_val = [
        record for record in val if record.source_group in overlapping_group_set
    ]
    report = {
        "overlap_policy": overlap_policy,
        "overlapping_source_groups": len(overlapping_groups),
        "excluded_val_images": 0,
        "retained_val_images": len(val),
        "overlap_examples": overlapping_groups[:20],
    }

    if overlapping_groups and overlap_policy == "error":
        examples = "\n".join(f"  {group}" for group in overlapping_groups[:20])
        raise DataPreparationError(
            f"train/val source leakage: {len(overlapping_groups)} source groups overlap. "
            f"Examples:\n{examples}"
        )

    if overlapping_groups and overlap_policy == "exclude":
        val = [
            record for record in val if record.source_group not in overlapping_group_set
        ]
        report["excluded_val_images"] = len(overlapping_val)
        report["retained_val_images"] = len(val)
        report["excluded_val_examples"] = [
            str(record.image_path) for record in overlapping_val[:20]
        ]
        print(
            "[val] excluded "
            f"{len(overlapping_val)} images from {len(overlapping_groups)} source groups "
            "that also occur in train",
            flush=True,
        )

    return val, report


def ensure_new_output_directory(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise DataPreparationError(
            f"output directory is not empty: {output_dir}. Use a new directory to avoid "
            "overwriting a previous dataset."
        )


def _copy_or_link(source: Path, destination: Path, mode: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "hardlink":
        os.link(source, destination)
    else:
        shutil.copy2(source, destination)


def _write_data_yaml(output_dir: Path) -> Path:
    yaml_path = output_dir / "data.yaml"
    root = output_dir.resolve().as_posix()
    yaml_path.write_text(
        "\n".join(
            [
                f'path: "{root}"',
                "train: images/train",
                "val: images/val",
                "",
                "names:",
                "  0: fire",
                "  1: smoke",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return yaml_path


def _write_manifest(output_dir: Path, records: list[ConvertedSample]) -> None:
    manifest_path = output_dir / "reports" / "manifest.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "source_image",
                "source_annotation",
                "source_folder",
                "source_group",
                "width",
                "height",
                "target_boxes",
                "is_background",
                "metadata_warnings",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "split": record.split,
                    "source_image": str(record.image_path),
                    "source_annotation": str(record.annotation_path),
                    "source_folder": record.source_folder,
                    "source_group": record.source_group,
                    "width": record.width,
                    "height": record.height,
                    "target_boxes": record.target_count,
                    "is_background": not record.boxes,
                    "metadata_warnings": " | ".join(record.metadata_warnings),
                }
            )


def _draw_visualization(
    image_path: Path, boxes: tuple[YoloBox, ...], destination: Path
) -> None:
    colors = {0: "#ff3030", 1: "#ff9500"}
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for box in boxes:
        x1 = (box.x_center - box.width / 2.0) * width
        y1 = (box.y_center - box.height / 2.0) * height
        x2 = (box.x_center + box.width / 2.0) * width
        y2 = (box.y_center + box.height / 2.0) * height
        color = colors[box.class_id]
        draw.rectangle((x1, y1, x2, y2), outline=color, width=max(2, width // 500))
        draw.text((x1 + 3, max(0, y1 - 14)), CLASS_NAMES[box.class_id], fill=color)
    if not boxes:
        draw.rectangle((0, 0, width - 1, height - 1), outline="#00aa55", width=3)
        draw.text((8, 8), "background / hard negative", fill="#00aa55")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.thumbnail((1600, 1600))
    image.save(destination, quality=90)


def materialize(
    output_dir: Path,
    records: list[ConvertedSample],
    cross_split_report: dict,
    mode: str,
    visualization_count: int,
    seed: int,
) -> None:
    ensure_new_output_directory(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, record in enumerate(records, start=1):
        image_destination = output_dir / "images" / record.split / record.image_path.name
        label_destination = output_dir / "labels" / record.split / f"{record.image_path.stem}.txt"
        _copy_or_link(record.image_path, image_destination, mode)
        label_destination.parent.mkdir(parents=True, exist_ok=True)
        label_text = "\n".join(box.as_line() for box in record.boxes)
        if label_text:
            label_text += "\n"
        label_destination.write_text(label_text, encoding="utf-8")
        if index % 5000 == 0:
            print(f"materialized {index}/{len(records)} images", flush=True)

    _write_data_yaml(output_dir)
    _write_manifest(output_dir, records)
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    summaries = {
        split: summarize([record for record in records if record.split == split])
        for split in ("train", "val")
    }
    summaries["cross_split"] = cross_split_report
    (reports_dir / "preprocess_report.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if visualization_count > 0:
        rng = random.Random(seed)
        for split in ("train", "val"):
            candidates = [record for record in records if record.split == split]
            selected = rng.sample(candidates, min(visualization_count, len(candidates)))
            for record in selected:
                destination = (
                    reports_dir
                    / "visualizations"
                    / split
                    / f"{record.image_path.stem}_boxes.jpg"
                )
                _draw_visualization(record.image_path, record.boxes, destination)


def _resolved(path: str) -> Path:
    return Path(path).expanduser().resolve()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert AI Hub wildfire JSON annotations to YOLO26 detection format."
    )
    parser.add_argument("--train-images", required=True, help="Selected Training image root")
    parser.add_argument("--train-labels", required=True, help="Training JSON annotation root")
    parser.add_argument("--val-images", required=True, help="AI Hub Validation image root")
    parser.add_argument("--val-labels", required=True, help="Validation JSON annotation root")
    parser.add_argument("--output-dir", required=True, help="New YOLO dataset directory")
    parser.add_argument(
        "--mode",
        choices=("copy", "hardlink"),
        default="copy",
        help="Copy images (safe default) or create same-volume hard links",
    )
    parser.add_argument(
        "--visualize",
        type=int,
        default=24,
        metavar="N",
        help="Save N deterministic box visualizations per split",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--val-overlap-policy",
        choices=("exclude", "error"),
        default="exclude",
        help=(
            "Exclude official Validation images from source sequences also present in "
            "train (safe default), or stop with an error"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print statistics without creating output files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    train_images = _resolved(args.train_images)
    train_labels = _resolved(args.train_labels)
    val_images = _resolved(args.val_images)
    val_labels = _resolved(args.val_labels)
    output_dir = _resolved(args.output_dir)

    for label, path in (
        ("train images", train_images),
        ("train labels", train_labels),
        ("val images", val_images),
        ("val labels", val_labels),
    ):
        if not path.is_dir():
            raise DataPreparationError(f"{label} directory does not exist: {path}")

    for source_root in (train_images, train_labels, val_images, val_labels):
        if output_dir == source_root or output_dir.is_relative_to(source_root):
            raise DataPreparationError(
                f"output must not be inside a source directory: {output_dir}"
            )

    print("[train] indexing and validating source data", flush=True)
    train_records = prepare_split("train", train_images, train_labels)
    print("[val] indexing and validating source data", flush=True)
    val_records = prepare_split("val", val_images, val_labels)
    val_records, cross_split_report = resolve_cross_split(
        train_records, val_records, args.val_overlap_policy
    )

    summaries = {
        "train": summarize(train_records),
        "val": summarize(val_records),
        "cross_split": cross_split_report,
    }
    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    for split in ("train", "val"):
        summary = summaries[split]
        class_counts = summary["target_class_counts"]
        missing_classes = [name for name in CLASS_NAMES.values() if class_counts.get(name, 0) == 0]
        if missing_classes:
            raise DataPreparationError(
                f"{split} has no objects for required classes: {', '.join(missing_classes)}"
            )

    if args.dry_run:
        print("dry-run complete: no output files were created")
        return 0

    materialize(
        output_dir,
        train_records + val_records,
        cross_split_report,
        args.mode,
        args.visualize,
        args.seed,
    )
    print(f"YOLO dataset created: {output_dir}")
    print(f"dataset config: {output_dir / 'data.yaml'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DataPreparationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
