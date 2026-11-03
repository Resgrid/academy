import { fireEvent, render, screen } from '@testing-library/react-native';
import React from 'react';

import { useCallsSettingsStore } from '@/stores/widget-settings/calls-settings-store';
import { usePersonnelSettingsStore } from '@/stores/widget-settings/personnel-settings-store';
import { useWidgetSettingsStore } from '@/stores/widget-settings/store';

import Configure from '../configure';

jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    getBoolean: jest.fn(),
    getNumber: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  })),
}));

jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock'));

jest.mock('expo-router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  // The dashboard store pulls in @/lib/i18n, which calls i18n.use(initReactI18next) at import time.
  initReactI18next: { type: '3rdParty', init: jest.fn() },
}));

jest.mock('nativewind', () => ({
  styled: jest.fn((Component: any) => Component),
  useColorScheme: jest.fn(() => ({ colorScheme: 'light' })),
}));

jest.mock('lucide-react-native', () => ({
  ChevronDown: () => null,
  ChevronUp: () => null,
}));

// The filter section reaches for groups/personnel APIs on mount; the configure screen's
// tab switching is what is under test here, not that section's data loading.
jest.mock('@/components/configure/scheduled-calls-filter-section', () => ({
  ScheduledCallsFilterSection: () => null,
}));

describe('Configure screen', () => {
  it('preserves the same font settings and columns the operational widgets use when saving', () => {
    usePersonnelSettingsStore.getState().updateSettings({ fontSize: 19, hideUnavailable: true, columnOrder: ['name', 'status'] });
    useCallsSettingsStore.getState().updateSettings({ fontSize: 21, dispatchScrollSpeed: 55, columnOrder: ['priority', 'name'] });
    const view = render(<Configure />);
    fireEvent.press(screen.getByTestId('configure-save-button'));
    expect(usePersonnelSettingsStore.getState().settings).toEqual(expect.objectContaining({ fontSize: 19, hideUnavailable: true, columnOrder: ['name', 'status'] }));
    expect(useCallsSettingsStore.getState().settings).toEqual(expect.objectContaining({ fontSize: 21, dispatchScrollSpeed: 55, columnOrder: ['priority', 'name'] }));
    view.unmount();
  });

  it('renders the Unit Alerts content when the Unit Alerts tab is selected', () => {
    render(<Configure />);

    expect(screen.queryByTestId('configure-unitAlerts-content')).toBeNull();

    fireEvent.press(screen.getByTestId('configure-tab-unitAlerts'));

    expect(screen.getByTestId('configure-unitAlerts-content')).toBeVisible();
  });
});

it('keeps a partial minus sign and saves a valid west longitude', () => {
  const view = render(<Configure />);
  fireEvent.press(screen.getByTestId('configure-tab-map'));
  fireEvent.changeText(screen.getByPlaceholderText('configure.longitude'), '-');
  expect(screen.getByDisplayValue('-')).toBeTruthy();
  fireEvent.changeText(screen.getByPlaceholderText('configure.latitude'), '41.85');
  fireEvent.changeText(screen.getByPlaceholderText('configure.longitude'), '-87.69');
  fireEvent.press(screen.getByTestId('configure-save-button'));
  expect(useWidgetSettingsStore.getState().map).toEqual(expect.objectContaining({ latitude: 41.85, longitude: -87.69 }));
  view.unmount();
});

it('shows an error and does not replace saved coordinates with an invalid value', () => {
  useWidgetSettingsStore.getState().updateMapSettings({ latitude: 41.85, longitude: -87.69 });
  const view = render(<Configure />);
  fireEvent.press(screen.getByTestId('configure-tab-map'));
  fireEvent.changeText(screen.getByPlaceholderText('configure.latitude'), '91');
  fireEvent.press(screen.getByTestId('configure-save-button'));
  expect(screen.getByText('calls.coordinates_out_of_range')).toBeTruthy();
  expect(useWidgetSettingsStore.getState().map.latitude).toBe(41.85);
  view.unmount();
});
