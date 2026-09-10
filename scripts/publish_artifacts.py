"""
Upload artifacts to HuggingFace and create a versioned release tag.

Run from the repository root after export_artifacts.py has been run:
    python scripts/publish_artifacts.py

The R package version in packages/r/DESCRIPTION is used as the tag name:
    r-v<version>   (e.g. r-v0.7.0)

Prerequisites:
    pip install huggingface_hub
    hf auth login
"""

import re
import subprocess
import sys
from pathlib import Path

from huggingface_hub import HfApi

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
HF_REPO_ID = "marknovak/TaxonBodyMassML"
DESCRIPTION = REPO_ROOT / "packages" / "r" / "DESCRIPTION"


def _r_version() -> str:
    for line in DESCRIPTION.read_text().splitlines():
        m = re.match(r"^Version:\s*(\S+)", line)
        if m:
            return m.group(1)
    raise RuntimeError(f"Version not found in {DESCRIPTION}")


def main() -> None:
    version = _r_version()
    tag = f"r-v{version}"

    print(f"Uploading {ARTIFACTS_DIR} → {HF_REPO_ID} ...")
    result = subprocess.run(
        ["hf", "upload", HF_REPO_ID, str(ARTIFACTS_DIR), ".", "--repo-type", "model"],
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"Upload failed (exit {result.returncode}). Aborting tag creation.")

    api = HfApi()
    for tag in (f"r-v{version}", f"py-v{version}"):
        print(f"Creating HuggingFace tag {tag!r} ...")
        api.create_tag(HF_REPO_ID, tag=tag, repo_type="model", exist_ok=True)
    print(f"Done. Artifacts published at {HF_REPO_ID} (r-v{version}, py-v{version})")


if __name__ == "__main__":
    main()
