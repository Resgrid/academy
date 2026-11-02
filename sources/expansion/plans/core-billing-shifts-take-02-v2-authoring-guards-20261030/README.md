# Billing and Shifts take 02: v2 final-input author

Use `sources/production/author_core_billing_shifts_take_02_20261030_v2.py`
for future explicit assembly. The original author and all of its input pins are
retained. V2 additionally pins the original author hash and writes only NEW
`-take-02-final-inputs-20261030-v2` packages.

The original Shifts author produced six scene instruction digests that differed
when the actual renderer expanded the identical SRT. The cause is a binary
floating-point addition-order difference after one minute, not changed speech.
V2 checks identical real words and a difference below one nanosecond, then uses
the renderer's own explicit-millisecond SRT parser before binding the instruction
digest. Source containment uses that same tiny arithmetic tolerance. No explicit
SRT time, source span, caption word, audio or recorded image has been changed.

Default invocation validates sources and actual audio read-only. Actual final
assembly still requires one named lesson, `--assemble`, and
`--listening-review-sha256` for its genuine User hearing receipt. Optional
`--listening-review-file` follows the same existing safe public-relative path
rules. Root timing and proposal identities remain pinned exactly as in v1.

```sh
python3 -B sources/production/author_core_billing_shifts_take_02_20261030_v2.py
python3 -B -m unittest discover -s sources/production/tests -p test_core_billing_shifts_take_02_authoring_guards_v2.py
```

Nineteen focused tests pass. They reproduce the six original Shifts differences,
verify every v2 Billing and Shifts scene against actual renderer expansion,
reject a changed real word or millisecond, retain genuine-hearing checks, and
verify default execution does not render or author final inputs. Only the
stdlib SRT parser is used on default preflight; optional media libraries and
rendering/strict-final-validation entrypoints are not called.

This package is source preparation. It supplies no hearing receipt, final plan,
render, encoded-frame review, browser playback, canonical readiness, deployment,
app operation or Git action. The actual User listening reviews remain pending.
