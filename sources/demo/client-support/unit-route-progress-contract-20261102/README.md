# Unit route-progress response contract

The current Core GetRouteProgress endpoint returns Data.Instance plus progress counts and stops. The recording client's model incorrectly declared Data as a bare instance, and its poll overwrote activeInstance with that wrapper. After Start Route (whose URL has no instanceId), this erased the resolved ID and Directions performed no action. The retained patch types the envelope and stores Data.Instance. It uses the same authenticated API and changes no server status or permissions.

Apply the before/after hash-checked changes only to the isolated Unit-records copy. The original Unit repository and historical native recordings are untouched. The contract regression runs the actual transpiled store against the Core response shape and real installed Zustand. Restart the owned Metro server with inherited environment and --clear, then verify the normal start/reopen/directions workflow. Keep keys and login credentials outside the source package.
