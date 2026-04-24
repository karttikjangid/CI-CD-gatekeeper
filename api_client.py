"""OpenMetadata API client skeleton for CI/CD Gatekeeper Phase 1."""

from __future__ import annotations

import logging
from typing import Any, cast

from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    CustomSecretStr,
    OpenMetadataJWTClientConfig,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.data.table import Table


class GatekeeperOMClient:
    """Wrapper around the OpenMetadata SDK for lineage impact lookups."""

    def __init__(self, host: str, jwt_token: str) -> None:
        """Initialize the Gatekeeper OpenMetadata client wrapper.

        Args:
            host: OpenMetadata server host and port endpoint.
            jwt_token: JWT token used for OpenMetadata authentication.
        """
        self._logger: logging.Logger = logging.getLogger(__name__)

        if not host:
            raise ValueError("host must be a non-empty string")
        if not jwt_token:
            raise ValueError("jwt_token must be a non-empty string")

        jwt_secret: CustomSecretStr = cast(CustomSecretStr, jwt_token)
        security_config: OpenMetadataJWTClientConfig = OpenMetadataJWTClientConfig(
            jwtToken=jwt_secret
        )

        connection_payload: dict[str, Any] = {
            "hostPort": host,
            "authProvider": "openmetadata",
            "securityConfig": security_config,
        }

        if hasattr(OpenMetadataConnection, "model_validate"):
            self._connection = OpenMetadataConnection.model_validate(connection_payload)
        else:
            self._connection = OpenMetadataConnection.parse_obj(connection_payload)

        try:
            self.metadata: OpenMetadata = OpenMetadata(self._connection)
        except Exception:
            self._logger.exception("Failed to initialize OpenMetadata client")
            raise

    def health_check(self) -> bool:
        """Check whether the OpenMetadata service is reachable.

        Returns:
            True when the service is healthy; otherwise False.
        """
        try:
            is_healthy: bool = bool(self.metadata.health_check())
        except Exception:
            self._logger.exception("OpenMetadata health check request failed")
            return False

        if not is_healthy:
            self._logger.error("OpenMetadata server is unreachable or unhealthy")
        return is_healthy

    def get_table_entity(self, fqn: str) -> Any | None:
        """Retrieve a table entity by FQN including tag metadata.

        Args:
            fqn: Fully qualified table name in OpenMetadata.

        Returns:
            The table entity when found; otherwise None.
        """
        if not fqn:
            raise ValueError("fqn must be a non-empty string")

        try:
            table_entity: Any | None = self.metadata.get_by_name(
                entity=Table,
                fqn=fqn,
                fields=["tags"],
            )
        except Exception:
            self._logger.exception("Failed to retrieve table entity for FQN: %s", fqn)
            raise RuntimeError(f"Failed to retrieve table entity for FQN: {fqn}")

        if table_entity is None:
            self._logger.warning("Table entity not found for FQN: %s", fqn)
            raise RuntimeError(f"Table entity not found for FQN: {fqn}")
        return table_entity

    def get_downstream_impact(self, table_fqn: str) -> tuple[int, list[dict[str, Any]]]:
        """Return critical downstream impact count and entity details for a table.

        Args:
            table_fqn: Fully qualified table name to analyze.

        Returns:
            A tuple with total critical asset count and impacted asset details.
        """
        if not table_fqn:
            raise ValueError("table_fqn must be a non-empty string")

        table_entity: Any | None = self.get_table_entity(table_fqn)
        if table_entity is None:
            raise RuntimeError(f"Unable to resolve table entity for FQN: {table_fqn}")

        table_id_value: Any = getattr(table_entity, "id", None)
        clean_id: str = (
            str(table_id_value.root)
            if hasattr(table_id_value, "root")
            else str(getattr(table_id_value, "__root__", table_id_value) or "")
        )
        if not clean_id:
            self._logger.warning("Table id missing for FQN: %s", table_fqn)
            raise RuntimeError(f"Table id missing for FQN: {table_fqn}")

        try:
            lineage_response: Any = self.metadata.client.get(
                f"/lineage/table/{clean_id}?downstreamDepth=3"
            )
        except Exception:
            self._logger.exception("Failed lineage lookup for FQN: %s", table_fqn)
            raise RuntimeError(f"Failed lineage lookup for FQN: {table_fqn}")

        nodes: list[Any] = []
        if isinstance(lineage_response, dict):
            raw_nodes: Any = lineage_response.get("nodes", [])
            if isinstance(raw_nodes, list):
                nodes = raw_nodes

        impacted_assets: list[dict[str, Any]] = []
        for node in nodes:
            if not isinstance(node, dict):
                continue

            reasons: list[str] = []
            # Extract type, using both `type` and `entityType` as fallbacks
            entity_type: str = str(node.get("type", node.get("entityType", ""))).lower()
            if entity_type in {"mlmodel", "dashboard", "pipeline"}:
                reasons.append(f"critical entity type: {entity_type}")

            node_id = node.get("id")
            full_entity = node

            if node_id and entity_type:
                try:
                    # Step B: Fetch full entity defensively
                    endpoint = f"/{entity_type}s/{node_id}?fields=tags"
                    fetched_entity = self.metadata.client.get(endpoint)
                    if isinstance(fetched_entity, dict):
                        full_entity = fetched_entity
                except Exception as e:
                    self._logger.warning("Failed to fetch full entity for %s (%s): %s", node_id, entity_type, e)

            # Step C: Inspect the full entity payload for tags and tier
            tags_value: Any = full_entity.get("tags", [])
            has_tier1_tag: bool = False
            
            if isinstance(tags_value, str):
                import json
                try:
                    tags_value = json.loads(tags_value)
                except Exception:
                    pass

            if isinstance(tags_value, list):
                for tag in tags_value:
                    if isinstance(tag, dict):
                        tag_fqn = str(tag.get("tagFQN", "")).lower()
                        tag_name = str(tag.get("name", "")).lower()
                        if "tier1" in tag_fqn or "tier1" in tag_name:
                            has_tier1_tag = True
                            break
                    elif isinstance(tag, str):
                        if "tier1" in tag.lower():
                            has_tier1_tag = True
                            break
            elif isinstance(tags_value, dict):
                tag_fqn = str(tags_value.get("tagFQN", "")).lower()
                tag_name = str(tags_value.get("name", "")).lower()
                if "tier1" in tag_fqn or "tier1" in tag_name:
                    has_tier1_tag = True

            if has_tier1_tag:
                reasons.append("critical tag: Tier1")

            if reasons:
                impacted_assets.append(
                    {
                        "source_table_fqn": table_fqn,
                        "impacted_asset_fqn": node.get("fullyQualifiedName", ""),
                        "entity_type": entity_type,
                        "reasons": reasons,
                    }
                )

        return len(impacted_assets), impacted_assets
