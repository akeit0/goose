# Integration toolchain

The `lab-toolchain` branch extends upstream revision
`2ec9b38bde93cda87ee374157b0353722b2d5f8e`.
It supports external libraries and application input/rendering needed by goose-lab.
Language ownership, worker isolation and explicit resource cleanup remain unchanged.

Routine goose-lab validation uses this upstream-tracking toolchain. A second
upstream-only build is reserved for a minimal reproduction of a specific fork
difference, rather than repeating the same suite on both checkouts. The fork
changes are module search, C adapter guards, opt-in gfx integration and tooling;
slice-pool allocation and storage semantics come directly from upstream.

## Capabilities

| Area | Extension | Boundary |
| --- | --- | --- |
| Project imports | Repeatable `--module-dir directory` / `-I directory` | Root-file directory wins, then project roots in argument order, then standard-library roots; relative imports stay relative to the importing file |
| C adapters | `GS_TYPE_<slice name>` guards around generated slice typedefs | An optional header can supply a missing declaration without duplicate typedefs; slice representation is unchanged |
| Rendering | `present_on_demand`, `request_present`, screen/content revisions | Opt-in; idle polling avoids presentation/submission, screen render passes invalidate automatically, other screen writers must explicitly request presentation |
| Text input | `text_transactions`, preedit/commit events, `text_event_into`, caret area | Opt-in; legacy clients keep scalar events; UTF-8 payload tokens expire at next frame or close, with a lazy 64-KiB frame arena and zero token on overflow |
| Window close | `defer_close`, `EVENT_CLOSE_REQUESTED` | Opt-in; the app can save/discard/cancel before calling `quit`; default close behavior is unchanged |
| Input fixtures | Ordered wheel, preedit and close injection | Test helpers exercise the same event queue as platform input |

Compiler, `stdlib/gfx.goose` and the native gfx archive must come from the same
checkout: transaction metadata extends the event representation. Recompile
generated C and native libraries when switching toolchains. IME payloads are
copied into Goose while their frame token is live; native code retains no Goose
references. Destructors and escaping callbacks are not required.

Each feature has its own commit and focused check, so an upstream proposal can
be reviewed independently. The Visual Studio discovery fix is a separate tooling
commit. There are no changes to the upstream Nuklear/UI implementation and no
compiler-baked source path for standard-library discovery; external builds pass
the existing `--stdlib` option explicitly.

## Build and check

Build with upstream's normal CMake instructions. Initialize the SDL submodule
and enable `GOOSE_GFX` to execute graphics checks. The scripts accept an explicit
compiler path and use this checkout's stdlib.

```powershell
python test/project_modules.py --exe build/Release/goose.exe
python test/native_adapters.py --exe build/Release/goose.exe
python test/api_check.py gfx
python test/run_tests.py --exe build/Release/goose.exe --profile baseline --cc msvc --no-jit
```

Use `--cc native` on other platforms. If the compiler was built outside the source
tree, set `GOOSE_STDLIB` to this checkout's `stdlib` for the general test runner.
The new gfx fixtures run through the existing runner at native -O0/-O2 and check
event ordering, legacy behavior, token expiry, deferred close and idle submissions.
Headless checks need a GPU. Native IME candidate placement and OS expose/resize
behavior require manual window checks. See [testing](testing.md) for baseline,
JIT, optional native layers and bootstrap coverage.
