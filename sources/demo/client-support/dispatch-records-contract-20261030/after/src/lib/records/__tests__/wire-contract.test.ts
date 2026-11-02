import { cellKey, isProtected, isRestricted, toValueList, toValueMap } from '@/lib/records/schema';
import { type RecordFieldSchema, type RecordValuesData, RmsFieldClassification } from '@/models/v4/records';

// Literal server values, not fixtures built from this client's enum: Core Standard=0/Restricted=1/Protected=2.
describe('Core Records wire contract', () => {
  it('matches the three actual Core classification values and keeps unknown fields restricted', () => {
    expect([RmsFieldClassification.Standard, RmsFieldClassification.Restricted, RmsFieldClassification.Protected]).toEqual([0, 1, 2]);
    for (const [number, restricted, protectedField] of [
      [0, false, false],
      [1, true, false],
      [2, true, true],
      [99, true, false],
    ] as const) {
      const field = { Classification: number } as RecordFieldSchema;
      expect(isRestricted(field)).toBe(restricted);
      expect(isProtected(field)).toBe(protectedField);
    }
    expect(isRestricted({} as RecordFieldSchema)).toBe(true);
  });

  it('maps nested sections and repeating rows without merging their identities', () => {
    const payload: RecordValuesData = {
      DefinitionKey: 'training-review',
      DefinitionVersion: 1,
      Sections: [
        {
          SectionKey: 'summary',
          Rows: [
            {
              RowKey: null,
              Ordinal: 0,
              Cells: [
                { FieldKey: 'summary', Value: '  exact summary  ' },
                { FieldKey: 'notes', Value: 'Stored notes' },
              ],
            },
          ],
        },
        {
          SectionKey: 'crew',
          Repeating: true,
          Rows: [
            {
              RowKey: 'row-a',
              Ordinal: 0,
              Cells: [
                { FieldKey: 'member', ReferenceType: 'user', ReferenceId: 'member-a' },
                { FieldKey: 'options', Values: ['alpha', 'beta'] },
              ],
            },
            { RowKey: 'row-b', Ordinal: 1, Cells: [{ FieldKey: 'member', ReferenceType: 'user', ReferenceId: 'member-b' }] },
          ],
        },
      ],
    };
    const unchanged = JSON.stringify(payload);
    const mapped = toValueMap(payload);
    expect(mapped[cellKey('summary', 'summary')].Value).toBe('  exact summary  ');
    expect(mapped[cellKey('summary', 'notes')].Value).toBe('Stored notes');
    expect(mapped[cellKey('crew', 'member', 'row-a')]).toMatchObject({ SectionKey: 'crew', RowKey: 'row-a', Ordinal: 0, ReferenceType: 'user', ReferenceId: 'member-a' });
    expect(mapped[cellKey('crew', 'member', 'row-b')]).toMatchObject({ RowKey: 'row-b', Ordinal: 1, ReferenceId: 'member-b' });
    expect(mapped[cellKey('crew', 'options', 'row-a')].Values).toEqual(['alpha', 'beta']);
    expect(JSON.stringify(payload)).toBe(unchanged);
  });

  it('does not map withheld cells or field keys even if unexpected raw content is present', () => {
    const mapped = toValueMap({
      WithheldFieldKeys: ['withheld-by-key'],
      Sections: [
        {
          SectionKey: 'summary',
          Rows: [
            {
              Cells: [
                { FieldKey: 'visible', Value: 'Returned plaintext' },
                { FieldKey: 'withheld', Withheld: true, Value: 'must not copy', Display: '[redacted]' },
                { FieldKey: 'withheld-by-key', Value: 'must not copy either' },
                { FieldKey: 'display-only', Display: 'not an editable value' },
              ],
            },
          ],
        },
      ],
    });
    expect(mapped[cellKey('summary', 'withheld')]).toBeUndefined();
    expect(mapped[cellKey('summary', 'withheld-by-key')]).toBeUndefined();
    expect(mapped[cellKey('summary', 'display-only')].Value).toBeNull();
    expect(toValueList(mapped)).toEqual([expect.objectContaining({ FieldKey: 'visible', Value: 'Returned plaintext' })]);
  });

  it('preserves flat-array prefill callers and both withholding flags', () => {
    const mapped = toValueMap([
      { SectionKey: 'summary', FieldKey: 'call', ReferenceType: 'call', ReferenceId: '51001' },
      { SectionKey: 'summary', FieldKey: 'legacy-private', IsWithheld: true, Value: 'not copied' },
      { SectionKey: 'summary', FieldKey: 'private', Withheld: true, Value: 'not copied' },
    ]);
    expect(Object.keys(mapped)).toEqual([cellKey('summary', 'call')]);
    expect(mapped[cellKey('summary', 'call')]).toMatchObject({ ReferenceType: 'call', ReferenceId: '51001' });
    expect(toValueMap({ Cells: [{ SectionKey: 'summary', FieldKey: 'summary', Value: 'Legacy wrapper' }] })[cellKey('summary', 'summary')].Value).toBe('Legacy wrapper');
  });

  it('keeps raw units, currency and a zero offset without deriving values from display/numbers', () => {
    const mapped = toValueMap({
      Sections: [
        {
          SectionKey: 'summary',
          Rows: [{ RowKey: 'r', Ordinal: 0, Cells: [{ FieldKey: 'amount', Value: '0.00', CurrencyCode: 'USD', OffsetMinutes: 0, UnitCode: 'gal', Display: 'Different formatted display' }] }],
        },
      ],
    });
    expect(mapped[cellKey('summary', 'amount', 'r')]).toMatchObject({ Value: '0.00', CurrencyCode: 'USD', OffsetMinutes: 0, UnitCode: 'gal', Ordinal: 0 });
  });

  it('does not invent absent sections, rows, cells or identities', () => {
    for (const payload of [null, undefined, {}, { Sections: [] }, { Sections: [{ SectionKey: 'summary' }] }]) {
      expect(toValueMap(payload)).toEqual({});
    }
    expect(toValueMap([{ FieldKey: 'without-section', Value: 'not mapped' }])).toEqual({});
    expect(toValueMap({ Sections: [], Cells: [{ SectionKey: 'summary', FieldKey: 'stale-flat', Value: 'not substituted' }] })).toEqual({});
  });
});
