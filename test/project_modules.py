"""Check project-module order and relative imports: --exe path/to/goose."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True)
    args = parser.parse_args()
    compiler = str(Path(args.exe).resolve())
    stdlib = Path(__file__).resolve().parent.parent / "stdlib"
    with tempfile.TemporaryDirectory(prefix="goose modules ") as directory:
        root = Path(directory)
        first, second, app = (root / name for name in ("first modules", "second", "app"))
        for p in (first, second, app):
            p.mkdir()
        (first / "dep.goose").write_text('import .helper; fn answer() -> i64 { helper() }\n')
        (first / "helper.goose").write_text('fn helper() -> i64 { 42 }\n')
        (second / "dep.goose").write_text('fn answer() -> i64 { "wrong directory" }\n')
        source = app / "main.goose"
        source.write_text('import std; import dep; fn main() { print(answer()); }\n')

        def check(*options, succeeds=True):
            run = subprocess.run([compiler, "--check", "--roundtrip", "--stdlib", str(stdlib),
                                  *map(str, options), str(source)], capture_output=True, text=True)
            if (run.returncode == 0) != succeeds:
                raise AssertionError(run.stdout + run.stderr)

        check("--module-dir", first, "-I", second)
        check(succeeds=False)
        (app / "dep.goose").write_text('fn answer() -> i64 { 7 }\n')
        check("--module-dir", second)
        source.write_text('import std; fn main() { print("ok"); }\n')
        check()
    print("Project module order, root precedence and relative imports passed")


if __name__ == "__main__":
    main()
