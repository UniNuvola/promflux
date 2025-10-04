from influxdb_client_3 import InfluxDBClient3, Point
from logging import getLogger, DEBUG, INFO, StreamHandler
from os import getenv
from datetime import datetime, timezone


class InfluxWrapper:
    """
    Classe che Wrappa la interazione con il database influx.

    Questa classe funziona con il database InfluxCoreV3 altre
    versioni del database Influx non è dato sapere se funzionano.

    :param str url: Endpoint dove si trova il server InfluxCoreV3
    :param str token: Token di accesso per il database; di fatto
                      l'utente con il quale ci stiamo loggando.
    """

    def __init__(self, url: str, token: str):
        self.log = getLogger(__name__)
        self.log.setLevel(DEBUG if getenv("DEBUG", 0) else INFO)
        self.log.addHandler(StreamHandler())
        self.url = url
        self.token = token

    def write(self, db_name: str, data: list[dict]):
        """
        Questa funzione si occupa di interpretare il risultato di
        Responde dal server Prometheus.

        :param str db_name: Nome del database dove salvare i dati
        :param list[dict]: I dati grezzi che devono essere inseriti
        """
        with InfluxDBClient3(
            host=self.url,
            token=self.token,
            org="uninuvola",
            database="uninuvola",
        ) as client:
            for result in data:
                data_keys = result.keys()
                print(type(data_keys))
                if "values" in data_keys:
                    for time, value in result["values"]:
                        point = Point(db_name)
                        point.field("value", float(value))
                        for key, tag in result["metric"].items():
                            point.tag(key, tag)
                        dt_object = datetime.fromtimestamp(
                            time,
                            tz=timezone.utc,
                        )
                        point.time(dt_object)
                        client.write(point)
                        self.log.debug(
                            f"Scritto in database influx ->{point.to_line_protocol()}"
                        )
                elif "value" in data_keys:
                    point = Point(db_name)
                    time, value = result["value"]
                    point.field("value", float(value))
                    for key, tag in result["metric"].items():
                        point.tag(key, tag)
                        point.field("value", float(value))
                    dt_object = datetime.fromtimestamp(time, tz=timezone.utc)
                    point.time(dt_object)
                    client.write(point)
                    self.log.debug(
                        f"Scritto in database influx ->{point.to_line_protocol()}"
                    )
                else:
                    """In questa condizione non so cosa fare,
                    nei miei test non è mai successo
                    """
                    self.log.error(
                        "Never have the case data_keys DON'T CONTAINS [values or value], I DONT KNOW WHAT TO DO"
                    )
                    raise Exception(f"LOGGED ERROR - DATA: {data_keys}")
