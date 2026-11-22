from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import importlib.metadata
import platform
import torch

import typing


class git_run_manifest_object(typing.TypedDict):
    commit: str
    dirty: bool


class environment_run_manifest_object(typing.TypedDict):
    platform: str
    python: str
    torch: str
    torchvision: str
    dvc: str
    mlflow: str
    cuda_runtime: str | None


class execution_run_manifest_object(typing.TypedDict):
    device: str
    random_state: int
    mlflow_run_id: str


class configuration_run_manifest_object(typing.TypedDict):
    image_size: int
    batch_size: int
    epochs: int
    learning_rate: float
    dropout: float
    augmentation_enabled: bool
    horizontal_flip: float
    rotation_degrees: int


class data_run_manifest_object(typing.TypedDict):
    training_data_identity: str


class run_manifest_object(typing.TypedDict):
    git: git_run_manifest_object
    data: data_run_manifest_object
    environment: environment_run_manifest_object
    execution: execution_run_manifest_object
    configuration: configuration_run_manifest_object


def training_data_identity(
    train_manifest: Path = Path("data/processed/manifests/train.csv"),
    validation_manifest: Path = Path("data/processed/manifests/validation.csv"),
) -> str:
    """Return a deterministic identity for the training + validation manifests.

    This helper is provided because the final evaluator uses the same identity
    to verify that the selected MLflow Run matches the current prepared data.
    Do not hard-code the value.
    """
    paths = (train_manifest, validation_manifest)
    if any(not path.exists() for path in paths):
        return "unavailable"

    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_run_manifest(params: dict, device: str, mlflow_run_id: str) -> run_manifest_object:
    """Build experiment provenance metadata.

    Hints: subprocess, platform, importlib.metadata, torch,
    training_data_identity().
    """

    try:
        commit_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit_sha = "unavailable"

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        ).strip()
        dirty = bool(status)
    except (subprocess.CalledProcessError, FileNotFoundError):
        dirty = True

    return {
        "git": {
            "commit": commit_sha,
            "dirty": dirty,
        },
        "data": {
            "training_data_identity": training_data_identity(),
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": importlib.metadata.version("torch"),
            "torchvision": importlib.metadata.version("torchvision"),
            "dvc": importlib.metadata.version("dvc"),
            "mlflow": importlib.metadata.version("mlflow"),
            "cuda_runtime": torch.version.cuda if torch.cuda.is_available() else None,
        },
        "execution": {
            "device": device,
            "random_state": int(params["train"]["random_state"]),
            "mlflow_run_id": mlflow_run_id,
        },
        "configuration": {
            "image_size": int(params["data"]["image_size"]),
            "batch_size": int(params["train"]["batch_size"]),
            "epochs": int(params["train"]["epochs"]),
            "learning_rate": float(params["train"]["learning_rate"]),
            "dropout": float(params["train"]["dropout"]),
            "augmentation_enabled": bool(params["augmentation"]["enabled"]),
            "horizontal_flip": params["augmentation"]["horizontal_flip"],
            "rotation_degrees": params["augmentation"]["rotation_degrees"],
        },
    }


def write_run_manifest(params: dict, device: str, mlflow_run_id: str, path: Path) -> run_manifest_object:
    manifest = build_run_manifest(params, device, mlflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest