import { pinBounds, validCoordinates, visibleMapPins } from '@/lib/widget-map-settings';
import { MapMakerInfoData } from '@/models/v4/mapping/getMapDataAndMarkersData';
import { type MapWidgetSettings } from '@/stores/widget-settings/store';

const settings: MapWidgetSettings = { zoomLevel: 12, showAllMarkers: true, hideLabels: false, showCalls: true, showLinkedCalls: true, showStations: true, showUnits: true, showPersonnel: true, latitude: 0, longitude: 0 };
const pin = (Type: number, linked = false) => Object.assign(new MapMakerInfoData(), { Type, Latitude: 41.8, Longitude: -87.6, IsLinkedCall: linked });

describe('saved map visibility', () => {
  it('independently filters calls, linked calls, units, stations and personnel', () => {
    const pins = [pin(0), pin(0, true), pin(1), pin(2), pin(3), pin(4), pin(5)];
    expect(visibleMapPins(pins, { ...settings, showCalls: false, showLinkedCalls: false, showUnits: false, showStations: false, showPersonnel: false })).toEqual([pins[5], pins[6]]);
    expect(visibleMapPins(pins, { ...settings, showCalls: false })).toContain(pins[1]);
    expect(visibleMapPins(pins, { ...settings, showLinkedCalls: false })).not.toContain(pins[1]);
  });
  it('rejects corrupt coordinates while retaining locations on the equator or prime meridian', () => {
    expect(validCoordinates(0, -78)).toBe(true);
    expect(validCoordinates(52, 0)).toBe(true);
    for (const pair of [
      [0, 0],
      [NaN, 1],
      [1, Infinity],
      [null, 1],
      [91, 0],
      [0, 181],
    ])
      expect(validCoordinates(...(pair as [unknown, unknown]))).toBe(false);
  });
  it('fits only the visible coordinates', () => {
    const pins = [pin(0), { ...pin(1), Latitude: 42, Longitude: -88 }];
    expect(pinBounds(pins)).toEqual([
      [-88, 41.8],
      [-87.6, 42],
    ]);
  });
});
