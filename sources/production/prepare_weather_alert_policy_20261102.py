"""Freeze actual saved weather policy controls; no live-feed result is inferred."""
import json
from prepare_records_reports_exports_20261102 import LESSONS, S, freeze, sha

NAME = 'core-weather-alert-policy'
LESSONS['weather-policy'] = dict(
    name=NAME, raw='core-weather-alert-policy-20261102', route='/User/WeatherAlerts/Settings',
    title='Set weather-alert display and notification policy',
    summary='Review severity and delivery-hour controls, save a display threshold, verify the stored policy, and distinguish policy from an active weather feed.',
    audience=['Department administrators', 'Operations supervisors', 'Weather-alert coordinators'],
    prerequisites=['Authorized access to Weather Alerts and its Settings page in a separate fictional training department.',
                   'Department agreement on weather-alert display, notifications and call context before operational enablement.'],
    sector_scenario='Agree appropriate severity, delivery windows and call-context policy, verify saved settings, and separately validate the source and operational alert results.',
    scope='Only the disabled notification policy was changed and reopened. Minimum Severity to Display changed Moderate to Severe, saved successfully, and retained Severe after reload; it was then restored to Moderate, saved with visible success and independently reopened. Global alerts, all five auto-message severity enables and call integration remained unchecked. Extreme hours18to6, other rows0to24 and the fictional excluded title were retained and read back. No source was added or activated. The Add/Edit Source form has a default checked Active field but is unsaved and has no configured source; it is never called an enabled feed. Existing Guid source/zone materialization failure remains unresolved outside this policy-only exercise. No live weather receipt, display filtering effect on real alerts, message delivery, call-note creation, zone management or forecast result is claimed.',
    excluded={},
    scenes=[
        ('Open Weather Alerts settings', [1, 2], ['Weather Alerts', 'Settings', 'Active Weather Alerts', 'Notification Settings'],
         'Open your department’s Weather Alerts page, then select Settings beside View History. This training department currently says there are no active weather alerts. The Settings page opens Notification Settings, which describes the controls for automatically generating messages to department members. This lesson prepares and checks those policy settings. Practice in a separate training department before changing how a live team receives information.'),
        ('Choose the display threshold deliberately', [2, 3], ['Enable Weather Alerts', 'Minimum Severity to Display', 'Moderate', 'Severe'],
         'Review Enable Weather Alerts and Minimum Severity to Display. The enable checkbox stays clear throughout this exercise. Change the display selection from Moderate to Severe. The help below says that only alerts at or above the selected severity will be shown in the dashboard. This is the display threshold. The separate table below controls which severities generate automatic messages, so review both areas when deciding your department’s policy.'),
        ('Understand severity delivery windows', [5], ['Auto-Message Severity Threshold', 'Extreme', 'Severe', 'Moderate', 'Minor', 'Unknown', 'Enabled', 'Start Hour', 'End Hour'],
         'Scroll to the complete Auto-Message Severity Threshold table. It provides Extreme, Severe, Moderate, Minor and Unknown rows, each with its own Enabled checkbox, Start Hour and End Hour. Every Enabled box remains clear here. The Extreme row contains eighteen and six: the help explains that this wraps overnight, from six P M to six A M in department local time. Delivery includes the start hour and excludes the end hour. Zero and twenty-four represent all-day delivery. Entered hours alone do not check a row’s Enabled box.'),
        ('Separate event exclusions from display', [4], ['Excluded Alert Events', 'TRAINING ONLY - Practice alert'],
         'Review Excluded Alert Events below the table. The help asks for a comma-separated list of event titles that should not generate automatic messages, and says those alerts can still appear in the dashboard. This example retains only a clearly fictional Practice alert title. Treat exclusion as a deliberate messaging decision, not as a way to remove an alert from every view. Agree the appropriate event titles with your department before changing a live policy.'),
        ('Review the call-context option', [4], ['Attach Weather Context to Calls', 'Save Settings'],
         'Below the exclusions, find Attach Weather Context to Calls. Its help says that enabling it attaches active weather alerts near a call’s location as a call note. Keep it unchecked in this training exercise. Consider whether that context belongs in your department’s incident record and review the resulting notes when you test an operational configuration. This recording changes no call notes; it shows the actual option and its stated purpose.'),
        ('Save and verify the stored threshold', [6, 8], ['Save Settings', 'Minimum Severity to Display', 'Severe', 'Enable Weather Alerts'],
         'Select Save Settings for the prepared policy. Reload Settings and look at Minimum Severity to Display again: Severe remains selected. Enable Weather Alerts is still unchecked. That fresh readback confirms the threshold was stored beyond the earlier unsaved dropdown choice. It does not demonstrate a received weather alert or a delivered message. Verify the saved controls and any operational results separately.'),
        ('Restore and reopen the training policy', [9, 10, 11, 12, 13, 14], ['Moderate', 'Save Settings', 'Settings saved successfully.', 'Auto-Message Severity Threshold', 'Excluded Alert Events', 'Attach Weather Context to Calls'],
         'Return the display selection to Moderate and select Save Settings again. The page shows Settings saved successfully beside the button. Reload once more: Moderate is retained, and global Enable Weather Alerts remains clear. Scroll through the full severity table to confirm its unchecked rows and retained hours. Then review the unchanged fictional exclusion and unchecked call-context control. This leaves the original disabled training policy in place.'),
        ('Validate the feed separately for your department', [7], ['Alert Sources', 'No weather alert sources configured. Add a source to start receiving weather alerts.'],
         'The Alert Sources notice says no weather alert sources are configured. Saving notification policy does not establish a live feed. Source setup and a verified alert are separate work before operational use. Search-and-rescue teams, wildland contractors, industrial emergency teams and security departments can all benefit from an agreed weather-information policy, as can community paramedicine, mental health response, fire and E M S teams. Choose the display and messaging behavior that supports your operations, then test the complete configured service.')])


if __name__ == '__main__':
    freeze('weather-policy')
    out = S / 'expansion/plans' / (NAME + '-source-20261102')
    raw = S / 'captures/expansion/core-weather-alert-policy-20261102/manifest.json'
    snapshot = out / 'raw-manifest.snapshot.json'
    snapshot.write_bytes(raw.read_bytes())
    path = out / 'captures.reviewed.json'
    manifest = json.loads(path.read_text())
    manifest['raw_manifest'] = dict(file=snapshot.relative_to(S).as_posix(), sha256=sha(snapshot))
    for row in manifest['screenshots']:
        row['capture_review']['method'] = 'Root personally reviewed all four unchanged actual source sheets and the full-size restored-policy save confirmation. Only policy save/readback is claimed; the separate unsaved source form is not a configured feed.'
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
