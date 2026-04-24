import os
import re
import sys
import logging
import requests
import sqlglot
from llm_client import call_llm
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_report() -> tuple[str, str]:
    try:
        with open("report.md", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read report.md: {e}")
        sys.exit(0)
        
    pattern = r"^\s*\|?\s*([a-zA-Z0-9_]+)\s*\|\s*([a-zA-Z0-9_.]+)\s*\|"
    match = re.search(pattern, content, re.MULTILINE)
    
    if match is None:
        logger.error("Parsing failure: regex returned None")
        sys.exit(0)
        
    dropped_table = match.group(1)
    downstream_fqn = match.group(2)
    return dropped_table, downstream_fqn

def fetch_schema(fqn: str) -> str:
    token = os.environ.get("OPENMETADATA_JWT_TOKEN", "")
    host = os.environ.get("OPENMETADATA_HOST", "http://localhost:8585/api").rstrip("/")
    
    url = f"{host}/v1/tables/name/{fqn}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Timeout occurred while fetching schema")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to fetch schema: {e}")
        sys.exit(0)
        
    data = response.json()
    columns = data.get("columns", [])
    
    schema_strings = []
    for col in columns:
        name = col.get("name")
        data_type = col.get("dataType")
        schema_strings.append(f"Column: {name} | Type: {data_type}")
        
    return "\n".join(schema_strings)



def generate_patch(source_table: str, fqn: str, schema: str) -> None:
    prompt = f"""According to the strict constraints of this environment, you are an automated, deterministic database engine remediation module.
You must generate CREATE VIEW {source_table}, selecting all necessary fields, using CAST(NULL AS <data_type>) AS <column_name> for missing data.
Do NOT use Markdown formatting. Do NOT wrap the SQL in triple backticks. The very first character of your response must be 'C' for 'CREATE VIEW'.

Schema:
{schema}"""
    
    llm_output = call_llm(prompt)
    
    try:
        sqlglot.parse_one(llm_output, read="bigquery")
    except sqlglot.errors.ParseError as e:
        logger.error(f"SQL validation ParseError: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(0)
        
    try:
        with open("report.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n### Remediation Patch\n")
            f.write(f"```sql\n{llm_output}\n```\n")
    except Exception as e:
        logger.error(f"Failed to write to report.md: {e}")
        sys.exit(0)

if __name__ == "__main__":
    dropped_table, fqn = parse_report()
    logger.info(f"Dropped table: {dropped_table}, Downstream FQN: {fqn}")
    schema = fetch_schema(fqn)
    logger.info(f"Schema:\n{schema}")
    generate_patch(dropped_table, fqn, schema)
    logger.info("Remediation patch generated and appended successfully.")
