import json
import dateparser
from argparse import ArgumentParser, Namespace
from Wrappers import PrometheusWrapper, RuleParser


def main(args: Namespace):
    prometheus = PrometheusWrapper(args.prometheus, True)

    conf_parser = RuleParser(args.file)
    rules = conf_parser.get_rules()
    print(f"Rules Found: {len(rules)}\n")
    print("-" * 8)

    for rule in rules:
        print(f"Rule: {rule.name}")
        print(f"query: {rule.query}")
        print(f"start {rule.start} - end {rule.end} - step {rule.step}")

        query_result = prometheus.query(
            query=rule.query,
            start=rule.start,
            end=rule.end,
            step=rule.step,
        )
        if query_result.status_code != 200:
            raise Exception(f"Return code error: {query_result.status_code} != 200")

        json_f = json.loads(query_result.content)
        data = json_f["data"]
        print()
        print("Raw result: ", data)

        results = data["result"]
        for result in results:
            for value in result["values"]:
                value[0] = str(dateparser.parse(f"{value[0]}"))

        print("Result    : ", data)
        print("-" * 8)


if __name__ == "__main__":
    pargs = ArgumentParser("Promflux")
    pargs.add_argument(
        "prometheus",
        help="Addess for the Prometheus server",
    )
    pargs.add_argument(
        "-f",
        "--file",
        type=str,
        default="rules.yaml",
        help="Filepath where configuration is located",
    )

    args = pargs.parse_args()
    main(args)
