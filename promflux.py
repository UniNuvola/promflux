from argparse import ArgumentParser, Namespace
import json
from os import getenv
from dotenv import load_dotenv
from logging import getLogger, DEBUG, INFO, StreamHandler
from Wrappers import PrometheusWrapper, InfluxWrapper, RuleParser

load_dotenv()

log = getLogger("Promflux")
log.setLevel(DEBUG if getenv("DEBUG", 0) else INFO)
log.addHandler(StreamHandler())


def main(arguments: Namespace):
    file_config = getenv("FILE_PATH")
    log.debug(file_config)
    if arguments.file is not None:
        file_config = arguments.file

    prometheus_url = getenv("PROMETHEUS_URL")
    log.debug(prometheus_url)
    if arguments.prometheus is not None:
        prometheus_url = arguments.prometheus

    influx_url = getenv("INFLUX_URL")
    log.debug(influx_url)
    if arguments.influx is not None:
        influx_url = arguments.influx

    influx_token = getenv("INFLUX_TOKEN")
    if arguments.token is not None:
        influx_token = arguments.token

    ignore_tls = getenv("IGNORE_TLS", False)
    if arguments.ignore_tls is not None:
        ignore_tls = True

    conf_parser = RuleParser(file_config)

    prometheus = PrometheusWrapper(prometheus_url, not ignore_tls)

    influx = InfluxWrapper(influx_url, influx_token)

    rules = conf_parser.get_rules()

    for rule in rules:
        query_result = prometheus.query(
            query=rule.query, start=rule.start, end=rule.end, step=rule.step
        )
        if query_result.status_code != 200:
            raise Exception(f"Return code error: {query_result.status_code} != 200")

        json_f = json.loads(query_result.content)

        data = json_f["data"]

        if data["resultType"] != "vector":
            log.warning(
                f"Prometheus query retuned: resultType == {
                    data['resultType']
                } -> NOT TESTED!! BE AWARE!!"
            )

        result = data["result"]

        influx.write(rule.name, result)


if __name__ == "__main__":
    pargs = ArgumentParser("Promflux")

    server_args = pargs.add_argument_group("Server Endpoint")
    server_args.add_argument(
        "prometheus",
        nargs="?",
        help="Addess for the Prometheus server",
    )
    server_args.add_argument(
        "influx",
        nargs="?",
        help="Address for the Influx database",
    )

    settings = pargs.add_argument_group("Setting")
    settings.add_argument("--ignore-tls")
    settings.add_argument(
        "-t",
        "--token",
        type=str,
        help="Influx token",
    )
    settings.add_argument(
        "-f",
        "--file",
        type=str,
        help="Filepath where configuration is located",
    )

    args = pargs.parse_args()
    main(args)
