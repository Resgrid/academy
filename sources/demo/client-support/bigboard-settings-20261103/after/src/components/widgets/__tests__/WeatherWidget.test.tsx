import { act, render, screen, waitFor } from '@testing-library/react-native';
import * as Location from 'expo-location';
import React from 'react';

import { getWeatherOutlook } from '@/api/weather/weather';

import { WeatherWidget } from '../WeatherWidget';

let mockSettings = { units: 'metric', latitude: 0, longitude: -78 };
const mockMap = { mapData: { CenterLat: 41.85, CenterLon: -87.69 }, fetchMapData: jest.fn() };
const mockCore = { config: { OpenWeatherApiKey: 'unit-test-provider-key' } };
const mockLocation = { latitude: null, longitude: null, setLocation: jest.fn() };
jest.mock('@/stores/widget-settings/store', () => ({ useWidgetSettingsStore: (select: (state: unknown) => unknown) => select({ weather: mockSettings }) }));
jest.mock('@/stores/app/core-store', () => ({ useCoreStore: (select: (state: unknown) => unknown) => select(mockCore) }));
jest.mock('@/stores/app/location-store', () => ({ useLocationStore: (select: (state: unknown) => unknown) => select(mockLocation) }));
jest.mock('@/stores/mapping/map-store', () => ({ useMapStore: Object.assign((select: (state: unknown) => unknown) => select(mockMap), { getState: () => mockMap }) }));
jest.mock('@/api/weather/weather', () => ({ getWeatherOutlook: jest.fn() }));
jest.mock('expo-location', () => ({ requestForegroundPermissionsAsync: jest.fn(), getCurrentPositionAsync: jest.fn(), Accuracy: { Balanced: 3 } }));
jest.mock('nativewind', () => ({ styled: (component: unknown) => component, useColorScheme: () => ({ colorScheme: 'light' }) }));
const outlook = { location: 'Test location', current: { temperature: 18, condition: 'Clouds', humidity: 55, windSpeed: 4, icon: '03d' }, forecast: [] };

describe('Weather widget saved location and units', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSettings = { units: 'metric', latitude: 0, longitude: -78 };
    (getWeatherOutlook as jest.Mock).mockResolvedValue(outlook);
  });
  it('uses saved coordinates even on the equator without requesting device location', async () => {
    const view = render(<WeatherWidget />);
    await waitFor(() => expect(getWeatherOutlook).toHaveBeenCalledWith('unit-test-provider-key', 0, -78, 'metric'));
    expect(Location.requestForegroundPermissionsAsync).not.toHaveBeenCalled();
    expect(screen.getByText('18°C')).toBeTruthy();
    view.unmount();
  });
  it('uses the numeric department map centre when saved coordinates are unset', async () => {
    mockSettings = { ...mockSettings, latitude: 0, longitude: 0 };
    const view = render(<WeatherWidget />);
    await waitFor(() => expect(getWeatherOutlook).toHaveBeenCalledWith('unit-test-provider-key', 41.85, -87.69, 'metric'));
    expect(Location.requestForegroundPermissionsAsync).not.toHaveBeenCalled();
    view.unmount();
  });
  it('does not overwrite the latest forecast with an obsolete response', async () => {
    let resolveOld: (value: typeof outlook) => void = () => {};
    (getWeatherOutlook as jest.Mock).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveOld = resolve;
        })
    );
    const view = render(<WeatherWidget />);
    await waitFor(() => expect(getWeatherOutlook).toHaveBeenCalledTimes(1));
    mockSettings = { ...mockSettings, latitude: 1 };
    view.rerender(<WeatherWidget />);
    await screen.findByText('Weather - Test location');
    await act(async () => resolveOld({ ...outlook, location: 'Obsolete location' }));
    expect(screen.queryByText('Weather - Obsolete location')).toBeNull();
    view.unmount();
  });
});
