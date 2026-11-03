import { type MapMakerInfoData } from '@/models/v4/mapping/getMapDataAndMarkersData';
import { type MapWidgetSettings } from '@/stores/widget-settings/store';

export const validCoordinates = (latitude: unknown, longitude: unknown): latitude is number =>
  typeof latitude === 'number' &&
  typeof longitude === 'number' &&
  Number.isFinite(latitude) &&
  Number.isFinite(longitude) &&
  Math.abs(latitude) <= 90 &&
  Math.abs(longitude) <= 180 &&
  !(latitude === 0 && longitude === 0);

export const visibleMapPins = (pins: MapMakerInfoData[], settings: MapWidgetSettings): MapMakerInfoData[] =>
  pins.filter((pin) => {
    if (!validCoordinates(pin.Latitude, pin.Longitude)) return false;
    switch (pin.Type) {
      case 0:
        return pin.IsLinkedCall ? settings.showLinkedCalls : settings.showCalls;
      case 1:
        return settings.showUnits;
      case 2:
        return settings.showStations;
      case 3:
        return settings.showPersonnel;
      default:
        return true;
    }
  });

export const pinBounds = (pins: MapMakerInfoData[]): [[number, number], [number, number]] => [
  [Math.min(...pins.map((pin) => pin.Longitude)), Math.min(...pins.map((pin) => pin.Latitude))],
  [Math.max(...pins.map((pin) => pin.Longitude)), Math.max(...pins.map((pin) => pin.Latitude))],
];

export const widgetZoom = (zoom: number): number => (Number.isFinite(zoom) ? Math.max(0, Math.min(22, zoom)) : 12);
