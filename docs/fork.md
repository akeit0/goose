# Integration toolchain

The `lab-toolchain` branch tracks upstream `4f23f22`.
Routine goose-lab validation uses one upstream-tracking compiler. A second
upstream build is only for a focused reproduction of a relevant fork difference.
The typechecker, optimizer, ownership and slice-pool runtime are upstream code.
The implicit inline-return correction is upstream in PR #11 (`e7792d7`).

## Remaining extensions

* Repeated, ordered `--module-dir directory` / `-I directory` for project imports.
  Package-local files and explicitly declared packages retain upstream semantics;
  project roots precede standard-library roots. Relative imports resolve next
  to the importing file.
* `GS_TYPE_<slice name>` guards allow optional native headers to provide primitive
  slice declarations without duplicate typedefs. Slice representation is unchanged.
* CMake package source paths resolve relative to the compiler's own CMake module,
  allowing the compiler to be embedded in a consuming project's build.
* Visual Studio discovery includes Build Tools installations and rejects failed
  environment initialization in the Python test tooling.

Graphics, audio, UI and physics are external upstream packages. The compiler's
normal build has no SDL dependency and no builtin native packages. Goose-lab directly maintains graphics package source derived from
`aardappel/goose_gfx`, including its input/presentation extensions and regressions;
no native graphics source or lab graphics fixture remains in this compiler fork.
TinyCC is vendored by upstream and always built for JIT support.

## Checks

Build with upstream's normal CMake instructions, then run:

```text
python test/project_modules.py --exe /path/to/goose
python test/native_adapters.py --exe /path/to/goose
```

Goose-lab runs its own core/GUI probes, native adapter and application contracts.
For graphics changes, rebuild both its generated Goose C and patched native
package; the text-transaction extension changes the event representation.
See upstream's testing guide for compiler baseline and JIT coverage.
