from logging import getLogger, DEBUG, INFO, StreamHandler
from os import getenv
from yaml import safe_load
from dataclasses import dataclass
from datetime import datetime
from dateparser import parse


@dataclass
class Rule:
    name: str
    query: str
    start: datetime | None = None
    end: datetime | None = None
    step: str | float | None = None

    def __init__(self, name, query, start=None, end=None, step=None):
        self.name = name
        self.query = query

        if start is not None:
            self.start = parse(start)

        if end is not None:
            self.end = parse(end)

        self.step = step


class RuleParser:
    """
    Classe che si occupa di interpretare le regole scritte in YAML

    :param str path: Path dove si trovano le regole. \
    Intese come query
    """

    def __init__(self, path: str):
        self.log = getLogger(__name__)
        self.log.setLevel(DEBUG if getenv("DEBUG", 0) else INFO)
        self.log.addHandler(StreamHandler())

        self.path = path
        self.log.debug(path)

    def get_rules(self) -> list[Rule]:
        """
        Funzione che interpreta il file .yaml

        :return list[Rule]: Lista che contiene oggetti di tipo rule
                che sono @dataclass interpretate dal file
        """

        with open(self.path) as file:
            yaml = safe_load(file)

        rules = list()

        for rule in yaml["rules"]:
            rules.append(Rule(**rule))

        return rules
