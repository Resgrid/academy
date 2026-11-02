"""Freeze genuine fictional compensation and call-costing UI examples."""
from prepare_records_reports_exports_20261102 import LESSONS, freeze

COMMON=dict(raw='core-workforce-compensation-costing-20261102',route='/User/Workforce',
            audience=['Department administrators','Workforce managers','Operational supervisors'],
            prerequisites=['Authorized Workforce access in a separate fictional training department.',
                           'Existing workers, work entries and a disposable training unit; all example amounts are fictional.'],
            sector_scenario='Review the same fictional personnel and resource costing controls using the terminology appropriate to your department.',
            scope='All amounts are fictional software inputs. No employment decision, real payroll import, external payment, tax filing, invoice or revenue transaction is performed.')

LESSONS['compensation']=dict(COMMON,
    name='core-workforce-compensation-default-approval',
    title='Configure a compensation default and complete independent approval',
    summary='Set effective dates, base pay and components; inspect the loaded-day preview and verify a separate manager’s approval.',
    excluded={},scenes=[
        ('Open compensation and understand the fallback order',[1,2],['Compensation','Add department default'],
         'In Workforce, open Compensation. The page separates employee, role-default and department-default profiles. Its help gives the estimate order: employee profile, then role default, then department default. It also says an approved payroll cost takes precedence. This lesson creates one fictional department default so you can see its settings and independent approval. It does not set a real employee’s pay. Select Add department default to open the form.'),
        ('Set the effective period and hourly base',[3,4],['Effective *','Expires','Pay basis','Currency','Base amount','Hours / day','Hours / week'],
         'Check the profile heading so you know which scope you are editing. Set Effective to October first and Expires to November thirtieth in this dated exercise. Choose Hourly, use U S D, and enter a Base amount of twenty. The form explains that the base is interpreted according to the pay basis. Keep eight Hours per day and forty Hours per week. The Regular hourly equivalent is an optional override; it stays blank here. These are deliberately simple fictional values for checking the software calculation.'),
        ('Add a pay component',[4,5],['Pay components','Category','Name','Basis','Amount','Eligible pay codes','Per OT hour'],
         'Use the plus control in Pay components to add a row. Each row has a Category, Name, Basis, Amount, Eligible pay codes and a Per O T hour checkbox. The example adds a named equipment differential with an amount of two per hour for Regular and Standby. Its overtime checkbox remains unchecked. The panel explains that these components sit on top of the base. Review the row as a separate contribution instead of putting every cost into the base amount.'),
        ('Add the employer cost and multipliers',[6,7],['Employer cost components','Rate','Cap','Eligible pay codes','Rate multipliers','Source'],
         'Use the plus control in Employer cost components for a separate fictional overhead amount of five per hour, again limited to Regular and Standby. Leave its optional Cap blank. In Rate multipliers, the example sets Overtime to one point five, DoubleTime to two, and Standby and Travel to one, using the J S O N structure shown. Add a Source note that identifies this as a fictional software exercise. These values are configuration examples, not prescribed rates for any department.'),
        ('Save and read the loaded-day preview',[7,8,9],['Save','Saved.','Approval','216.00 USD'],
         'Select Save, then confirm the Saved message and the persisted inputs. Scroll to Approval. Resgrid previews a regular eight-hour day at two hundred sixteen dollars: one hundred sixty in base pay, sixteen in pay components and forty in employer costs. Those amounts match the configured twenty, two and five per hour. The profile is still not approved. The notice says unapproved profiles can price estimates but flag their lines for review, and a rate change removes an approval.'),
        ('Recognize the independent-review guard',[10,11],['Approve profile','Compensation','No'],
         'Approve profile is a separate action from Save. When the manager who made the latest change tries to approve this example, Resgrid refuses. The message says that it is the manager’s own pay or they made the latest change, and another manager must approve it. The index still shows No in Approved. Do not treat a saved profile or a calculated preview as approval. Have a different authorized manager review the same profile through their normal account.'),
        ('Approve as a separate manager and verify the stored result',[40,41,42,43],['Kelly Severide','Approve profile','Approval','Approved 2026-11-02','Yes'],
         'The recording now uses a different, existing fictional administrator, Kelly Severide. The same department default is still not approved when that manager opens it. After reviewing the inputs and preview, select Approve profile. The returned form shows the approval date, and the Compensation index independently shows Yes. That is the successful stored result. The account switch uses normal sign-in; no permissions were changed and no approval restriction was bypassed.'),
        ('Apply the process to your own organization',[43],['Department default','Approved','Yes'],
         'Use the same separation of preparation and review for search-and-rescue teams, security companies, wildland contractors, industrial emergency teams and community response services. Community paramedicine, mental health response, fire and E M S departments can all name components that fit their own organization. Agree who maintains profiles, who independently approves them, and who checks the resulting costing output. Keep fictional exercises separate from operational compensation data.')])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('lesson',choices=['compensation']);freeze(p.parse_args().lesson)
