"""Compile optional slice adapters with and without a live slice use."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import toolchain as tc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True)
    args = parser.parse_args()
    tc.setup_console()
    compiler = str(Path(args.exe).resolve())
    cc = tc.test_cc("native")
    with tempfile.TemporaryDirectory(prefix="goose adapter ") as directory:
        root = Path(directory)
        header = root / "adapter.h"
        header.write_text('''#ifndef GS_TYPE_sl_f32
#define GS_TYPE_sl_f32
typedef struct { float *data; int64_t len; } sl_f32;
#endif
static int64_t adapter_count(sl_f32 values) { return values.len; }
static int64_t adapter_marker(void) { return 7; }
''')
        for uses_slice in (False, True):
            source = root / "main.goose"
            body = 'var values: f32[2] = [1.0, 2.0]; print(count(values));' if uses_slice else 'print(marker());'
            source.write_text('import std;\nextern "adapter_marker" fn marker() -> i64;\n'
                              'extern "adapter_count" fn count(values: const f32[:]) -> i64;\n'
                              'fn main() { ' + body + ' }\n')
            generated, executable = root / "main.c", root / ("main" + tc.EXE_SUFFIX)
            subprocess.run([compiler, "--stdlib", str(ROOT / "stdlib"), "--standalone",
                            "--include", str(header), "-o", str(generated), str(source)], check=True)
            ok, log = cc.compile(generated, executable, opt=2, strict_decls=True)
            if not ok:
                raise AssertionError(log)
            run = subprocess.run([str(executable)], capture_output=True, text=True, check=True)
            assert run.stdout.strip() == ("2" if uses_slice else "7"), run.stdout
    print("Optional adapter and generated slice declarations passed")


if __name__ == "__main__":
    main()
