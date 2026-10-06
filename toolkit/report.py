"""Collects problems found while drawing (like a hand that can't reach its target).

Problems are printed as they happen. The render script switches printing off
in its helper processes and prints one tidy summary at the end instead.
"""
import sys

ECHO = True
_problems = []


def problem(message: str):
    _problems.append(message)
    if ECHO:
        print(f"WARNING: {message}", file=sys.stderr)


def take():
    """Return and clear everything reported so far."""
    out = list(_problems)
    _problems.clear()
    return out
