import { type FeatureCollection } from 'geojson';
import { type IndoorMapFloorResultData, type IndoorMapResultData } from '@/models/v4/mapping/indoorMapResultData';
import { type ActiveLayerSummary } from '@/models/v4/mapping/mappingResults';

import { getBaseApiUrl } from '@/lib/storage/app';
import { type GetMapDataAndMarkersResult } from '@/models/v4/mapping/getMapDataAndMarkersResult';
import { type GetMapLayersResult } from '@/models/v4/mapping/getMapLayersResult';
import {
  type GetCustomMapLayerResult,
  type GetCustomMapResult,
  type GetCustomMapsResult,
  type GetIndoorMapFloorResult,
  type GetIndoorMapsResult,
  type SearchAllMapFeaturesResult,
  type SearchCustomMapRegionsResult,
  type SearchIndoorLocationsResult,
} from '@/models/v4/mapping/mappingResults';
import { type PoiResult, type PoisResult, type PoiTypesResult } from '@/models/v4/mapping/poiResults';

import { createCachedApiEndpoint } from '../common/cached-client';
import { api, createApiEndpoint } from '../common/client';

const getMayLayersApi = createApiEndpoint('/Mapping/GetMayLayers');
const getMapDataAndMarkersApi = createApiEndpoint('/Mapping/GetMapDataAndMarkers');
const getPoiApi = createCachedApiEndpoint('/Mapping/GetPoi', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});
const getPoisApi = createCachedApiEndpoint('/Mapping/GetPois', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});
const getPoiTypesApi = createCachedApiEndpoint('/Mapping/GetPoiTypes', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});

// Indoor map endpoints
const getIndoorMapsApi = createCachedApiEndpoint('/Mapping/GetIndoorMaps', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});
const searchIndoorLocationsApi = createApiEndpoint('/Mapping/SearchIndoorLocations');
const getNearbyIndoorMapsApi = createApiEndpoint('/Mapping/GetNearbyIndoorMaps');

// Custom map endpoints
const getCustomMapsApi = createCachedApiEndpoint('/Mapping/GetCustomMaps', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});
const getCustomMapApi = createApiEndpoint('/Mapping/GetCustomMap');
const getCustomMapLayerApi = createApiEndpoint('/Mapping/GetCustomMapLayer');
const searchCustomMapRegionsApi = createApiEndpoint('/Mapping/SearchCustomMapRegions');

// Discovery endpoints
const getAllActiveLayersApi = createCachedApiEndpoint('/Mapping/GetAllActiveLayers', {
  ttl: 5 * 60 * 1000,
  enabled: true,
});
const searchAllMapFeaturesApi = createApiEndpoint('/Mapping/SearchAllMapFeatures');

// --- Existing Endpoints ---

export const getMapDataAndMarkers = async (signal?: AbortSignal) => {
  const response = await getMapDataAndMarkersApi.get<GetMapDataAndMarkersResult>(undefined, signal);
  return response.data;
};

export const getPoiTypes = async () => {
  const response = await getPoiTypesApi.get<PoiTypesResult>();
  return response.data;
};

export const getPois = async (poiTypeId?: number, destinationOnly?: boolean) => {
  const params: Record<string, unknown> = {};
  if (poiTypeId !== undefined) {
    params.poiTypeId = poiTypeId;
  }
  if (destinationOnly !== undefined) {
    params.destinationOnly = destinationOnly;
  }

  const response = await getPoisApi.get<PoisResult>(params);
  return response.data;
};

export const getPoi = async (poiId: number | string) => {
  const response = await getPoiApi.get<PoiResult>({
    poiId: encodeURIComponent(String(poiId)),
  });
  return response.data;
};

export const getMayLayers = async (type: number, signal?: AbortSignal) => {
  const response = await getMayLayersApi.get<GetMapLayersResult>(
    {
      type: encodeURIComponent(type),
    },
    signal
  );
  return response.data;
};

// --- Indoor Maps ---

export const getIndoorMaps = async () => {
  const response = await getIndoorMapsApi.get<GetIndoorMapsResult>();
  return response.data;
};

export const getIndoorMap = async (mapId: string) => {
  type CoreMap = IndoorMapResultData & { BoundsNELat: number; BoundsNELon: number; BoundsSWLat: number; BoundsSWLon: number };
  const response = await api.get<{Data: {Map: CoreMap; Floors: IndoorMapFloorResultData[]}}> (`/Mapping/GetIndoorMap/${encodeURIComponent(mapId)}`);
  const { Map: map, Floors: floors } = response.data.Data;
  return {...response.data, Data: {...map, Floors: floors, BoundsNELatitude: map.BoundsNELat, BoundsNELongitude: map.BoundsNELon, BoundsSWLatitude: map.BoundsSWLat, BoundsSWLongitude: map.BoundsSWLon}};
};

export const getIndoorMapFloor = async (floorId: string) => {
  const response = await api.get<GetIndoorMapFloorResult> (`/Mapping/GetIndoorMapFloor/${encodeURIComponent(floorId)}`);
  return response.data;
};

export const getIndoorMapZonesGeoJSON = async (floorId: string) => {
  const response = await api.get<FeatureCollection> (`/Mapping/GetIndoorMapZonesGeoJSON/${encodeURIComponent(floorId)}`);
  if (response.data.type !== 'FeatureCollection' || !Array.isArray(response.data.features)) throw new Error('Invalid GeoJSON feature collection');
  if (response.data.features.length > 0) return {Data: response.data};
  // Legacy Core floor-editor regions may retain georeferenced coordinate rings
  // in PixelGeometry. Accept only a geographic ring around its stored geo centre;
  // ordinary image-pixel coordinates are deliberately not projected or invented.
  const floor = await getIndoorMapFloor(floorId);
  const zones = floor.Data.Zones as unknown as Array<Record<string, unknown>>;
  const features = (zones ?? []).flatMap(zone => {
    if (typeof zone.PixelGeometry !== 'string' || !zone.PixelGeometry.trim()) return [];
    const latitude = Number(zone.CenterLatitude), longitude = Number(zone.CenterLongitude);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude) || (latitude === 0 && longitude === 0)) return [];
    let ring: number[][];
    try { ring = JSON.parse(zone.PixelGeometry); } catch { return []; }
    if (!Array.isArray(ring) || ring.length < 3 || !ring.every(point => Array.isArray(point) && point.length === 2 && point.every(Number.isFinite)
      && Math.abs(point[0]) <= 180 && Math.abs(point[1]) <= 90 && Math.abs(point[0] - longitude) <= 0.02 && Math.abs(point[1] - latitude) <= 0.02)) return [];
    const coordinates = ring.map(point => [...point]);
    if (coordinates[0][0] !== coordinates[coordinates.length - 1][0] || coordinates[0][1] !== coordinates[coordinates.length - 1][1]) coordinates.push([...coordinates[0]]);
    return [{type: 'Feature' as const, id: String(zone.IndoorMapZoneId), geometry: {type: 'Polygon' as const, coordinates: [coordinates]}, properties: {
      id: zone.IndoorMapZoneId, name: zone.Name, description: zone.Description,
      zoneType: zone.ZoneType, color: zone.Color || '#3388ff', isSearchable: zone.IsSearchable === true,
      isDispatchable: zone.IsDispatchable === true,
    }}];
  });
  return {Data: {type: 'FeatureCollection' as const, features}};
};

export const searchIndoorLocations = async (term: string, mapId?: string) => {
  const params: Record<string, unknown> = { term: encodeURIComponent(term) };
  if (mapId) {
    params.mapId = encodeURIComponent(mapId);
  }
  const response = await searchIndoorLocationsApi.get<SearchIndoorLocationsResult>(params);
  return response.data;
};

export const getNearbyIndoorMaps = async (lat: number, lon: number, radiusMeters: number) => {
  const response = await getNearbyIndoorMapsApi.get<GetIndoorMapsResult>({
    lat,
    lon,
    radiusMeters,
  });
  return response.data;
};

// --- Custom Maps ---

export const getCustomMaps = async (type?: number) => {
  const params: Record<string, unknown> = {};
  if (type !== undefined) {
    params.type = encodeURIComponent(type);
  }
  const response = await getCustomMapsApi.get<GetCustomMapsResult>(params);
  return response.data;
};

export const getCustomMap = async (mapId: string) => {
  const response = await getCustomMapApi.get<GetCustomMapResult>({
    id: encodeURIComponent(mapId),
  });
  return response.data;
};

export const getCustomMapLayer = async (layerId: string) => {
  const response = await getCustomMapLayerApi.get<GetCustomMapLayerResult>({
    layerId: encodeURIComponent(layerId),
  });
  return response.data;
};

export const getMapLayerGeoJSON = async (layerId: string) => {
  const response = await api.get<FeatureCollection> (`/Mapping/GetMapLayerGeoJSON/${encodeURIComponent(layerId)}`);
  if (response.data.type !== 'FeatureCollection' || !Array.isArray(response.data.features)) throw new Error('Invalid GeoJSON feature collection');
  return {Data: response.data};
};

export const getCustomMapRegionsGeoJSON = async (layerId: string) => {
  const response = await api.get<FeatureCollection> (`/Mapping/GetCustomMapRegionsGeoJSON/${encodeURIComponent(layerId)}`);
  if (response.data.type !== 'FeatureCollection' || !Array.isArray(response.data.features)) throw new Error('Invalid GeoJSON feature collection');
  return {Data: response.data};
};

export const searchCustomMapRegions = async (term: string, layerId?: string) => {
  const params: Record<string, unknown> = { term: encodeURIComponent(term) };
  if (layerId) {
    params.layerId = encodeURIComponent(layerId);
  }
  const response = await searchCustomMapRegionsApi.get<SearchCustomMapRegionsResult>(params);
  return response.data;
};

// --- Discovery & Search ---

export const getAllActiveLayers = async () => {
  type CoreLayer = Omit<ActiveLayerSummary, 'LayerId' | 'Source'> & {Id: string; LayerSource: ActiveLayerSummary['Source']};
  const response = await getAllActiveLayersApi.get<{Data: CoreLayer[]}>();
  return {...response.data, Data: response.data.Data.map(layer => ({...layer, LayerId: layer.Id, Source: layer.LayerSource}))};
};

export const searchAllMapFeatures = async (term: string, type?: 'all' | 'indoor' | 'custom') => {
  const params: Record<string, unknown> = { term: encodeURIComponent(term) };
  if (type) {
    params.type = type;
  }
  const response = await searchAllMapFeaturesApi.get<SearchAllMapFeaturesResult>(params);
  return response.data;
};

// --- URL Helpers (no fetch needed, constructs URLs for components) ---

export const getFloorImageUrl = (floorId: string): string => {
  return `${getBaseApiUrl()}/Mapping/GetIndoorMapFloorImage/${encodeURIComponent(floorId)}`;
};

export const getCustomMapLayerImageUrl = (layerId: string): string => {
  return `${getBaseApiUrl()}/Mapping/GetCustomMapLayerImage/${encodeURIComponent(layerId)}`;
};

export const getCustomMapTileUrl = (layerId: string): string => {
  return `${getBaseApiUrl()}/Mapping/GetCustomMapTile/${encodeURIComponent(layerId)}/{z}/{x}/{y}`;
};

// Native/web map image sources cannot attach the API bearer header. Request an
// existing department-scoped signed resource URL; do not fall back to public access.
export const getSignedFloorImageUrl = async (floorId: string): Promise<string> => {
  const url = getFloorImageUrl(floorId);
  const response = await api.post<{Data: Array<{Url: string; SignedUrl: string | null}>}>(
    '/Mapping/SignMapResourceUrls', {Urls: [url]}
  );
  const signed = response.data.Data.find(item => item.Url === url)?.SignedUrl;
  if (!signed) throw new Error('Floor image access is unavailable');
  return signed;
};
