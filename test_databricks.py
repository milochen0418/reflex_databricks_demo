import os

from databricks import sql


server_hostname = os.environ["DATABRICKS_SERVER_HOSTNAME"]
http_path = os.environ["DATABRICKS_HTTP_PATH"]


with sql.connect(
    server_hostname=server_hostname,
    http_path=http_path,
    auth_type="databricks-oauth",
) as connection:

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                patient_id,
                name,
                department,
                priority,
                status
            FROM default.patients
            ORDER BY priority
        """)

        rows = cursor.fetchall()

        for row in rows:
            print(row)