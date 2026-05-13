from influxdb_client_3 import InfluxDBClient3, Point

def connect(host: str, db_name: str, token: str) -> InfluxDBClient3:
    client = InfluxDBClient3(
        host=host,
        database=db_name,
        token=token,
    )

    try:
        client.write(record=Point("connection_healthcheck").field("ok", 1))
    except Exception as e:
        print(f"InfluxDB connection error: {e}")
        raise e

    return client
