import { act, render, screen } from '@testing-library/react-native';
import React from 'react';

import { TimeWidget } from '../TimeWidget';

let mockSettings = { format24Hour: true, showSeconds: false };
jest.mock('@/stores/widget-settings/store', () => ({ useWidgetSettingsStore: (select: (state: unknown) => unknown) => select({ time: mockSettings }) }));
jest.mock('nativewind', () => ({ styled: (component: unknown) => component, useColorScheme: () => ({ colorScheme: 'light' }) }));

describe('Time widget saved preferences', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date(2026, 10, 3, 17, 5, 9));
  });
  afterEach(() => jest.useRealTimers());
  it('uses 24-hour time without seconds and responds to a settings change', () => {
    const view = render(<TimeWidget />);
    expect(screen.getByText('17:05')).toBeTruthy();
    mockSettings = { format24Hour: false, showSeconds: true };
    view.rerender(<TimeWidget />);
    expect(screen.getByText('05:05:09 PM')).toBeTruthy();
    act(() => jest.advanceTimersByTime(1000));
    expect(screen.getByText('05:05:10 PM')).toBeTruthy();
    view.unmount();
  });
});
