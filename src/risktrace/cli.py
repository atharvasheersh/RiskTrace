"""Command entry point; subsequent stages register download and audit routines."""
import argparse
from .core import config, report_dates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-config", "pilot-data"])
    args = parser.parse_args()
    spec = config()
    if args.command == "check-config":
        dates = report_dates(spec["start"], spec["end"])
        assert len(dates) == 64
        print(f"Valid contract: {len(dates)} quarters, {len(spec['api']['financial_fields'])} financial fields")
    elif args.command == "pilot-data":
        from .data import collect
        summary = collect("pilot")
        print({k: summary[k] for k in ["rows", "banks", "distinct_positive_banks", "label_cutoff"]})


if __name__ == "__main__":
    main()
