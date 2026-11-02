# IC web camera compatibility for Academy recordings

This version retains the earlier Text DOM, native Camera defaults and Metro symlink compatibility, then fixes two web adapter boundaries: the native Camera ref now exists before style load and retains the latest source-specified recenter request; camera-change callbacks report actual map center and zoom. Ordinary layers wait for style readiness. Finite optional camera fields preserve zero values and omit undefined keys.

The old package directly under client-support remains unchanged as recording history. The versioned baseline pins the original IC revision and all six patched files. The patch applies only to a fresh isolated source copy, with original dependencies linked read-only. The launcher uses ordinary development mode with a local Metro cache reset, fictional loopback API, disabled analytics, and untouched inherited map credentials; it never prints credentials.

Verification performed: fresh isolated preparation, all six file hashes, full TypeScript no-emit check with zero diagnostics, Text DOM server-render tests, native-default tests, and actual React ref/effect tests with a mock map. Tests cover pre-load queue survival, latest request precedence, unchanged Camera mount across readiness, deferred layers, real center/zoom values, invalid coordinates, optional fields and zero durations. React test renderer emits its own deprecation notice.

Visual/runtime result remains pending actual browser review. These source tests do not establish Mapbox provider success, incident-map Save View persistence, GPS/device permissions, native hardware, or annotation operations. No browser or app UI was started by this preparation.
