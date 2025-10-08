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
            raise Exception(
                f"Return code error: {query_result.status_code} != 200\n{
                    json.loads(query_result.text)['error']
                }"
            )

        json_f = json.loads(query_result.content)
        data = json_f["data"]
        print()
        print("Raw result: ", data)

        # update data object (using reference)
        results = data["result"]
        for result in results:
            for value in result["values"]:
                value[0] = str(dateparser.parse(f"{value[0]}"))

        print("Result    : ", json.dumps(data, indent=4) if args.pretty else data)
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
    pargs.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="Prettify json prints",
    )

    args = pargs.parse_args()
    main(args)
