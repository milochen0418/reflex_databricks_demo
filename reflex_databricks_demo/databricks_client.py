import os
import threading
from typing import Any

from databricks import sql
from databricks.sql.experimental.oauth_persistence import DevOnlyFilePersistence
from dotenv import load_dotenv


load_dotenv()


PATIENT_STATUSES = ["waiting", "seeing", "done", "cancelled"]

# OAuth tokens are saved here so restarting the app does not ask to log in again.
OAUTH_TOKEN_FILE = os.path.expanduser("~/.reflex_databricks_demo_oauth.json")

# One shared connection, reused by every query (opening one triggers OAuth).
_connection = None
_connection_lock = threading.Lock()


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
        experimental_oauth_persistence=DevOnlyFilePersistence(OAUTH_TOKEN_FILE),
    )


def _get_shared_connection():
    """
    Return the shared connection, opening it on first use or after it closed.
    """

    global _connection

    if _connection is None or not _connection.open:
        _connection = get_connection()

    return _connection


def _reset_shared_connection() -> None:
    """
    Close and forget the shared connection so the next query reconnects.
    """

    global _connection

    if _connection is not None:
        try:
            _connection.close()
        except Exception:
            pass

    _connection = None


def _run_query(
    connection,
    query: str,
    parameters: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)

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


def execute_query(
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Execute a SQL query and return rows as a list of dictionaries.

    Uses the shared connection; if it has gone stale (e.g. session expired),
    reconnects once and retries.

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

    with _connection_lock:
        try:
            return _run_query(_get_shared_connection(), query, parameters)

        except sql.exc.RequestError:
            _reset_shared_connection()
            return _run_query(_get_shared_connection(), query, parameters)


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


def update_patient_status(patient_id: str, status: str) -> None:
    """
    Update a patient's status with SQL UPDATE.
    """

    if status not in PATIENT_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    query = """
        UPDATE default.patients
        SET status = :status
        WHERE patient_id = :patient_id
    """

    execute_query(
        query,
        {
            "status": status,
            "patient_id": patient_id,
        },
    )
