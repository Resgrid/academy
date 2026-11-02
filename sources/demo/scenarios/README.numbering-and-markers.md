# Replay the numbering recording scenario

[numbering-and-markers.json](numbering-and-markers.json) retains the public fictional
form values and dated observed results. It contains no credentials or stored
credential material. This recipe is separate from the run-card/workflow configuration
bundle because issuing a work request is an ordinary application operation.

Use only an isolated expansion-profile stack with database `resgrid_academy`,
department 51 **Firehouse 51 — Training Department**, and the six named training
units. Resolve names inside that department; observed IDs are not import IDs.
Inspect existing settings/items before any save. Preserve different existing data,
issued counters, calls and history. There is no automatic replay or database writer.
The source profile recreates sources and baseline startup, not mutable recording state.

1. In Department Settings, expand **Calls & Dispatch**, then **Call Settings**.
   Review the saved `FD51-{YYYY}-{SEQ}`, four digits and January 1. On an existing
   recording stack, leave **Raise next sequence to** blank and do not resubmit to
   force a photographed next value. The first new-scope value was 0001; the separate
   Responder exercise actually issued `FD51-2026-0001`, leaving next 0002.
2. Under Department Settings **Customization**, open **Document Numbering**.
   On a fresh authorized fictional replay only, enter the fixture's work-order
   pattern and four digits, keep January 1 and every other kind unchanged, then
   **Update**. Reopen and compare. Leave **Raise next to** blank. Inline examples use
   sample sequence 153 and are distinct from actual next values.
3. If explicitly practicing issuance, first search Work orders for the exact fixture
   title. Reuse an exact existing matching item; stop on different or duplicate
   content. Otherwise choose **New work order**. In **Describe the work**, enter the
   fixture title/description, **Other**, **Low**, no due date. Continue through
   **What it is for** with no unit/group/site; **Cost and vendor** with no costs or
   vendor; and **Safety and procedure** with no safety flags, references or task
   steps. Review all fields, then save once. Reopen using the actual register link.
   The observed result was **Requested**, `MNT-26-0001`. It is not a completed repair,
   inspection, financial approval or safety clearance. The actual returned number
   on any new replay is authoritative. Do not alter status or manufacture history.
4. Reopen Document Numbering. The recorded next value after that request was
   `MNT-26-0002`; older `WO-2026-*` numbers remained. Never reset a counter to obtain
   these strings on another stack.
5. In Records, expand **Manage** → **Settings**. Review the preserved pattern,
   four digits, January 1, blank Training prefix override (default **TRN**) and
   existing `TRN-2026-0001` Finalized record. The recorded next was 0002. This step
   performs no save, lifecycle action, disclosure, export or approval.
6. Custom marker assets and planned targets are retained in the fixture. Their
   upload is still blocked by the active Chrome extension's explicit file-URL
   capability rejection. All retained current icon screenshots are baseline
   built-in pins and default previews. Resume only after normal supported upload
   capability is available; never substitute a fixture or illustrated map as proof.

For text fields backed by change handlers, finish typing and leave the field before
saving. Always confirm the redirect and reopened values. Selecting a file or seeing
an inline preview does not prove a saved result. No import, GPS permission, MFA,
provider connection, call creation/closure or counter reset belongs to this recipe.
