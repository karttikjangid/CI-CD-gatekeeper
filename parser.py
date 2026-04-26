"""Parser module for extracting modified tables from SQL statements."""

from __future__ import annotations

import sqlglot
import sqlglot.expressions as exp
from sqlglot.errors import ParseError


def extract_modified_tables(sql_content: str, dialect: str = "bigquery") -> set[str]:
    """Extract tables targeted by DML/DDL operations while ignoring SELECT statements.

    Args:
        sql_content: The raw SQL string to parse.
        dialect: The SQL dialect to use for parsing, defaults to 'bigquery'.

    Returns:
        A set of table names that are modified by the SQL content.
    """
    modified_tables: set[str] = set()

    try:
        statements = sqlglot.parse(sql_content, read=dialect)
    except ParseError:
        return modified_tables

    for statement in statements:
        if statement is None:
            continue

        table_node: exp.Table | None = None

        if isinstance(statement, exp.Update):
            update_target = statement.args.get("this")
            if isinstance(update_target, exp.Table):
                table_node = update_target
        elif isinstance(statement, exp.Insert):
            insert_target = statement.args.get("this")
            if isinstance(insert_target, exp.Table):
                table_node = insert_target
        elif isinstance(statement, exp.Delete):
            delete_target = statement.args.get("this")
            if isinstance(delete_target, exp.Table):
                table_node = delete_target
        elif isinstance(statement, (exp.Drop, exp.Create)):
            direct_target = statement.args.get("this")
            if isinstance(direct_target, exp.Table):
                table_node = direct_target
        elif isinstance(statement, exp.Alter):
            alter_target = statement.args.get("this")
            actions = statement.args.get("actions", [])
            has_drop = any(isinstance(action, exp.Drop) for action in actions)
            if has_drop and isinstance(alter_target, exp.Table):
                table_node = alter_target

        if table_node is not None:
            modified_tables.add(table_node.sql(dialect=dialect))

    return {format_table_name(table_name) for table_name in modified_tables}


def format_table_name(raw_name: str) -> str:
    """Normalize a table name string to OpenMetadata FQN-compatible format."""
    return raw_name.replace("\"", "").replace("'", "").replace("`", "").lower()
