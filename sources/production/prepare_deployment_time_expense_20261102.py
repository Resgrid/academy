"""Freeze the actual saved draft deployment time report and expense exercise."""
import json
from prepare_records_reports_exports_20261102 import LESSONS, freeze, S, sha

LESSONS['deployment_time'] = dict(
    name='core-deployment-time-expenses', raw='core-deployment-administration-20261102',
    route='/User/Deployments',
    title='Record deployment duty and travel time and attach an expense',
    summary='Create a crew-scoped daily draft, separate personnel and resource time, save and verify the hours, and attach a nonbillable expense receipt.',
    audience=['Deployment coordinators', 'Department administrators', 'Resource supervisors'],
    prerequisites=['Authorized deployment time-entry access in the fictional training department.',
                   'The saved community support deployment with its van, Matthew Casey and Demo radio kit roster.'],
    sector_scenario='Record who worked, which resources were used and what was spent on a named assignment.',
    scope='This exercise saves a Draft daily time report and a nonbillable fictional expense. It does not submit, approve, sign, invoice or export a PDF. The deployment remains Planned and Operational only.',
    excluded={14:'Collapsed earlier selectors; use readable actual controls in016.',
              11:'Selected Active is not proof of a saved status transition.',
              12:'Despite its historical filename the saved badge remained Planned.',
              28:'The CSV control was captured but downloading its file did not complete; no successful CSV is claimed.'},
    scenes=[
        ('Choose the report date and crew scope', [13], ['Time reports', 'New time report', '2026-11-02', 'Crew: TRAINING ONLY - Community van 20261028'],
         'Open Time reports on the saved deployment. Choose November second as the report date and select Crew, with the training community van. The help explains that there is one report per day for each crew or person, and that entries are prefilled from the roster. Select New time report. A crew scope keeps this exercise focused on the van, its assigned person and its equipment. Choose the scope that matches the work you need to document.'),
        ('Inspect the prefilled draft and time zone', [16], ['Draft', 'Subject', 'Entry type', 'Start', 'times use the department time zone (America/Chicago)', 'Matthew Casey', 'Demo radio kit'],
         'The daily report opens as Draft. Read the Time entries heading: times use the department time zone, America slash Chicago in this exercise. The Subject column is prefilled with Matthew Casey, the training van and Demo radio kit. Each row initially uses Deployment as Entry type, with an eight o’clock Start. These are starting values from the roster, so check them against the actual exercise before saving. Use the horizontal table scrollbar to reach the remaining columns.'),
        ('Separate personnel duty from travel', [17], ['Subject', 'Entry type', 'Start', 'Add entry', 'Matthew Casey', 'Deployment', 'Travel'],
         'Prepare Casey’s Deployment row with a nine-thirty Start. Set the van and radio kit rows to nine o’clock. Use Add entry to create another row, then explicitly choose Casey as Subject and Travel as Entry type. Set that travel Start to nine o’clock. Inspect the new row rather than assuming Add entry selected the intended person or activity. This makes travel and coordination separate entries while keeping vehicle and equipment usage on their own subjects.'),
        ('Enter end times, breaks and distance', [18], ['End', 'Paid break (min)', 'Unpaid break (min)', 'Km', '10', '30', '12.5', 'Fictional coordination'],
         'Scroll the table right to End, Paid break, Unpaid break, kilometres and Notes. End the coordination, van and radio entries at one in the afternoon. End Casey’s travel at nine-thirty. Enter a ten-minute paid break and a thirty-minute unpaid break on the coordination row. Keep the other breaks at zero. Enter twelve point five kilometres on the van row and add a short note to each row. The notes distinguish fictional coordination, vehicle use, radio use and travel.'),
        ('Save the draft and verify calculated hours', [19,20,21], ['Save', 'Save and submit', 'Draft', '3.00h', '4.00h', '0.50h'],
         'Use Save in Actions to retain this draft. Save and submit is a separate control; this exercise uses Save. Review both sides of the returned table. Casey’s coordination shows three hours: nine-thirty to one, less the thirty-minute unpaid break. The paid break is not subtracted from that displayed total. Travel shows half an hour, while the van and radio each show four hours. Read the saved subject choices as well as the numbers so each total stays attached to the correct resource.'),
        ('Check the deployment summary', [22], ['Time reports', 'Personnel hours', '3.5', 'Draft', 'Open'],
         'Return to the deployment’s Time reports tab. Its Summary now shows three point five Personnel hours, representing Casey’s three hours of coordination and half an hour of travel. Vehicle and equipment hours are recorded separately; they are not extra people in that personnel total. The report list shows the dated crew report as Draft. Use Open to return to that report. A saved draft and a submitted or approved report are different states, so verify the displayed Status before treating it as ready for a later review.'),
        ('Prepare a fictional fuel expense and receipt', [24], ['Expenses', 'Date', 'Type', 'Fuel', 'Amount', '24.50', 'Currency', 'USD', 'Description', 'City', 'Receipt', 'Pre-approved', 'Billable', 'Add expense'],
         'In the report’s Expenses section, enter November second, choose Fuel, and enter twenty-four dollars and fifty cents in U S D. Add the training fuel description and Chicago as City. At Receipt, use Choose File to select the fictional receipt image. This fixture clearly says that no purchase or payment occurred. Leave Pre-approved unchecked and clear Billable for this operational-only exercise. Check those choices before selecting Add expense, because the form is preparing a new expense, not changing an existing one.'),
        ('Verify the saved expense and its report link', [25,27], ['Fuel', '24.50 USD', '· Not billable', 'Receipt', '#2', 'Total'],
         'After Add expense, the report lists Fuel, its training description and the saved amount. Return to the deployment’s Expenses tab for another readback. The row shows November second, Chicago, twenty-four dollars and fifty cents, and Not billable. Its Time report link is number two, tying this expense to the daily report. Total is also twenty-four dollars and fifty cents. The Receipt column offers the attachment; the downloaded file in this exercise matches the uploaded test receipt.'),
        ('Keep operational time and expense records useful', [27], ['Personnel hours', '3.5', 'Expenses', '24.50 USD', 'Time report'],
         'Use this process for the people, vehicles and equipment in your own department. Community paramedicine and mental health response teams, search-and-rescue teams, security companies, wildland contractors and industrial emergency teams can document assignment time and expenses alongside fire and E M S departments. Choose the right report scope, verify the time zone, and inspect saved hours and expense links. This example ends with a draft and a fictional nonbillable expense; later submission and approval require their own completed review.')])

if __name__ == '__main__':
    freeze('deployment_time')
    out=S/'expansion/plans/core-deployment-time-expenses-source-20261102'
    snap=out/'raw-manifest.snapshot.json'
    snap.write_bytes((S/'captures/expansion/core-deployment-administration-20261102/manifest.json').read_bytes())
    p=out/'captures.reviewed.json';data=json.loads(p.read_text())
    data['raw_manifest']={'file':snap.relative_to(S).as_posix(),'sha256':sha(snap)}
    for row in data['screenshots']:
        row['capture_review']['method']='Root personally inspected the actual original browser screenshot. Source pixels are unchanged.'
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
