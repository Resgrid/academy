# Big Board recording sources

Use the isolated Academy training stack and the Big Board recording launcher in
`../bigboard-20261101`. The app selector is the local Core Big Board selector.
Configure the real OpenWeather provider key privately in Core's
`MappingConfig.BigBoardOpenWeatherApiKey`; no key is shipped with this source.
A local operator can use their `BIGBOARD_OPENWEATHERKEY` environment value.
The browser renders provider forecast data only after the private server setting
is configured.

The weather-alert lesson uses the fictional data in
`../../scenarios/bigboard-weather-alerts-20261103.sql`. Its inactive source
and disabled notification and call integration settings keep the exercise local.
The actual map screens show a change from ten markers to six after filtering.
At the initial fixed zoom the resources lie outside the viewport; a wider fixed
view brings them back and retains the hidden pin labels. The failed label capture
number 007 is historical and is excluded from the lesson.

The timer lesson captures two real transitions. For the first, set a Staging
warning at one minute and alert at two minutes, mute a red alert for fifteen
minutes, and wait for expiry. For the second, set a one-minute warning and
four-minute alert, reset the unit status, and mute the fresh warning for fifteen
minutes. Observe the red alert return before the earlier mute deadline.

The patch compares the original recording sources with the final sources used
for recording. `current-product-and-recording-identities.json` binds the final
copies to the same files in the product repository. The app fixes belong in the
product repository; use this source snapshot to reproduce the lesson.
