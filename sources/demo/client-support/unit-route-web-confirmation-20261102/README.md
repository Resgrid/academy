# Unit web route confirmation

The isolated Unit-records browser build uses React Native Web, whose Alert.alert does not open a confirmation. The End Route control consequently performed no action. This recording-copy compatibility change presents the same translated confirmation in the existing NativeModal component on web, with explicit Cancel and End Route controls. Both platforms retain the existing store/API action and backend validation. No status is changed by applying this patch.

Before/after source and identities are retained. The original Unit repository and historical native recording copies are untouched. Restart only the owned Unit Metro server with its inherited Mapbox environment and --clear after applying the hash-checked change. Verify cancel, confirm, returned screen and freshly loaded Core history before claiming route completion. No provider geometry, real device location or physical arrival is inferred.
