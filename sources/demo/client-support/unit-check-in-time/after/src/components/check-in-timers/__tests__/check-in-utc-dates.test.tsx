import { render } from '@testing-library/react-native';
import React from 'react';

import type { CheckInRecordResultData } from '@/models/v4/checkIn/checkInRecordResultData';
import type { CheckInTimerStatusResultData } from '@/models/v4/checkIn/checkInTimerStatusResultData';

import { CheckInHistoryList } from '../check-in-history-list';
import { CheckInTimerCard } from '../check-in-timer-card';

jest.mock('@/lib/storage/app', () => ({ getBaseApiUrl: jest.fn() }));
jest.mock('@/lib/logging', () => ({ logger: { error: jest.fn() } }));
jest.mock('@/lib/shared-ticker', () => ({ subscribeToSharedTicker: jest.fn(() => jest.fn()) }));
jest.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
jest.mock('lucide-react-native', () => ({ Timer: () => null }));
jest.mock('@/components/ui/box', () => ({
  Box: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => {
    const { View } = require('react-native');
    return <View {...props}>{children}</View>;
  },
}));
jest.mock('@/components/ui/hstack', () => ({
  HStack: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => {
    const { View } = require('react-native');
    return <View {...props}>{children}</View>;
  },
}));
jest.mock('@/components/ui/vstack', () => ({
  VStack: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => {
    const { View } = require('react-native');
    return <View {...props}>{children}</View>;
  },
}));
jest.mock('@/components/ui/text', () => ({
  Text: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => {
    const { Text } = require('react-native');
    return <Text {...props}>{children}</Text>;
  },
}));
jest.mock('@/components/ui/button', () => ({
  Button: ({ children }: React.PropsWithChildren) => children,
  ButtonText: ({ children }: React.PropsWithChildren) => children,
}));

const NOW = new Date('2026-10-27T23:50:00Z');
const SAME_INSTANT = new Date(Date.UTC(2026, 9, 27, 23, 45));
const timer = (value: unknown): CheckInTimerStatusResultData => ({
  TargetType: 0,
  TargetTypeName: 'Personnel',
  TargetEntityId: 'training-user',
  TargetName: 'Training user',
  UnitId: '',
  LastCheckIn: value as string,
  DurationMinutes: 60,
  WarningThresholdMinutes: 5,
  ElapsedMinutes: 5,
  Status: 'Ok',
});
const record = (value: unknown): CheckInRecordResultData => ({
  CheckInRecordId: 'training-record',
  CallId: 1,
  CheckInType: 0,
  CheckInTypeName: 'Personnel',
  UserId: 'training-user',
  UnitId: '',
  Latitude: '',
  Longitude: '',
  Timestamp: value as string,
  Note: 'Training only',
});

// Run this actual component suite in separate TZ=UTC and TZ=America/Los_Angeles
// Jest processes. Mutating process.env.TZ inside a Jest VM is not a TZ proof.
describe('check-in API UTC timestamp presentation', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(NOW);
  });
  afterEach(() => {
    jest.useRealTimers();
  });

  it('uses the process timezone under test', () => {
    if (process.env.TZ === 'America/Los_Angeles') expect(NOW.getTimezoneOffset()).toBe(420);
    if (process.env.TZ === 'UTC') expect(NOW.getTimezoneOffset()).toBe(0);
  });

  it.each([
    ['naive UTC', '2026-10-27T23:45:00'],
    ['explicit Z', '2026-10-27T23:45:00Z'],
    ['explicit negative offset', '2026-10-27T16:45:00-07:00'],
    ['explicit positive offset', '2026-10-28T01:45:00+02:00'],
    ['offset without colon', '2026-10-27T16:45:00-0700'],
  ])('renders the same five-minute age and local history instant for %s', (_label, timestamp) => {
    const card = render(<CheckInTimerCard timer={timer(timestamp)} onCheckIn={jest.fn()} showCheckInButton={false} />);
    expect(card.getByText('check_in.last_check_in: 5 check_in.minutes_ago')).toBeTruthy();
    card.unmount();
    const history = render(<CheckInHistoryList records={[record(timestamp)]} />);
    expect(history.getByText(SAME_INSTANT.toLocaleString())).toBeTruthy();
    history.unmount();
  });

  it.each([null, undefined, '', 'not-a-timestamp'])('shows an unknown instant instead of a fabricated recent check-in for %s', (timestamp) => {
    const card = render(<CheckInTimerCard timer={timer(timestamp)} onCheckIn={jest.fn()} showCheckInButton={false} />);
    expect(card.getByText('check_in.last_check_in: common.unknown')).toBeTruthy();
    card.unmount();
    const history = render(<CheckInHistoryList records={[record(timestamp)]} />);
    expect(history.getByText('common.unknown')).toBeTruthy();
    expect(history.queryByText('Invalid Date')).toBeNull();
    history.unmount();
  });

  it('does not mask a genuinely future zoned timestamp by clamping its age', () => {
    const card = render(<CheckInTimerCard timer={timer('2026-10-27T23:55:00Z')} onCheckIn={jest.fn()} showCheckInButton={false} />);
    expect(card.getByText('check_in.last_check_in: -5 check_in.minutes_ago')).toBeTruthy();
    card.unmount();
  });
});
