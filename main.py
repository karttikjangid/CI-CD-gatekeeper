"""CLI entrypoint for CI/CD Gatekeeper orchestration."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from api_client import GatekeeperOMClient
from parser import extract_modified_tables


def generate_markdown_report(impacts: list, total_count: int) -> None:
    """Write blast-radius assessment report to report.md and exit with CI signal code."""
    with open("report.md", "w", encoding="utf-8") as report_file:
        if total_count == 0:
            report_file.write("### Blast Radius Assessment Passed\n\n")
            report_file.write(
                "No Tier-1 assets, ML models, or critical dashboards were impacted by this change.\n"
            )
            sys.exit(0)

        report_file.write("### WARNING: CRITICAL DOWNSTREAM IMPACT DETECTED\n\n")
        report_file.write(
            f"This pull request affects **{total_count}** critical downstream asset(s).\n\n"
        )
        report_file.write(
            "| Source Table Altered | Downstream Asset FQN | Asset Type | Risk Classification |\n"
        )
        report_file.write("| :--- | :--- | :--- | :--- |\n")

        for impact in impacts:
            source_table = str(impact.get("source_table_fqn", ""))
            impacted_asset = str(impact.get("impacted_asset_fqn", ""))
            entity_type = str(impact.get("entity_type", "")).capitalize()
            reasons = impact.get("reasons", [])
            risk = ", ".join(str(reason) for reason in reasons)
            report_file.write(
                f"| `{source_table}` | `{impacted_asset}` | **{entity_type}** | {risk} |\n"
            )

    sys.exit(100)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Run CI/CD Gatekeeper checks.")
    arg_parser.add_argument(
        "--sql-file",
        required=True,
        help="Path to the SQL file to analyze.",
    )
    args = arg_parser.parse_args()

    with open(args.sql_file, "r", encoding="utf-8") as sql_file_handle:
        sql_content = sql_file_handle.read()

    modified_tables = extract_modified_tables(sql_content)
    if not modified_tables:
        print("No mutated tables found. Safe to merge.")
        generate_markdown_report([], 0)

    openmetadata_host = os.environ.get("OPENMETADATA_HOST")
    openmetadata_jwt_token = os.environ.get("OPENMETADATA_JWT_TOKEN")

    if not openmetadata_host or not openmetadata_jwt_token:
        print("CRITICAL ERROR: Missing OPENMETADATA_HOST or OPENMETADATA_JWT_TOKEN.")
        sys.exit(1)

    try:
        client = GatekeeperOMClient(
            host=openmetadata_host,
            jwt_token=openmetadata_jwt_token,
        )

        all_impacts: list[dict[str, Any]] = []
        total_critical_count: int = 0

        for table in modified_tables:
            critical_count, impacts = client.get_downstream_impact(table)
            total_critical_count += critical_count
            all_impacts.extend(impacts)

        print(f"Parsed {len(modified_tables)} modified table(s).")
        print(f"Identified {total_critical_count} critical downstream impact(s).")
        generate_markdown_report(all_impacts, total_critical_count)
    except RuntimeError as exc:
        print(f"CRITICAL ERROR: {exc}")
        sys.exit(1)
