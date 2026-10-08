# Proposal: reusable native adapter type declarations

An adapter included with `--include` may define several C wrappers even when
a Goose program calls only one. The generated slice types currently depend
on extern reachability. For example, `sl_f32` exists when an extern taking an
`f32[:]` is called, but can be absent when it is unused. The C compiler parses
the entire adapter header in either case.

Adding a fallback anonymous-struct typedef fixes the unused case but conflicts
with the compiler's declaration in the used case. `test/native_adapter/fixtures`
contains the same adapter and two minimal programs that expose this difference.

This branch prototypes guards around emitted slice typedefs. The macro is
`GS_TYPE_` followed by the generated slice type name. An adapter can then
provide a matching fallback under the same guard, with the same packing:

```c
#ifndef GS_TYPE_sl_f32
#define GS_TYPE_sl_f32
#pragma pack(push, 1)
typedef struct { float *data; int64_t len; } sl_f32;
#pragma pack(pop)
#endif
```

Run the native integration test with:

```sh
python test/check_native_adapters.py --exe path/to/goose
```

The same header compiles and executes with the extern used and unused, at
native optimization levels 0 and 2. To reproduce the original conflict, pass
an original compiler with `--expect-unguarded`.

## Issue for discussion

Suggested issue title: **Provide supported C type declarations for optional extern adapters**

What is the intended supported native binding surface for reusable C
libraries? Could Goose expose documented primitive slice aliases, or generate
a header for a concrete extern surface independently of reachability?

The guard prototype removes duplicate definitions but still depends on
generated names, duplicated layouts and packing conventions. It does not
establish a complete stable ABI or solve nominal-struct naming. The fallback
must match the compiler's representation exactly. A native binding contract
should also specify mutable/read-only slices, ownership and primitive versus
nominal types.

The existing `--header` mode serves C callers of exported Goose functions;
it should not be assumed to generate an extern-import binding surface.
Agree on that interface before treating the guard workaround as the final
solution. This branch is separate from UI changes and module search features.
