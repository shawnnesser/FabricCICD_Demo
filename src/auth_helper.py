import os

from azure.identity import AzureCliCredential, ClientSecretCredential
from dotenv import load_dotenv
import requests

REQUIRED_ENV_VARS = (
    "AZURE_TENANT_ID",
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
)

SECRET_NAME_CANDIDATES = {
    "AZURE_TENANT_ID": ("azure-tenant-id", "tenant-id"),
    "AZURE_CLIENT_ID": ("azure-client-id", "client-id"),
    "AZURE_CLIENT_SECRET": ("azure-client-secret", "client-secret"),
}


def _read_secret(key_vault_name: str, secret_names: tuple[str, ...], credential: AzureCliCredential) -> str | None:
    token = credential.get_token("https://vault.azure.net/.default").token
    headers = {"Authorization": f"Bearer {token}"}

    for secret_name in secret_names:
        response = requests.get(
            f"https://{key_vault_name}.vault.azure.net/secrets/{secret_name}?api-version=7.4",
            headers=headers,
            timeout=30,
        )
        if response.status_code == 404:
            continue
        response.raise_for_status()
        return response.json().get("value")
    return None


def _get_key_vault_name(environment: str | None) -> str | None:
    return (
        os.environ.get("KEY_VAULT_NAME")
        or os.environ.get("AZURE_KEY_VAULT_NAME")
    )


def load_service_principal_settings(environment: str | None = None) -> dict[str, str]:
    load_dotenv()

    values = {name: os.environ.get(name) for name in REQUIRED_ENV_VARS}
    missing = [name for name, value in values.items() if not value]
    if not missing:
        return values

    key_vault_name = _get_key_vault_name(environment)
    if not key_vault_name:
        raise RuntimeError("Key Vault name not configured for service principal lookup.")

    credential = AzureCliCredential()

    for env_name in missing:
        secret_value = _read_secret(key_vault_name, SECRET_NAME_CANDIDATES[env_name], credential)
        if secret_value:
            values[env_name] = secret_value
            os.environ[env_name] = secret_value

    still_missing = [name for name, value in values.items() if not value]
    if still_missing:
        missing_list = ", ".join(still_missing)
        raise RuntimeError(
            f"Key Vault '{key_vault_name}' did not contain required secrets: {missing_list}."
        )

    print(f"[INFO] Loaded service principal settings from Key Vault '{key_vault_name}'.")
    return values


def get_client_secret_credential(environment: str | None = None) -> ClientSecretCredential:
    settings = load_service_principal_settings(environment)
    return ClientSecretCredential(
        tenant_id=settings["AZURE_TENANT_ID"],
        client_id=settings["AZURE_CLIENT_ID"],
        client_secret=settings["AZURE_CLIENT_SECRET"],
    )


def get_token_credential(environment: str | None = None):
    env_values = {name: os.environ.get(name) for name in REQUIRED_ENV_VARS}
    if all(env_values.values()):
        return ClientSecretCredential(
            tenant_id=env_values["AZURE_TENANT_ID"],
            client_id=env_values["AZURE_CLIENT_ID"],
            client_secret=env_values["AZURE_CLIENT_SECRET"],
        )

    try:
        return get_client_secret_credential(environment)
    except Exception as exc:
        print(f"[WARN] Service principal lookup unavailable: {exc}")

    print("[INFO] Falling back to Azure CLI credential for local execution.")
    return AzureCliCredential()