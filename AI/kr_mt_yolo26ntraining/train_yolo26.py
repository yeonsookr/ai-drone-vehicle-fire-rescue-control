"""Train and validate a YOLO26n wildfire detector with Ultralytics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_batch(value: str) -> int | float:
    """Accept fixed integer batches or Ultralytics auto-batch fractions."""

    try:
        if any(character in value.lower() for character in (".", "e")):
            parsed = float(value)
            if not 0.0 < parsed <= 1.0:
                raise ValueError
            return parsed
        parsed_int = int(value)
        if parsed_int == -1 or parsed_int > 0:
            return parsed_int
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "batch must be a positive integer, -1, or a fraction in (0, 1]"
        ) from exc
    raise argparse.ArgumentTypeError(
        "batch must be a positive integer, -1, or a fraction in (0, 1]"
    )


def parse_cache(value: str) -> bool | str:
    normalized = value.strip().lower()
    if normalized in {"false", "no", "0"}:
        return False
    if normalized in {"true", "yes", "1", "ram"}:
        return "ram"
    if normalized == "disk":
        return "disk"
    raise argparse.ArgumentTypeError("cache must be false, ram, or disk")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def summarize_metrics(metrics: Any, weights: Path) -> dict[str, Any]:
    box = getattr(metrics, "box", None)
    summary: dict[str, Any] = {
        "weights": str(weights.resolve()),
        "results_dict": _json_safe(getattr(metrics, "results_dict", {})),
        "speed_ms_per_image": _json_safe(getattr(metrics, "speed", {})),
    }
    if box is not None:
        summary["box"] = {
            "map50_95": _json_safe(getattr(box, "map", None)),
            "map50": _json_safe(getattr(box, "map50", None)),
            "map75": _json_safe(getattr(box, "map75", None)),
            "per_class_map50_95": _json_safe(getattr(box, "maps", None)),
        }
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a Korean wildfire YOLO26n model")
    parser.add_argument("--data", required=True, help="Generated data.yaml path")
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=parse_batch, default=0.70)
    parser.add_argument("--device", default=None, help="For example: 0, cpu, or mps")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--patience", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--optimizer", default="auto")
    parser.add_argument("--cache", type=parse_cache, default=False)
    parser.add_argument("--close-mosaic", type=int, default=10)
    parser.add_argument("--project-dir", default=None)
    parser.add_argument("--name", default="kr_yolo26n_baseline")
    parser.add_argument(
        "--resume",
        default=None,
        metavar="LAST_PT",
        help="Resume an interrupted run from its last.pt",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_yaml = Path(args.data).expanduser().resolve()
    if not data_yaml.is_file():
        raise SystemExit(f"data.yaml does not exist: {data_yaml}")

    try:
        import ultralytics
        from ultralytics import YOLO
        from ultralytics.data.utils import check_det_dataset
    except ImportError as exc:
        raise SystemExit(
            "Ultralytics is not installed in this Python environment. "
            "Install it only after the team approves the dependency change."
        ) from exc

    print(f"Ultralytics version: {ultralytics.__version__}")
    print(f"Validating dataset config: {data_yaml}")
    check_det_dataset(str(data_yaml))

    project_dir = (
        Path(args.project_dir).expanduser().resolve()
        if args.project_dir
        else data_yaml.parent / "runs"
    )

    if args.resume:
        resume_path = Path(args.resume).expanduser().resolve()
        if not resume_path.is_file():
            raise SystemExit(f"resume checkpoint does not exist: {resume_path}")
        model = YOLO(str(resume_path))
        model.train(resume=True)
    else:
        model = YOLO(args.model)
        train_options: dict[str, Any] = {
            "data": str(data_yaml),
            "epochs": args.epochs,
            "imgsz": args.imgsz,
            "batch": args.batch,
            "workers": args.workers,
            "patience": args.patience,
            "seed": args.seed,
            "deterministic": True,
            "optimizer": args.optimizer,
            "cache": args.cache,
            "close_mosaic": args.close_mosaic,
            "project": str(project_dir),
            "name": args.name,
            "exist_ok": False,
            "amp": True,
            "plots": True,
            "val": True,
        }
        if args.device is not None:
            train_options["device"] = args.device
        model.train(**train_options)

    trainer = getattr(model, "trainer", None)
    trainer_save_dir = getattr(trainer, "save_dir", None)
    if trainer_save_dir is None:
        raise SystemExit("training finished but Ultralytics did not report a run directory")
    save_dir = Path(trainer_save_dir).resolve()
    best_weights = save_dir / "weights" / "best.pt"
    last_weights = save_dir / "weights" / "last.pt"
    selected_weights = best_weights if best_weights.is_file() else last_weights
    if not selected_weights.is_file():
        raise SystemExit(f"training finished but no checkpoint was found under: {save_dir}")

    print(f"Validating selected checkpoint: {selected_weights}")
    best_model = YOLO(str(selected_weights))
    val_options: dict[str, Any] = {
        "data": str(data_yaml),
        "split": "val",
        "imgsz": args.imgsz,
        "workers": args.workers,
        "plots": True,
    }
    if isinstance(args.batch, int) and args.batch > 0:
        val_options["batch"] = args.batch
    if args.device is not None:
        val_options["device"] = args.device
    metrics = best_model.val(**val_options)
    summary = summarize_metrics(metrics, selected_weights)
    summary_path = save_dir / "validation_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"training output: {save_dir}")
    print(f"best checkpoint: {selected_weights}")
    print(f"validation summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
