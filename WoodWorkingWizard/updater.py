# Copyright (c) 2025 Fabio Brondo
# This software is distributed under the GNU GPLv3 license.
# Original Repository: https://github.com/fabio1994/WoodWorkingWizard

   
from __future__ import annotations
import os, io, json, shutil, zipfile, tempfile, hashlib, urllib.request
from typing import Tuple

                                                
PRODUCT_NAME = "WoodWorkingWizard"
PRODUCT_VERSION = "2.1.3"

def _safe_get_installed_version() -> str:
           
                             
    try:
        p = os.path.join(os.path.expanduser("~"), "AppData", "Roaming",
                         "Autodesk", "Autodesk Fusion 360", "API", "AddIns", "WoodWorkingWizard",
                         "WoodWorkingWizard.manifest")
        with open(p, "r", encoding="utf-8") as f:
            m = json.load(f)
        v = m.get("version") or m.get("Version")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:
        pass
                                 
    return PRODUCT_VERSION

                                                          
MANIFEST_URL = "https://fabio1994.github.io/WoodWorkingWizard/latest.json"


def _parse_version(v: str) -> Tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def _get_addin_dir() -> str:
    return os.path.join(os.path.expanduser("~"), "AppData", "Roaming",
                        "Autodesk", "Autodesk Fusion 360", "API", "AddIns", PRODUCT_NAME)


def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_for_update() -> Tuple[bool, str, dict]:
                                                          
    try:
        m = _fetch_json(MANIFEST_URL)
        latest = m.get("latestVersion")
        if not latest:
            return False, "No latestVersion in manifest.", m
        try:
            installed = PRODUCT_VERSION or "0.0.0"
            newer = _parse_version(latest) > _parse_version(installed)
        except Exception:
            newer = False
        return newer, (f"Update available: {latest}" if newer else f"Up to date: v{installed}"), m
    except Exception as e:
        return False, f"Update check failed: {e}", {}


def apply_update_from_manifest(manifest: dict) -> Tuple[bool, str]:
    try:
        zip_url = manifest["zipUrl"]
        blob = _download(zip_url)
        expected = manifest.get("zipSha256")
        if expected and _sha256(blob).lower() != expected.lower():
            return False, "Checksum mismatch for downloaded update."
        addin_dir = _get_addin_dir()
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                zf.extractall(td)
            backup = addin_dir + ".backup"
            if os.path.exists(backup):
                shutil.rmtree(backup, ignore_errors=True)
            if os.path.exists(addin_dir):
                os.replace(addin_dir, backup)
            shutil.copytree(td, addin_dir)
            shutil.rmtree(backup, ignore_errors=True)
        return True, "Update applied. Please restart Fusion 360."
    except Exception as e:
        return False, f"Update failed: {e}"


if __name__ == "__main__":
    newer, msg, m = check_for_update()
    print(msg)
    if newer:
        ok, umsg = apply_update_from_manifest(m)
        print(umsg)
