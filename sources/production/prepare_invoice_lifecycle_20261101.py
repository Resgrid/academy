"""Freeze reviewed, executed invoice screens and their matching narration proposal."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'core-invoice-offline-payments-and-aging'
RAW = Path('captures/expansion/core-invoice-lifecycle-20261101')
RAW_SHA = '6da734e936a765928285277ec8e3c3e0c01b76f947d1244aa548e6dbdd91b90d'
LABELS = {
    1: ['New invoice', 'Customer', 'Currency', 'USD', 'Create draft'],
    2: ['New invoice', 'Customer', 'Academy Logistics Desk (fictional)', 'This contact has no billing profile yet.', 'Set up billing profile', 'USD', 'Create draft'],
    3: ['Billing profile: Academy Logistics Desk (fictional)', 'Billing e-mail', 'Terms (net days)', '30', 'Default discount %', '0', 'Rate card'],
    4: ['Notes', 'TRAINING ONLY - Academy invoice and offline payment exercise. No customer communication or real payment.', 'Save', 'Cancel'],
    5: ['New invoice', 'Customer', 'Academy Logistics Desk (fictional)', 'Currency', 'USD', 'Create draft'],
    6: ['Invoice #1', 'Draft', 'Currency', 'USD', 'Due', 'Leave empty to use the profile terms: net days 30', 'Discount %', 'Notes', 'Terms', 'Save', 'Preview & send'],
    7: ['Invoice #1', 'Draft', 'Notes', 'Terms', 'Line items', 'Description', 'Qty', 'Rate', 'Taxable', 'Amount', 'TRAINING ONLY - Standby exercise', '2', '50', '100.00', 'Total', '0.00', 'Save', 'Preview & send', 'Add line'],
    8: ['Invoice #1', 'Draft', 'Mark as sent (no e-mail)', 'Amount paid', 'Balance', '100.00 USD', '0.00', 'Total', 'Subtotal'],
    9: ['Invoice #1', 'Invoice marked as sent.', 'Sent', 'Issued', 'Due', 'Record payment', 'Total', '100.00 USD', 'Amount paid', '0.00', 'Balance'],
    10: ['Record payment', 'Manual payments only; online payments are recorded automatically.', 'Amount', '40', 'Paid on', 'Method', 'Other', 'Reference', 'TRAINING-ONLY-PAYMENT-01', 'Notes', 'Cancel'],
    11: ['Invoice #1', 'Partially paid', 'Total', '100.00 USD', 'Amount paid', '40.00', 'Balance', '60.00 USD', 'Record payment'],
    12: ['Payments', 'Paid on', 'Method', 'Reference', 'Payment status', 'Fee', 'Amount', 'Other', 'TRAINING-ONLY-PAYMENT-01', 'Succeeded', '40.00'],
    13: ['Accounts receivable aging', 'Current', '1-30 days past due', 'Total', '60.00 USD', '1 invoices', '#1', 'Academy Logistics Desk (fictional)', 'Due', 'Balance', '100.00 USD'],
    14: ['Record payment', 'Amount', '60', 'Paid on', 'Method', 'Other', 'Reference', 'TRAINING-ONLY-PAYMENT-02', 'Notes', 'Cancel'],
    15: ['Invoice #1', 'Paid', 'Total', '100.00 USD', 'Amount paid', '100.00', 'Balance', '0.00 USD', 'TRAINING ONLY - Standby exercise'],
    16: ['Payments', 'Paid on', 'Method', 'Reference', 'Payment status', 'Other', 'TRAINING-ONLY-PAYMENT-01', 'TRAINING-ONLY-PAYMENT-02', 'Succeeded', '40.00', '60.00'],
    17: ['Accounts receivable aging', 'Current', 'Total', '0.00', '0 invoices', 'No outstanding invoices.'],
    18: ['Invoicing', 'Outstanding balance', 'Overdue balance', 'Invoices', 'Number', 'Status', 'Paid', 'Filter', '#1', 'Academy Logistics Desk (fictional)', 'Total', 'Balance', '100.00 USD', '0.00 USD'],
}
SCENES = [
    ('01', 'Choose the customer and identify the profile prerequisite', [1, 2],
     'In Invoicing, choose New invoice. Select the fictional Academy Logistics Desk customer. The message below Customer says that this contact has no billing profile yet, and offers Set up billing profile. Create draft is disabled in this selected-customer view. Follow the profile link first. This walkthrough uses one fictional invoice and two fictional offline payment entries to show how saved invoice status, balance and aging change. You need authorized invoicing access for these actions.'),
    ('02', 'Prepare and save the fictional billing profile', [3, 4],
     'On the customer Billing profile page, review Billing e-mail, Terms in net days and Default discount. This training profile uses an example email address, thirty net days and zero default discount. Scroll to Notes, where the exercise is clearly labeled training only, then select Save. Configure a real customer profile using your department\'s agreed billing details. Here, the profile is only a prerequisite for practicing the software workflow with fictional data.'),
    ('03', 'Create the draft and read its inherited terms', [5, 6],
     'Return to New invoice and select the same customer. Keep U S dollars for this example and choose Create draft. The returned page shows Invoice number one with a Draft badge. In its Due field, the helper text says that leaving the field empty uses the profile terms of thirty net days. Notes and Terms are editable below. The draft view lets you prepare the invoice before changing its issued status.'),
    ('04', 'Add a manual line and verify totals after saving', [7, 8],
     'Use Add line and enter the description, TRAINING ONLY, Standby exercise. Set quantity to two and rate to fifty, and leave Taxable clear for this fictional example. The line Amount shows one hundred. Notice that the Total panel still shows zero and says discount and tax are recalculated when you save. Select Save, then Preview and send. The returned draft summary shows a total of one hundred U S dollars, nothing paid, and a balance of one hundred. Check the saved result before continuing.'),
    ('05', 'Mark the training invoice sent without email', [8, 9],
     'The draft summary includes Mark as sent, no email. Use that control for this local exercise. The returned page says Invoice marked as sent, and its badge is now Sent. Issued and Due now have dates; Amount paid is still zero, and Balance remains one hundred. This step changes the invoice\'s issued state. It does not record a payment. The no-email control also lets this exercise proceed without sending an invoice to a customer.'),
    ('06', 'Record the first fictional offline payment', [10],
     'Choose Record payment. The dialog describes manual payments and separates Amount, Paid on, Method, Reference and Notes. For this software exercise, enter forty, keep the displayed date, choose Other and add the training reference ending in zero one. The note identifies a fictional partial payment with no real money received. Select Record payment in the dialog to save this entry. In normal department work, those fields should describe the actual offline payment you are recording.'),
    ('07', 'Reload and inspect the partial payment result', [11, 12],
     'Reload the invoice. Its badge now reads Partially paid. Total is still one hundred, Amount paid is forty, and Balance is sixty U S dollars. Scroll to Payments to verify the saved row, including its date, Other method, training reference and forty amount. The row shows Succeeded as its recorded status. This is a manual entry in the invoice history; the exercise has not processed a bank transaction. Compare the saved row and the summary together.'),
    ('08', 'Follow the open balance into aging', [13],
     'Select Aging. Accounts receivable aging groups open balances by how far past due they are. In this example, Current shows sixty U S dollars for one invoice. The row below identifies invoice number one, the fictional customer, its due date, the original one-hundred-dollar total and the sixty-dollar balance. This makes the remaining receivable visible separately from the original charge. Open the invoice number link when you need to inspect its supporting details.'),
    ('09', 'Record the remaining fictional balance', [14, 15],
     'Open that invoice and choose Record payment again. This second fictional entry is sixty, with Other as the method and a different training reference ending in zero two. Its note again identifies a software exercise. Save the entry, then reload the invoice. The badge now reads Paid. Amount paid is one hundred, matching Total, and Balance is zero U S dollars. These saved values show the effect of both recorded entries on this invoice.'),
    ('10', 'Compare both saved payment references', [16],
     'Scroll to Payments. There are now two separate rows: forty with the first training reference, and sixty with the second. Both show Other and Succeeded. Keeping separate references makes it possible to distinguish the entries later instead of treating the combined total as the complete history. Review the date, method, reference and amount together when investigating how an invoice reached its displayed paid balance.'),
    ('11', 'Verify aging and the Paid invoice filter', [17, 18],
     'Return to Aging. The saved result now shows zero open invoices and No outstanding invoices. Back in Invoices, choose Paid in the Status filter and select Filter. Invoice number one remains in the returned list with Paid status, its original total and a zero balance. The invoice has not disappeared from history when its receivable clears. Use the status filter and open its detail page when you need the line items and payment records.'),
    ('12', 'Apply the same review sequence across departments', [18],
     'The same invoice and payment review can support a security company tracking a standby service, a search-and-rescue organization reviewing an agreed service charge, or a community paramedicine or mental health response team coordinating customer billing. Wildland contractors, industrial response teams, and fire and E M S departments can use the same saved-status checks where invoicing fits their work. Practice with fictional data, compare the line total with the recorded payments, then verify the remaining balance and invoice status.'),
]


def prepare(write=False):
    from verify_capture_evidence import _Validator, _image_dimensions
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    raw = S / RAW / 'manifest.json'
    assert sha(raw) == RAW_SHA
    rows = json.loads(raw.read_text())
    numbered = {int(row['id'][:3]): row for row in rows}
    reviewed_at = datetime.now(timezone.utc).isoformat()
    selected = []
    for number, labels in LABELS.items():
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        assert _image_dimensions(S / row['file']) == (row['width'], row['height'])
        dom = S / RAW / (row['id'] + '.txt')
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[],
                   dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom),
                   capture_review=dict(reviewer='Root', passed=True, reviewed_at=reviewed_at,
                                       sha256=row['sha256'], method='Root personally viewed this exact stored original using view_image. Pixels unchanged; only literal visible labels selected.'))
        validator = _Validator(S)
        validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
        selected.append(row)
    scenes = [dict(id=i, title=title, route='/User/Invoicing',
                   capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the executed customer profile, invoice form, saved status, payment record or aging result being discussed.',
                   required_labels=list(dict.fromkeys(label for n in refs for label in LABELS[n])),
                   narration=text, practice=title + ' using a separate fictional training customer and invoice.')
              for i, title, refs, text in SCENES]
    lesson = dict(id=NAME, title='Create an invoice and verify offline payments and aging', app='Core',
                  summary='Create a customer profile and manual invoice, mark it sent without email, record separate offline payments, and verify saved balances, aging and the Paid filter.',
                  audience=['Authorized invoicing administrators', 'Department billing coordinators', 'Department trainers'],
                  prerequisites=['Authorized invoicing view and management access in a local fictional department.', 'An existing fictional contact with no real customer or payment information.'],
                  scenes=scenes,
                  sector_examples=[dict(sector=sector, scenario=text) for sector, text in [
                      ('Security', 'Track an agreed standby-service invoice and separate offline payment records.'),
                      ('Search and rescue', 'Review a service invoice and the remaining balance in aging.'),
                      ('Community response', 'Coordinate customer billing for community paramedicine or mental health response services where appropriate.'),
                      ('Wildland', 'Compare contractor service charges with recorded offline payments.'),
                      ('Industrial', 'Review response-team service invoices and their saved balances.'),
                      ('Fire/EMS', 'Practice invoice administration with fictional service and payment entries.')]],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; generated narration, listening, complete correspondence, encoded-frame review and actual playback remain required.',
                                'No invoice email, payment collection, provider connection, bank transfer, PDF export, tax advice, void, refund or deployment rate schedule is demonstrated.',
                                'Source007 shows a pre-save Total of0.00 while the line Amount is100.00. Source008 is the saved100.00 result.',
                                'Source005 retains the no-profile hint after the profile save; only the enabled button and successful returned draft are demonstrated.',
                                'Manual payment Succeeded labels describe the saved entries; no external settlement is claimed.'])
    narration = '\n\n'.join(x['narration'] for x in scenes) + '\n'
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=raw.relative_to(S).as_posix(), sha256=RAW_SHA), screenshots=selected)
    review = dict(reviewer='Root', reviewed_at=reviewed_at,
                  actual_originals_personally_viewed=list(LABELS), source_pixels_changed=False,
                  script_reviewed_against_actual_views=True, source_only=True,
                  narration_words=len(narration.split()), audio_or_final_approval_inferred=False,
                  notes=['All eighteen exact original JPEGs personally viewed.',
                         'Profile email is a fictional example.invalid address; its DOM value was tool-redacted, so the address is not included as a validator label or narrated literally.',
                         'Mark as sent used the normal no-email UI control; User accepted its stalled native confirmation before the Sent result was recorded.',
                         'The draft line Amount and subtotal update before Save, while Total remains0.00 until the saved summary. Narration explicitly distinguishes them.',
                         'The invoice was reloaded after both payment stages. No real payment or email action occurred.'])
    if write:
        out = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
        assert not out.exists()
        out.mkdir()
        for file, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest), ('source-review.json', review)]:
            (out / file).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
        (out / 'narration.txt').write_text(narration)
    return dict(lesson_id=NAME, source_ready=True, scenes=len(scenes), actual_screens=len(selected), words=len(narration.split()), written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
