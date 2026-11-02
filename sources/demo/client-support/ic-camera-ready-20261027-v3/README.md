# IC web camera compatibility v3

This separate version retains v2 Text DOM, native default settings, pre-load Camera refs and actual center/zoom callbacks. It adds the existing Unit web adapter’s Mercator projection handling at construction and style load. It also waits until initial camera placement succeeds before flushing the latest queued source request, and treats defaultSettings as initial values rather than later controlled updates.

The regression is concrete in source tests: v2 with a failed first projection initialization invokes fallback jumpTo, incident easeTo, then delayed fallback jumpTo. V3 invokes initial attempts before the latest incident request. Both versions’ actual mocked call sequences and source hashes are retained in regression-before-after.json. This does not prove that the same failure caused the observed browser framing problem.

Native source files, original repositories, provider settings and department coordinates are unchanged. No cartography, GPS fix or movement result is invented. Existing v2 package and earlier media/capture proofs remain intact.

Use the versioned preparer with explicit --source and a fresh --destination. It refuses changed source hashes, revisions or nonempty targets and links existing dependencies. Use the versioned verifiers on that target, then full TypeScript no-emit. Normal development mode with --clear, inherited IC_MAPBOX_PUBKEY, fictional local API and disabled analytics are retained. Never print map credentials.

The actual browser checkpoint now passes initial Chicago incident framing, normal user pan, Save View and persistence after route reopening and full browser reload. See runtime-validation-20261027.json and HANDOFF.md for exact reviewed source hashes and limits. The old Metro listener was in CI mode with reloads disabled; only the rebuilt v3 session establishes the current UI behavior. This does not prove the cause of older framing failures.

Annotation tap handling remains absent from the web adapter; Line/Area/Text visibility is not drawing proof. No native device/provider behavior or multi-user saved-view synchronization was tested. The source-only checkpoint does not make an entire lesson ready for export.
