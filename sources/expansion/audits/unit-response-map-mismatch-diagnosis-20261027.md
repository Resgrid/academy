# Unit interactive map mismatch — source diagnosis

Original021 is retained as failed mapping evidence: Nevada/western-US cartography and marker disagree with the Chicago address. It is excluded from successful lesson proof. Inline Static Images uses the supplied coordinate directly and shows Chicago.

The confirmed defect is in Unit’s web Camera adapter: all four option paths include optional `zoom`, `bearing`, or `pitch` keys even when undefined. Installed MapboxGL3.18.1 uses property-presence checks and numeric coercion, producing NaN. Omitting a missing key preserves the existing value; valid zero is retained. The wrapper marks initialization before moving and swallows projection errors, so a failed move can leave fallback framing. FullScreenMap correctly passes the same coordinate to Camera and annotation; no intentional Nevada target exists there.

Offline evidence: the actual installed SDK16-case probe produces8 nonfinite original results and0 proposed results. Ten real Camera/ReactDOM/MapContext regressions produce original5fail/5pass and proposed10pass. These test numeric option handling, not GPU/cartography or animation success. Undefined center is separately safe: jumpTo ignores it and easeTo falls back to previous center.

The unchanged repository Jest harness aborts before tests because `react-native-permissions` is missing from the current installation. No install or setup edit was performed. The isolated jsdom harness used existing installed dependencies.

The reviewable unified patch is `_reports/Unit-camera-optional-values-20261027.patch`, limited to the four numeric option objects and the colocated regression. This agent has not applied it to Unit. A real parent UI retest is still required; this diagnosis does not declare the Nevada problem fixed.

## Unsaved create-form safety

Typing GPS text alone does not set `selectedLocation`; the full-screen picker initially receives no supplied point. The real GPS magnifier parses and stores the entered point even if reverse-address lookup warns. Its callback writes the visible six-decimal GPS string, hidden latitude/longitude and selectedLocation. Create uses those stored values; the text field alone is insufficient.

Close a full-screen picker with its X without Set Location. The inline picker has no own dismiss control: leave the map and Confirm Location untouched and scroll past it, or Cancel the whole unsaved form. Never choose My Location or grant device permissions. Verify the actual formatted input/address and subsequently saved location through ordinary UI before claiming a stored exercise point. Wrong interactive cartography remains a capture gap.

Exact source/SDK/probe/patch/image hashes and acceptance criteria are in the adjacent JSON. No browser, database, provider or app source mutation was performed.
