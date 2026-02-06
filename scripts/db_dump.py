import os
import datetime
import pymysql


def get_env(name):
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        raise RuntimeError("missing env: PINGUAN_DB_HOST/PORT/USER/PASSWORD/NAME")
    return value


db_host = get_env("PINGUAN_DB_HOST")
db_port = int(get_env("PINGUAN_DB_PORT"))
db_user = get_env("PINGUAN_DB_USER")
db_password = get_env("PINGUAN_DB_PASSWORD")
db_name = get_env("PINGUAN_DB_NAME")

out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "exports")
os.makedirs(out_dir, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
schema_file = os.path.join(out_dir, f"schema_{timestamp}.sql")
data_file = os.path.join(out_dir, f"data_{timestamp}.sql")

conn = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name,
    charset="utf8mb4",
    autocommit=True,
)

cursor = conn.cursor()
cursor.execute(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY table_name",
    (db_name,),
)
tables = [row[0] for row in cursor.fetchall()]

with open(schema_file, "w", encoding="utf-8") as schema_out:
    schema_out.write("SET NAMES utf8mb4;\n")
    for table in tables:
        cursor.execute(f"SHOW CREATE TABLE `{table}`")
        create_sql = cursor.fetchone()[1]
        schema_out.write(f"DROP TABLE IF EXISTS `{table}`;\n")
        schema_out.write(create_sql + ";\n\n")

with open(data_file, "w", encoding="utf-8") as data_out:
    data_out.write("SET NAMES utf8mb4;\n")
    for table in tables:
        cursor.execute(f"SELECT * FROM `{table}`")
        rows = cursor.fetchall()
        if not rows:
            continue
        columns = [desc[0] for desc in cursor.description]
        col_list = ",".join([f"`{col}`" for col in columns])
        for row in rows:
            values = []
            for value in row:
                if value is None:
                    values.append("NULL")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                elif isinstance(value, (bytes, bytearray)):
                    values.append("0x" + value.hex())
                else:
                    escaped = pymysql.converters.escape_string(str(value))
                    values.append("'" + escaped + "'")
            data_out.write(f"INSERT INTO `{table}` ({col_list}) VALUES ({','.join(values)});\n")

cursor.close()
conn.close()

print(f"schema={schema_file}")
print(f"data={data_file}")
