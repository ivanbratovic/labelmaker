#!/usr/bin/env python

"""
Generates Traefik labels for use in e.g. Docker containers.
"""

from typing import *
from util.label import *
from util.formatter import *

import readline
import argparse

__author__ = "Ivan Bratović"
__copyright__ = "Copyright 2021, Ivan Bratović"
__license__ = "MIT"

__version__ = "0.0.1"

FORMATS = ["none", "docker", "compose"]


def has_yaml_extension(path: str) -> bool:
    basename = path.split("/")[-1].strip()
    if basename[-4:].lower() == ".yml":
        return True
    if basename[-5:].lower() == ".yaml":
        return True
    return False


def main() -> None:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate Traefik labels")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="use interactive mode",
    )
    parser.add_argument(
        "-d",
        "--docker-compose",
        metavar="FILE",
        help="generate labels from a given Compose file",
    )
    parser.add_argument(
        "-c",
        "--container",
        metavar="NAME",
        help="generate labels for a given container on the system",
    )
    parser.add_argument(
        "-f",
        "--format",
        metavar="FORMAT",
        help=f"set output format, one of: [{', '.join(FORMATS)}]",
        choices=FORMATS,
        default="none",
    )

    args, unknownargs = parser.parse_known_args()

    formatter: Callable[[List[str]], str] = globals()[f"formatter_{args.format}"]
    labels: List[str] = []

    if args.interactive:
        assert False, "Interactive mode is not implemented yet"
        # Initialize readline interface
        HISTORY_FILE = ".laebelmaker_history"
        readline.set_history_length(1000)
        try:
            readline.read_history_file(HISTORY_FILE)
            HISTORY_LEN = readline.get_current_history_length()
        except FileNotFoundError:
            open(HISTORY_FILE, "wb").close()
            HISTORY_LEN = 0
        readline.write_history_file(HISTORY_FILE)
    if args.docker_compose:
        try:
            labels += gen_label_set_from_compose(args.docker_compose)
        except NoInformationException:
            print("Invalid docker-compose file given.")
    if args.container:
        try:
            labels += gen_label_set_from_container(args.container)
        except NoInformationException:
            print("Invalid container identifier given.")
    if unknownargs:
        for arg in unknownargs:
            if has_yaml_extension(arg):
                try:
                    labels += gen_label_set_from_compose(arg)
                except NoInformationException:
                    print("Unkown YAML file path: ", arg)
                    raise
            else:
                print("Unkown argument given: ", arg)

    if labels:
        print("-- START GENERATED LABELS --")
        print(formatter(labels), end="")
        print("-- END GENERATED LABELS   --")
    else:
        print("No arguments given.")
        parser.print_help()


if __name__ == "__main__":
    main()
