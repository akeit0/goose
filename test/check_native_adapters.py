"""Compile one optional native adapter with its extern used and unused.

python test/check_native_adapters.py --exe build/Release/goose.exe
Uses the repository toolchain helpers; no graphics or native dependencies.
--expect-unguarded reproduces the original compiler's conflicting typedef.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import toolchain as tc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--cc", help="C compiler executable, e.g. cl or clang")
    parser.add_argument("--expect-unguarded", action="store_true")
    options = parser.parse_args()
    compiler = options.exe.resolve()
    if options.cc:
        style = "msvc" if Path(options.cc).stem.lower() in ("cl", "clang-cl") else "gcc"
        cc = tc.CC("adapter", options.cc, options.cc, style, options.cc)
    else:
        cc = tc.test_cc()
    if not cc:
        parser.error("No C compiler available; run in a developer shell or pass --cc")
    fixtures = ROOT / "test/native_adapter/fixtures"
    with tempfile.TemporaryDirectory(prefix="goose native adapters ") as directory:
        work = Path(directory)
        for usage in ("used", "unused"):
            generated = work / (usage + ".c")
            emitted = subprocess.run([str(compiler), "--stdlib", str(ROOT / "stdlib"),
                                      "--standalone", "--include", str(fixtures / "adapter_guarded.h"),
                                      "-o", str(generated), str(fixtures / ("slice_" + usage + ".goose"))],
                                     cwd=work, capture_output=True, text=True, errors="replace")
            assert emitted.returncode == 0, emitted.stdout + emitted.stderr
            for level in (0, 2):
                executable = work / (usage + "-O" + str(level) + tc.EXE_SUFFIX)
                extra = ["/MT", "/utf-8"] if cc.style == "msvc" else []
                ok, diagnostics = cc.compile(generated, executable, opt=level, extra=extra)
                if options.expect_unguarded and usage == "used":
                    assert not ok and "sl_f32" in diagnostics, diagnostics or "Expected the original compiler's typedef conflict"
                    print(f"{usage} O{level}: original typedef conflict reproduced")
                    continue
                assert ok, diagnostics
                result = subprocess.run([str(executable)], cwd=work, capture_output=True,
                                        text=True, errors="replace")
                assert result.returncode == 0, result.stdout + result.stderr
                expected = "3.0" if usage == "used" else "No native sum call"
                assert result.stdout.strip() == expected, result.stdout
                print(f"{usage} O{level}: native output matches")


if __name__ == "__main__":
    main()
