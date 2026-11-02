# Static shift recording support

The current Core static-shift Edit view omitted the full-width styling used by New. Select2 collapsed the initially empty unit selector to a few pixels. The retained one-line patch makes the actual Edit control readable without changing its selections, assignment behavior or permissions.

The patch was built through the regular Resgrid.Web publish and verified through the normal training UI. The Edit warning still applies: updating recreates assignments and signups using the submitted settings, so review and reselect every unit to retain before updating.

Apply only to a matching checkout after checking the patch with `git apply --check`; rebuild the normal recording stack. The actual source is `Web/Resgrid.Web/Areas/User/Views/Workshifts/Edit.cshtml`. No browser-injected CSS or fabricated screenshots are used.
