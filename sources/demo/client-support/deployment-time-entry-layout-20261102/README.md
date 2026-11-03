# Deployment time-entry readability

The real Core time-report form allowed datetime inputs to consume nearly all of its table width, collapsing the Subject and Entry type selectors. This narrowly scoped Razor layout patch wraps that existing table in the theme’s horizontal scroll container and gives its existing columns readable widths.

No fields, posted names, precision, calculations, permissions, validations or approval logic change. Scroll horizontally to review the remaining time, break, distance and note columns. The Academy captures use the normally compiled local training application with this patch, rather than altered screenshots or injected page styles.

Apply this patch to the matching checkout before a normal Docker-configuration web publish. Retain the prior web build and the local training database; no reseeding or migrations are required for this layout change. Successful build and actual UI verification are recorded separately after they occur.

The companion expense-form layout gives the date enough room and moves Currency to its own labeled row. Its existing values and submission names remain unchanged. The final two-view patch is `readable-entry-and-expense-controls.patch`; the first table-only patch is retained as production history.

The final `readable-deployment-form-controls.patch` also gives Max days its own labeled row on New/Edit deployment; its value, constraints and submission name are unchanged. This prevents the former one-column control from collapsing. All three changes are real application layout improvements and require an ordinary web build.
