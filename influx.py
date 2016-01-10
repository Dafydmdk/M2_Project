import influxdb


def send_data(json_data):
    db_client = influxdb.InfluxDBClient('5.196.8.140',
                                        8086,
                                        'ISEN',
                                        'ISEN29',
                                        'thermostat')
    db_client.write_points(json_data)
