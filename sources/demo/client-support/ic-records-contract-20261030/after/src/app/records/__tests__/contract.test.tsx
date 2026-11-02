import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { randomUUID } from 'expo-crypto';
import React from 'react';

import { createRecordDraft, getRecord } from '@/api/records/records';
import { goldenCatalogEntry } from '@/lib/records/__tests__/fixtures';
import { type RecordDefinitionSchema, RmsRecordState } from '@/models/v4/records';
import { useRecordsStore } from '@/stores/records/store';

const mockReplace = jest.fn();
const mockTranslate = (key: string) => key;
const mockContext = {};
let mockParams: { id?: string; draft?: string } = {};
const GUID = '11111111-1111-4111-8111-111111111111';
const EXISTING_GUID = '22222222-2222-4222-8222-222222222222';
const mockSchema: RecordDefinitionSchema = {
  SchemaVersion: 1,
  Sections: [
    {
      Key: 'summary',
      Label: 'Summary',
      Fields: [
        { Key: 'summary', Label: 'Summary', Type: 1, Classification: 0 },
        { Key: 'notes', Label: 'Notes', Type: 2, Classification: 0 },
      ],
    },
  ],
};
const mockEntry = goldenCatalogEntry({ DefinitionKey: 'training-review', Version: 1, Name: 'Training review', SupportsPrefill: false, AllowOffline: false });

jest.mock('expo-crypto', () => ({ randomUUID: jest.fn(() => '11111111-1111-4111-8111-111111111111') }));
jest.mock('expo-router', () => ({ Stack: { Screen: () => null }, useRouter: () => ({ replace: mockReplace, back: jest.fn() }), useLocalSearchParams: () => mockParams }));
jest.mock('react-i18next', () => ({ useTranslation: () => ({ t: mockTranslate }) }));
jest.mock('lucide-react-native', () => ({ ChevronRight: () => null, CloudOff: () => null }));
jest.mock('@/hooks/use-records-context', () => ({ useRecordsContext: () => mockContext }));
jest.mock('@/stores/terminology/store', () => ({
  TermKeys: { Records: 'records' },
  useTerm: (_key: string, fallback: string) => fallback,
  useDefinitionTerm: (_key: string, fallback: string) => fallback,
  definitionTermKey: () => null,
  terminologyStore: (selector: (state: { names: Record<string, string> }) => unknown) => selector({ names: {} }),
}));
jest.mock('@/lib/records/uploads', () => ({ runUpload: jest.fn(), cancelUpload: jest.fn() }));
jest.mock('@/lib/logging', () => ({ logger: { error: jest.fn(), warn: jest.fn(), info: jest.fn(), debug: jest.fn() } }));
jest.mock('@/api/records/field-records', () => ({
  reportFieldRecordTelemetry: jest.fn(),
  getFieldRecordsPreflight: jest.fn(),
  getFieldRecordsCatalog: jest.fn(),
  getFieldRecordPrefill: jest.fn(),
  syncFieldRecords: jest.fn().mockResolvedValue({}),
  getFieldRecordAssignments: jest.fn(),
  getAssignmentsForRecord: jest.fn(),
  acknowledgeAssignment: jest.fn(),
  completeAssignment: jest.fn(),
}));
jest.mock('@/api/records/records', () => ({
  getRecord: jest.fn(),
  getRecordDefinitionVersion: jest.fn(),
  createRecordDraft: jest.fn(),
  saveRecordDraft: jest.fn(),
  submitRecordForReview: jest.fn(),
  finalizeRecord: jest.fn(),
  cancelRecord: jest.fn(),
}));
jest.mock('@/components/records/record-attachments', () => ({ RecordAttachments: () => null }));
jest.mock('@/components/records/record-form', () => {
  const { Text } = require('react-native');
  return { RecordForm: ({ values }: { values: unknown }) => <Text testID="returned-values">{JSON.stringify(values)}</Text> };
});
jest.mock('@/components/ui/box', () => ({ Box: require('react-native').View }));
jest.mock('@/components/ui/text', () => ({ Text: require('react-native').Text }));
jest.mock('@/components/ui/heading', () => ({ Heading: require('react-native').Text }));
jest.mock('@/components/ui/hstack', () => ({ HStack: require('react-native').View }));
jest.mock('@/components/ui/vstack', () => ({ VStack: require('react-native').View }));
jest.mock('@/components/ui/divider', () => ({ Divider: () => null }));
jest.mock('@/components/ui/spinner', () => ({ Spinner: () => null }));
jest.mock('@/components/ui/badge', () => ({ Badge: require('react-native').View, BadgeText: require('react-native').Text }));
jest.mock('@/components/ui/pressable', () => ({ Pressable: require('react-native').TouchableOpacity }));
jest.mock('@/components/ui/button', () => {
  const { Text, TouchableOpacity } = require('react-native');
  return { ButtonText: Text, Button: ({ isDisabled, ...props }: { isDisabled?: boolean }) => <TouchableOpacity disabled={isDisabled} {...props} /> };
});
jest.mock('@/components/ui/checkbox', () => ({ Checkbox: require('react-native').View, CheckboxIndicator: require('react-native').View, CheckboxIcon: () => null, CheckboxLabel: require('react-native').Text }));

const NewRecordScreen = require('../new').default as React.ComponentType;
const RecordScreen = require('../[id]').default as React.ComponentType;

describe('Records screens use the Core wire contract', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockParams = {};
    useRecordsStore.getState().reset();
    useRecordsStore.setState({
      catalog: { ContractVersion: 'field-catalog.v1', OriginClient: 'IncidentCommand', Ok: true, Reasons: [], ContextVerified: true, Definitions: [mockEntry], Exclusions: [], ServerTimestampMs: 0 },
      schemas: { 'training-review:1': mockSchema },
      pendingDrafts: {},
    });
    (createRecordDraft as jest.Mock).mockResolvedValue({ Data: { RecordId: GUID } });
  });

  it('sends a fresh UUID as both ClientRecordId and IdempotencyKey through the actual store', async () => {
    render(<NewRecordScreen />);
    fireEvent.press(screen.getByTestId('records-choose-training-review'));
    await screen.findByTestId('records-save-send');
    fireEvent.press(screen.getByTestId('records-save-send'));
    await waitFor(() => expect(createRecordDraft).toHaveBeenCalledTimes(1));
    const request = (createRecordDraft as jest.Mock).mock.calls[0][0];
    expect(randomUUID).toHaveBeenCalledTimes(1);
    expect(request.ClientRecordId).toBe(GUID);
    expect(request.ClientRecordId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    expect(request.IdempotencyKey).toBe(request.ClientRecordId);
    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith(`/records/${GUID}`));
  });

  it('preserves a resumed draft identity rather than silently rekeying it', async () => {
    mockParams = { draft: EXISTING_GUID };
    useRecordsStore.setState({
      pendingDrafts: {
        [EXISTING_GUID]: { clientRecordId: EXISTING_GUID, recordId: null, definitionKey: 'training-review', definitionVersion: 1, name: 'Training review', values: [], updatedOn: '2026-10-30T00:00:00Z' },
      },
    });
    render(<NewRecordScreen />);
    await screen.findByTestId('records-save-send');
    fireEvent.press(screen.getByTestId('records-save-send'));
    await waitFor(() => expect(createRecordDraft).toHaveBeenCalledTimes(1));
    expect(randomUUID).not.toHaveBeenCalled();
    expect((createRecordDraft as jest.Mock).mock.calls[0][0]).toMatchObject({ ClientRecordId: EXISTING_GUID, IdempotencyKey: EXISTING_GUID });
  });

  it('passes returned nested Summary/Notes into the form without writing a record', async () => {
    mockParams = { id: GUID };
    (getRecord as jest.Mock).mockResolvedValue({
      Data: {
        RecordId: GUID,
        DefinitionKey: 'training-review',
        DefinitionVersion: 1,
        State: RmsRecordState.Finalized,
        RowVersion: 1,
        Values: {
          DefinitionVersion: 1,
          Sections: [
            {
              SectionKey: 'summary',
              Rows: [
                {
                  RowKey: null,
                  Ordinal: 0,
                  Cells: [
                    { FieldKey: 'summary', Value: 'Returned summary' },
                    { FieldKey: 'notes', Value: 'Returned notes' },
                    { FieldKey: 'private', Withheld: true, Display: '[redacted]' },
                  ],
                },
              ],
            },
          ],
        },
      },
    });
    render(<RecordScreen />);
    await screen.findByText(/Returned summary/);
    expect(screen.getByText(/Returned notes/)).toBeTruthy();
    expect(screen.queryByText(/redacted/)).toBeNull();
    expect(createRecordDraft).not.toHaveBeenCalled();
    expect(screen.queryByTestId('record-save')).toBeNull();
  });
});
