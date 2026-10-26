"""Command entry point; subsequent stages register download and audit routines."""
import argparse
from .core import config, report_dates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-config", "pilot-data", "audit", "collect-half", "verify-integration"])
    parser.add_argument("--file", help="Incoming raw-schema CSV for integration checks")
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
    elif args.command == "audit":
        from .audit import run_audit
        print(run_audit().to_string(index=False))
    elif args.command == "collect-half":
        from .data import collect
        summary = collect("full")
        print({k: summary[k] for k in ["rows", "banks", "quarters", "distinct_positive_banks"]})
    elif args.command == "verify-integration":
        if not args.file:
            parser.error("verify-integration requires --file")
        from .data import verify_integration
        print(verify_integration(args.file))


if __name__ == "__main__":
    main()
