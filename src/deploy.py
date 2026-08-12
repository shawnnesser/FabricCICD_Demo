"""
deploy.py - Fabric CI/CD deployment script
Called by GitHub Actions to deploy item definitions to a target environment.

Usage:
    python src/deploy.py --environment test
    python src/deploy.py --environment prod
"""

import argparse
import os
import sys

from fabric_cicd import FabricWorkspace, publish_all_items
from auth_helper import get_token_credential


def get_credential(environment: str):
    """Build a token credential from env vars, Key Vault, or Azure CLI."""
    try:
        return get_token_credential(environment)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


ITEM_TYPES = [
    "Lakehouse",
    "Notebook",
    "DataPipeline",
    "SemanticModel",
    "Report",
]


def main():
    parser = argparse.ArgumentParser(description="Deploy Fabric solution via fabric-cicd")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["test", "prod"],
        help="Target environment",
    )
    args = parser.parse_args()

    print(f"[INFO] Starting deployment to environment: {args.environment}")

    workspace_id_variable = f"FABRIC_{args.environment.upper()}_WORKSPACE_ID"
    workspace_id = os.environ.get(workspace_id_variable)
    if not workspace_id:
        parser.error(f"{workspace_id_variable} must be set for deployment.")
    repository_directory = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "workspace")
    )

    print(f"[INFO] Workspace ID: {workspace_id}")
    print(f"[INFO] Repository directory: {repository_directory}")

    credential = get_credential(args.environment)

    workspace = FabricWorkspace(
        workspace_id=workspace_id,
        environment=args.environment,
        repository_directory=repository_directory,
        item_type_in_scope=ITEM_TYPES,
        token_credential=credential,
    )

    publish_all_items(workspace)

    print(f"[INFO] Deployment to '{args.environment}' completed successfully.")


if __name__ == "__main__":
    main()
