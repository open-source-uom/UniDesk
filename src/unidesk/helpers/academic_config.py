"""@file academic_config.py
@brief Loads and saves the shared UniOS academic profile."""

import json
import os

# Where the shared UniOS academic profile is persisted. Other UniOS apps read
# this same file, so the location and key names below must not change.
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".unios")
CONFIG_PATH = os.path.join(CONFIG_DIR, "academicConfig.json")


def load_academic_config():
    """@brief Reads the saved academic profile from disk.

    A missing, corrupt or partial file gives empty strings instead of an error.
    @return A dict with the "universityName" and "departmentName" keys.
    """
    config = {"universityName": "", "departmentName": ""}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return config

    if isinstance(data, dict):
        config["universityName"] = data.get("universityName", "") or ""
        config["departmentName"] = data.get("departmentName", "") or ""
    return config


def save_academic_config(university, department):
    """@brief Saves the academic profile to ~/.unios/academicConfig.json.
    @param university Name of the chosen university.
    @param department Name of the chosen department.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "universityName": university,
        "departmentName": department,
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
