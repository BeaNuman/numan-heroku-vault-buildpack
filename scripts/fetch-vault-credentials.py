#!/usr/bin/env python3
"""
Launch a process with an environment partially populated from Vault.

This script connects to a Vault instance via its HTTP API and attempts
to pull sensitive environment variables from a namespace as specified by
the command line arguments. A process is then spawned with the sensitive
environment variables set.
"""
import json
import os

import urllib3


def main():
    if "VAULT_DEPLOYMENT_TOKEN" not in os.environ:
        raise OSError("The environment variable VAULT_DEPLOYMENT_TOKEN must be set.")
    if "VAULT_ADDRESS" not in os.environ:
        raise OSError("The environment variable VAULT_ADDRESS must be set.")
    if "VAULT_NAMESPACE" not in os.environ:
        raise OSError("The environment variable VAULT_NAMESPACE must be set.")
    if "VAULT_KV_STORE" not in os.environ:
        raise OSError("The environment variable VAULT_KV_STORE must be set.")
    if "VAULT_SECRET" not in os.environ:
        raise OSError("The environment variable VAULT_SECRET must be set.")

    VAULT_DEPLOYMENT_TOKEN = os.getenv("VAULT_DEPLOYMENT_TOKEN")
    VAULT_ADDRESS = os.getenv("VAULT_ADDRESS")
    VAULT_NAMESPACE = os.getenv("VAULT_NAMESPACE")
    VAULT_KV_STORE = os.getenv("VAULT_KV_STORE")
    VAULT_SECRET = os.getenv("VAULT_SECRET")

    http_pool = urllib3.PoolManager()

    try:
        vault_secret_request = http_pool.request(
            "GET",
            f"{VAULT_ADDRESS}/v1/{VAULT_KV_STORE}/data/{VAULT_SECRET}",
            headers={
                "X-Vault-Namespace": VAULT_NAMESPACE,
                "X-Vault-Token": VAULT_DEPLOYMENT_TOKEN,
            },
        )
    except Exception as e:
        raise Exception(f"Attempt to reach Vault failed with error: {e}")

    if vault_secret_request.status != 200:
        raise Exception(
            f"Request to Vault failed with status code {vault_secret_request.status}"
        )

    try:
        payload = json.loads(vault_secret_request.data.decode("utf-8"))["data"]["data"]
    except Exception as e:
        raise Exception(f"Failed to parse Vault payload with error: {e}")

    print('\n'.join(f"{key}={value}" for key, value in payload.items()))

if __name__ == "__main__":
    main()