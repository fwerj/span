#!/usr/bin/env python
import collections
import datetime
import fire
import random
import toml
import pathlib
import time
import sys


__version__ = "0.1.0"
UNTRACK_TIME = 600  # time after which we consider the experiment as a new one
SLEEP_TIME = 1
STATE_FILE = pathlib.Path().home() / ".local" / "share" / "span" / "state.toml"
HISTORY_FILE = pathlib.Path().home() / ".local" / "share" / "span" / "history.tsv"
if not HISTORY_FILE.exists():
    with HISTORY_FILE.open("w") as fp:
        print(
            "time",
            "correctness",
            "size",
            "name",
            "myanswer",
            "rightanswer",
            "isnew",
            sep="\t",
            file=fp,
        )

OKGREEN = "\033[92m"
FAIL = "\033[91m"
ENDC = "\033[0m"


def _getstate():
    try:
        with open(STATE_FILE, "r") as fp:
            return collections.defaultdict(dict, toml.load(fp))
    except FileNotFoundError:
        return defaultdict(dict)


def _putstate(state):
    STATE_FILE.parent.mkdir(exist_ok=True, parents=True)
    with open(STATE_FILE, "w") as fp:
        toml.dump(state, fp)


def show(start=3):
    """ Show some letters from the alphabet read from stdin.
    The number of letters depends on previous invocation of function"""
    state = _getstate()
    alphabet = "".join(sys.stdin).split()
    if (
        state.get("drop", False)
        or "date" not in state["nextsize"]
        or time.time() > UNTRACK_TIME + state["nextsize"]["date"].timestamp()
    ):
        state["drop"] = False
        print(OKGREEN + "New test" + ENDC)
        size = start
        state["nextsize"]["size"] = size
        state["nextsize"]["date"] = datetime.datetime.now()
        state["new"] = True
    else:
        state["new"] = False
        size = state["nextsize"]["size"]
    answer = []
    for i in range(size):
        if not answer:
            index = random.randrange(len(alphabet))
        else:
            tmp = random.randrange(len(alphabet) - 1)
            index = tmp + 1 if tmp >= index else 0
        answer.append(alphabet[index])
        print("\r" * 20 + answer[-1], end="")
        time.sleep(SLEEP_TIME)
    print("\r" * 20 + " " * 20 + "\r" * 20, end="")
    state["answer"] = answer
    state["checked"] = False
    _putstate(state)


def forward():
    """Prompt to enter the letters from show invocation in forward order.
    Check for correctness and make record in history file."""
    state = _getstate()
    if "answer" not in state or state["checked"]:
        raise RuntimeError("No recorded tests. Run 'show' first.")
    line = input()
    if " " in line or "\t" in line:
        answer = line.split()
    else:
        answer = list(line)
    state["nextsize"]["date"] = datetime.datetime.now()
    if answer == state["answer"]:
        print(OKGREEN + "Right: {}".format(len(state["answer"])) + ENDC)
        state["nextsize"]["size"] += 1
    else:
        print(FAIL + "Wrong: {}".format(len(state["answer"])) + ENDC)
        state["nextsize"]["size"] -= 1
    state["checked"] = True
    _putstate(state)
    _record(state, answer, "forward")


def _record(state, answer, name):
    with open(HISTORY_FILE, "a") as fp:
        print(
            int(time.time()),
            answer == state["answer"],
            len(state["answer"]),
            name,
            "|".join(answer),
            "|".join(state["answer"]),
            state["new"],
            sep="\t",
            file=fp,
        )


check = forward


def new():
    """ Drop caches of previous tests and next show invocation will start new test"""
    state = _getstate()
    state["drop"] = True
    _putstate(state)


def _main():
    fire.Fire()
