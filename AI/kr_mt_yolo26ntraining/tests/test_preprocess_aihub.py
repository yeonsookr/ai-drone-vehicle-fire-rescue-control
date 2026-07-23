from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from AI.yolo26.preprocess_aihub import (
    ConvertedSample,
    DataPreparationError,
    bbox_xywh_to_yolo,
    convert_sample,
    normalize_source_class,
    resolve_cross_split,
)


class PreprocessAiHubTest(unittest.TestCase):
    @staticmethod
    def _sample(split: str, stem: str, source_group: str) -> ConvertedSample:
        return ConvertedSample(
            split=split,
            image_path=Path(f"/{split}/{stem}.jpg"),
            annotation_path=Path(f"/{split}/{stem}.json"),
            source_group=source_group,
            source_folder="fixture",
            width=100,
            height=50,
            boxes=(),
            source_annotation_counts=(),
            ignored_annotation_counts=(),
            metadata_warnings=(),
        )

    def test_bbox_xywh_to_yolo(self) -> None:
        self.assertEqual(
            bbox_xywh_to_yolo([10, 20, 20, 10], 100, 50),
            (0.2, 0.5, 0.2, 0.2),
        )

    def test_bbox_outside_image_is_rejected(self) -> None:
        with self.assertRaises(DataPreparationError):
            bbox_xywh_to_yolo([90, 10, 20, 10], 100, 50)

    def test_class_name_normalization(self) -> None:
        self.assertEqual(
            normalize_source_class(" 백색 · 회색 연기 "),
            normalize_source_class("백색/회색연기"),
        )

    def test_convert_sample_maps_targets_and_drops_confusers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_root = root / "images"
            image_dir = image_root / "selected"
            image_dir.mkdir(parents=True)
            image_path = image_dir / "sample.jpg"
            Image.new("RGB", (100, 50), "white").save(image_path)

            annotation_path = root / "sample.json"
            annotation = {
                "info": {"camera_id": "CAM-1", "video_id": "V-1"},
                "environment": {"address": "site"},
                "categories": [
                    {"id": 1, "name": "화염"},
                    {"id": 2, "name": "백색/회색연기"},
                    {"id": 4, "name": "구름"},
                ],
                "images": [
                    {"id": 1, "width": 100, "height": 50, "file_name": "sample.jpg"}
                ],
                "annotations": [
                    {"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 20, 10]},
                    {"id": 2, "image_id": 1, "category_id": 2, "bbox": [40, 10, 20, 20]},
                    {"id": 3, "image_id": 1, "category_id": 4, "bbox": [0, 0, 100, 20]},
                ],
            }
            annotation_path.write_text(
                json.dumps(annotation, ensure_ascii=False), encoding="utf-8"
            )

            sample = convert_sample(
                image_path, annotation_path, image_root, split="train"
            )
            self.assertEqual([box.class_id for box in sample.boxes], [0, 1])
            self.assertEqual(dict(sample.ignored_annotation_counts), {"구름": 1})

    def test_cross_split_excludes_validation_sequence_leakage(self) -> None:
        train = [self._sample("train", "train-a", "shared")]
        val = [
            self._sample("val", "val-a", "shared"),
            self._sample("val", "val-b", "independent"),
        ]

        retained, report = resolve_cross_split(train, val, "exclude")

        self.assertEqual([sample.image_path.stem for sample in retained], ["val-b"])
        self.assertEqual(report["overlapping_source_groups"], 1)
        self.assertEqual(report["excluded_val_images"], 1)

    def test_cross_split_error_policy_rejects_sequence_leakage(self) -> None:
        train = [self._sample("train", "train-a", "shared")]
        val = [self._sample("val", "val-a", "shared")]

        with self.assertRaises(DataPreparationError):
            resolve_cross_split(train, val, "error")


if __name__ == "__main__":
    unittest.main()
