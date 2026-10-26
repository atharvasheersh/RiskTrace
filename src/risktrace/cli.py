"""Command entry point; subsequent stages register download and audit routines."""
import argparse
from .core import config, report_dates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-config"])
    args = parser.parse_args()
    spec = config()
    if args.command == "check-config":
        dates = report_dates(spec["start"], spec["end"])
        assert len(dates) == 64
        print(f"Valid contract: {len(dates)} quarters, {len(spec['api']['financial_fields'])} financial fields")


if __name__ == "__main__":
    main()
