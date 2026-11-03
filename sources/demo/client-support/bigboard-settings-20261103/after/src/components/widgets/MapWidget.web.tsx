import mapboxgl from 'mapbox-gl';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { getMapDataAndMarkers, getMapLayers } from '@/api/mapping/mapping';
import { Box } from '@/components/ui/box';
import { Spinner } from '@/components/ui/spinner';
import { useMapLiveLocations } from '@/hooks/use-map-live-locations';
import { useMapSignalRUpdates } from '@/hooks/use-map-signalr-updates';
import { logger } from '@/lib/logging';
import { getDepartmentMapCenter } from '@/lib/map-center';
import { useDepartmentMapStyle } from '@/lib/map-style';
import { getMapboxAccessToken, onMapboxAccessTokenChange } from '@/lib/mapbox-token';
import { pinBounds, validCoordinates, visibleMapPins, widgetZoom } from '@/lib/widget-map-settings';
import { type MapMakerInfoData } from '@/models/v4/mapping/getMapDataAndMarkersData';
import { useCoreStore } from '@/stores/app/core-store';
import useAuthStore from '@/stores/auth/store';
import { useMapStore } from '@/stores/mapping/map-store';
import { useWidgetSettingsStore } from '@/stores/widget-settings/store';

import MapPins from '../maps/map-pins.web';
import { WidgetContainer } from './WidgetContainer';

interface MapWidgetProps {
  onRemove?: () => void;
  isEditMode?: boolean;
  width?: number;
  height?: number;
  containerWidth?: number;
  containerHeight?: number;
}

export const MapWidget: React.FC<MapWidgetProps> = ({ onRemove, isEditMode, width = 2, height = 3, containerWidth, containerHeight }) => {
  const [mapPins, setMapPins] = useState<MapMakerInfoData[]>([]);
  const [isMapReady, setIsMapReady] = useState(false);
  const [hasLoadedInitialData, setHasLoadedInitialData] = useState(false);
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const appliedCamera = useRef<string | null>(null);
  const settings = useWidgetSettingsStore((state) => state.map);
  const visiblePins = useMemo(() => visibleMapPins(mapPins, settings), [mapPins, settings]);
  const cameraKey = JSON.stringify(settings);

  // The department's day/night base map. It changes when config lands as well as when the theme
  // flips, so construction reads it through a ref and a separate effect restyles the live map
  // instead of tearing it (and its pins) down.
  const mapStyle = useDepartmentMapStyle();
  const mapStyleRef = useRef(mapStyle);
  const appliedMapStyleRef = useRef<string | null>(null);
  useEffect(() => {
    mapStyleRef.current = mapStyle;
  }, [mapStyle]);

  // mapbox-gl reads its global token on every request. The listener runs inside the token store's
  // update, before the re-render that may restyle the map with a style needing the new token.
  useEffect(
    () =>
      onMapboxAccessTokenChange((token) => {
        mapboxgl.accessToken = token;
      }),
    []
  );

  // Get auth and core store states
  const accessToken = useAuthStore((state) => state.accessToken);
  const isInitialized = useCoreStore((state) => state.isInitialized);
  const isAuthenticated = !!accessToken;

  // Realtime unit/personnel positions move pins in place; every REST snapshot goes through applySnapshot
  const { applySnapshot } = useMapLiveLocations(mapPins, setMapPins);
  const handleMarkersUpdate = useCallback((markers: MapMakerInfoData[], fetchStartedAt: number) => setMapPins(applySnapshot(markers, fetchStartedAt)), [applySnapshot]);

  // Use SignalR updates to refresh map pins
  useMapSignalRUpdates(handleMarkersUpdate);

  const setMapData = useMapStore((state) => state.setMapData);

  // Initialize map
  useEffect(() => {
    if (map.current) return; // initialize map only once
    if (!mapContainer.current) return;
    // Building the map before config lands pins it on the fallback centre permanently: the guard
    // above means this effect never constructs a second time once a map exists.
    if (!isInitialized) return;

    mapboxgl.accessToken = getMapboxAccessToken();

    // Add CSS if not already added
    if (!document.getElementById('mapbox-gl-css')) {
      const link = document.createElement('link');
      link.id = 'mapbox-gl-css';
      link.href = 'https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.css';
      link.rel = 'stylesheet';
      document.head.appendChild(link);
    }

    const center = getDepartmentMapCenter();

    appliedMapStyleRef.current = mapStyleRef.current;
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: mapStyleRef.current,
      center: [center.longitude, center.latitude],
      zoom: center.zoomLevel,
      attributionControl: false,
    });

    map.current.on('load', () => {
      setIsMapReady(true);
    });

    return () => {
      // Clean up map
      map.current?.remove();
      map.current = null;
      appliedMapStyleRef.current = null;
      // Reset loaded flag when map is cleaned up
      setHasLoadedInitialData(false);
      // A rebuilt map starts on the fallback centre again, so let it re-centre once
      appliedCamera.current = null;
    };
  }, [isInitialized]);

  // Restyle the live map when the department style changes (config load or theme flip). Pins are
  // DOM markers, so they survive setStyle.
  useEffect(() => {
    if (map.current && appliedMapStyleRef.current !== mapStyle) {
      map.current.setStyle(mapStyle);
      appliedMapStyleRef.current = mapStyle;
    }
  }, [mapStyle]);

  // Load initial map data when conditions are met
  useEffect(() => {
    const loadInitialData = async () => {
      if (!isMapReady || !isAuthenticated || !isInitialized || hasLoadedInitialData) {
        return;
      }

      try {
        logger.info({ message: 'MapWidget.web: Loading initial map data' });

        // Fetch both map data and layers
        const fetchStartedAt = Date.now();
        const [mapDataResult, layersResult] = await Promise.all([
          getMapDataAndMarkers(),
          getMapLayers(0), // 0 = All layers
        ]);

        if (mapDataResult?.Data?.MapMakerInfos) {
          logger.info({
            message: 'MapWidget.web: Initial map data loaded',
            context: { markerCount: mapDataResult.Data.MapMakerInfos.length },
          });
          setMapPins(applySnapshot(mapDataResult.Data.MapMakerInfos, fetchStartedAt));
          setMapData(mapDataResult.Data);
          setHasLoadedInitialData(true);
        }

        if (layersResult?.Data) {
          logger.info({
            message: 'MapWidget.web: Map layers loaded',
            context: { layerCount: layersResult.Data.Layers?.length || 0 },
          });
          // Store layers if needed for future use
        }
      } catch (error) {
        logger.error({
          message: 'MapWidget.web: Failed to load initial map data',
          context: { error },
        });
      }
    };

    loadInitialData();
  }, [isMapReady, isAuthenticated, isInitialized, hasLoadedInitialData, applySnapshot, setMapData]);

  // Apply saved framing once per configuration change, preserving later operator pans and live updates.
  useEffect(() => {
    if (!isMapReady || appliedCamera.current === cameraKey) return;
    if (!map.current) return;
    if (settings.showAllMarkers && visiblePins.length === 0) return;
    const department = getDepartmentMapCenter();
    const center: [number, number] = validCoordinates(settings.latitude, settings.longitude) ? [settings.longitude, settings.latitude] : [department.longitude, department.latitude];
    const zoom = widgetZoom(settings.zoomLevel);
    if (settings.showAllMarkers && visiblePins.length > 1) {
      const [sw, ne] = pinBounds(visiblePins);
      map.current.fitBounds([sw, ne], { padding: 40, maxZoom: zoom, duration: 0 });
    } else {
      const position: [number, number] = settings.showAllMarkers && visiblePins.length === 1 ? [visiblePins[0].Longitude, visiblePins[0].Latitude] : center;
      map.current.jumpTo({ center: position, zoom });
    }
    appliedCamera.current = cameraKey;
  }, [isMapReady, cameraKey, settings, visiblePins]);

  return (
    <WidgetContainer title="Map" onRemove={onRemove} isEditMode={isEditMode} testID="map-widget" width={containerWidth} height={containerHeight}>
      <Box className="relative flex-1">
        {!isMapReady && (
          <Box className="absolute inset-0 z-10 items-center justify-center">
            <Spinner size="small" />
          </Box>
        )}
        <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
        <MapPins map={map.current} pins={visiblePins} hideLabels={settings.hideLabels} isMapReady={isMapReady} />
      </Box>
    </WidgetContainer>
  );
};
