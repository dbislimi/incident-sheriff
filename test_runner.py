import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CURRENT_DIR / "output"
CPP_DIR = CURRENT_DIR / "cpp"
BUILD_DIR = CPP_DIR / "build"


@dataclass
class TestFile:
    ticket_name: str
    run_id: str
    test_path: Path


def get_tests():
    tests: list[TestFile] = []

    if not OUTPUT_DIR.exists():
        print("Error: output directory does not exist.")
        return tests

    for ticket_dir in sorted(OUTPUT_DIR.iterdir()):
        if ticket_dir.is_dir():
            for run_dir in sorted(ticket_dir.iterdir()):
                test_file = run_dir / "rebooking_test.cpp"
                if test_file.exists():
                    tests.append(
                        TestFile(ticket_dir.name, run_dir.name, test_file.resolve())
                    )

    return tests


def compile(test_file: Path):
    subprocess.run(
        ["cmake", "-S", str(CPP_DIR), "-B", str(BUILD_DIR), f"-DTEST_SOURCE_FILE={test_file.resolve()}", "-DDISCOVER_TESTS=ON"],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(BUILD_DIR)], check=True)
    subprocess.run(["ctest", "--output-on-failure"], cwd=BUILD_DIR, check=True)


if __name__ == "__main__":
    tests = get_tests()
    if not tests:
        sys.exit(1)

    for i, test in enumerate(tests):
        print(f"[{i}] {test.ticket_name} -> Run: {test.run_id}")

    choice = input(f"Choose a file to execute (0-{len(tests)-1}) or -1 for latest: ")

    try:
        index = int(choice)
        if index == -1:
            test = max(tests, key=lambda item: item.run_id)
        elif 0 <= index < len(tests):
            test = tests[index]
        else:
            raise ValueError("Selection out of range")
        print(f"You chose {test.ticket_name} -> Run: {test.run_id}")
        compile(test.test_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
