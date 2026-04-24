import os
from api_client import GatekeeperOMClient

if __name__ == "__main__":
    print("Initializing client...")
    client = GatekeeperOMClient(
        host=os.environ.get("OPENMETADATA_HOST"),
        jwt_token=os.environ.get("OPENMETADATA_JWT_TOKEN")
    )

    if client.health_check():
        print("SUCCESS: Connected to OpenMetadata!")
    else:
        print("FAILED: Could not reach OpenMetadata.")