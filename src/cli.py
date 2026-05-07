import argparse
import subprocess
import sys


def run_train():
    print("Starting model training...\n")

    result = subprocess.run(
        [sys.executable, "src/train_model.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("ERROR:")
        print(result.stderr)


def run_predict(input_file):
    print(f"Running flaky prediction on: {input_file}\n")

    result = subprocess.run(
        [sys.executable, "src/predictor.py", input_file],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("ERROR:")
        print(result.stderr)


def main():
    parser = argparse.ArgumentParser(description="FlakeGuard AI CLI")

    subparsers = parser.add_subparsers(dest="command")

    # TRAIN COMMAND
    subparsers.add_parser("train")

    # PREDICT COMMAND
    predict_parser = subparsers.add_parser("predict")
    predict_parser.add_argument("--input", required=True)

    args = parser.parse_args()

    if args.command == "train":
        run_train()

    elif args.command == "predict":
        run_predict(args.input)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()