import os
from typing import Any

from databricks import sql
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create a connection to Databricks SQL Warehouse.

    Required environment variables:
    - DATABRICKS_SERVER_HOSTNAME
    - DATABRICKS_HTTP_PATH
    """

    server_hostname = os.environ["DATABRICKS_SERVER_HOSTNAME"]
    http_path = os.environ["DATABRICKS_HTTP_PATH"]

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        auth_type="databricks-oauth",
    )


def execute_query(query: str) -> list[dict[str, Any]]:
    """
    Execute a SQL query and return rows as a list of dictionaries.

    Example:
    [
        {
            "patient_id": "P001",
            "name": "Amy",
            "department": "Internal Medicine",
            "priority": 3,
            "status": "waiting",
        }
    ]
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)

            if cursor.description is None:
                return []

            columns = [
                column[0]
                for column in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]


def get_patients() -> list[dict[str, Any]]:
    """
    Get all patients ordered by priority.
    """

    query = """
        SELECT
            patient_id,
            name,
            department,
            priority,
            status
        FROM default.patients
        ORDER BY priority ASC
    """

    return execute_query(query)


def get_waiting_patients() -> list[dict[str, Any]]:
    """
    Get patients whose status is waiting.
    """

    query = """
        SELECT
            patient_id,
            name,
            department,
            priority,
            status
        FROM default.patients
        WHERE status = 'waiting'
        ORDER BY priority ASC
    """

    return execute_query(query)


def get_patient_count() -> int:
    """
    Return the total number of patients.
    """

    query = """
        SELECT COUNT(*) AS patient_count
        FROM default.patients
    """

    rows = execute_query(query)

    if not rows:
        return 0

    return int(rows[0]["patient_count"])