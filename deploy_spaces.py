"""
Deploy paper-repro-auditor and finetune-failure-extractor to HuggingFace Spaces.
Run: python deploy_spaces.py
"""

from huggingface_hub import HfApi
from pathlib import Path

api = HfApi()
ROOT = Path(__file__).parent

SPACES = [
    {
        "repo_id": "sidharthkriplani/paper-repro-auditor",
        "folder": ROOT / "solutions" / "paper-repro-auditor",
        "files": ["app.py", "core.py", "risk_factors.py", "requirements.txt"],
        "hf_readme": "hf_README.md",
    },
    {
        "repo_id": "sidharthkriplani/finetune-failure-extractor",
        "folder": ROOT / "solutions" / "finetune-failure-extractor",
        "files": ["app.py", "core.py", "failure_types.py", "requirements.txt"],
        "hf_readme": "hf_README.md",
    },
]

for space in SPACES:
    print(f"\nDeploying {space['repo_id']} ...")

    # Create space if it doesn't exist
    api.create_repo(
        repo_id=space["repo_id"],
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
    )

    # Upload README (frontmatter tells HF it's a Gradio space)
    api.upload_file(
        path_or_fileobj=str(space["folder"] / space["hf_readme"]),
        path_in_repo="README.md",
        repo_id=space["repo_id"],
        repo_type="space",
    )

    # Upload source files
    for filename in space["files"]:
        api.upload_file(
            path_or_fileobj=str(space["folder"] / filename),
            path_in_repo=filename,
            repo_id=space["repo_id"],
            repo_type="space",
        )
        print(f"  ✓ {filename}")

    print(f"  → https://huggingface.co/spaces/{space['repo_id']}")

print("\nAll spaces deployed.")
