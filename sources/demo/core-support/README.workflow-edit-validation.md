# Workflow edit validation support patch

This patch preserves the workflow edit fix used by the expansion recording stack. It contains only the current changes to:

- `Web/Resgrid.Web/Areas/User/Controllers/WorkflowsController.cs`
- `Tests/Resgrid.Tests/Web/User/WorkflowTenantIsolationTests.cs`

The edit form previously failed validation for the server-owned required `CreatedBy` value. The fix permits settings edits while retaining the server-owned values and previously stored steps. The original Core working tree already contains the fix. **Review and apply this patch only in a disposable isolated checkout; never apply it to the user's original Core checkout.**

`workflow-edit-validation.json` records the baseline HEAD, SHA-256 hashes of both baseline and modified files, the patch hash, and the validation provenance. The baseline is `6f83872110b0382f2911d099e95d6a4ef7da8315`. Review the patch and metadata before using it. A different HEAD requires a fresh compatibility review.

From the Academy artifact checkout, set the isolated destination explicitly:

```sh
academy_support_dir="$(pwd)/sources/demo/core-support"
academy_isolated_core="/absolute/path/to/a/disposable/Core-checkout"
git -C "$academy_isolated_core" rev-parse HEAD
git -C "$academy_isolated_core" diff --stat
git -C "$academy_isolated_core" apply --check "$academy_support_dir/workflow-edit-validation.patch"
git -C "$academy_isolated_core" apply "$academy_support_dir/workflow-edit-validation.patch"
```

Use the metadata's per-file hashes to confirm the baseline before applying and the modified result afterwards. If the isolated checkout already has this fix or unrelated local edits to either file, preserve those edits and review the difference first. Application and verification leave the work uncommitted; no staging, commits or pushes are part of this procedure.

The parent recording task reports five new cases and 21 passing `WorkflowTenantIsolationTests`. The host tests used .NET 10 roll-forward because the host lacks the .NET 9 runtime. The updated Docker .NET 9 web application then successfully enabled and saved both fictional workflows. This retention task did not rerun that test suite or browser exercise. It independently verified that the patch passes `git apply --check` against an isolated temporary source tree populated from the baseline HEAD.

The expansion source snapshots are evidence excerpts, not a complete buildable checkout. Acquire a complete Core checkout at the recorded expansion HEAD, review this support patch there, and use the existing isolated recording setup. Neither this patch nor the evidence retention task changes shared `scripts/setup_demo.py`, original evidence, credentials, providers or department data.
