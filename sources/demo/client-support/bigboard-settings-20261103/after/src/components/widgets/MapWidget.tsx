import Mapbox from '@rnmapbox/maps';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { StyleSheet } from 'react-native';

import { getMapDataAndMarkers, getMapLayers } from '@/api/mapping/mapping';
import { Box } from '@/components/ui/box';
import { Spinner } from '@/components/ui/spinner';
import { Text } from '@/components/ui/text';
import { useMapLiveLocations } from '@/hooks/use-map-live-locations';
import { useMapSignalRUpdates } from '@/hooks/use-map-signalr-updates';
import { logger } from '@/lib/logging';
import { getDepartmentMapCenter } from '@/lib/map-center';
import { useDepartmentMapStyle } from '@/lib/map-style';
import { pinBounds, validCoordinates, visibleMapPins, widgetZoom } from '@/lib/widget-map-settings';
import { type MapMakerInfoData } from '@/models/v4/mapping/getMapDataAndMarkersData';
import { useCoreStore } from '@/stores/app/core-store';
import useAuthStore from '@/stores/auth/store';
import { useMapStore } from '@/stores/mapping/map-store';
import { useWidgetSettingsStore } from '@/stores/widget-settings/store';

import MapPins from '../maps/map-pins';
import { WidgetContainer } from './WidgetContainer';

interface MapWidgetProps {
  onRemove?: () => void;
  isEditMode?: boolean;
  width?: number;
  height?: number;
  containerWidth?: number;
  containerHeight?: number;
}

const styles = StyleSheet.create({
  map: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
});

export const MapWidget: React.FC<MapWidgetProps> = ({ onRemove, isEditMode, width = 2, height = 3, containerWidth, containerHeight }) => {
  // The department's day/night base map; follows config and the theme
  const mapStyle = useDepartmentMapStyle();
  const [mapPins, setMapPins] = useState<MapMakerInfoData[]>([]);
  const [isMapReady, setIsMapReady] = useState(false);
  const [hasLoadedInitialData, setHasLoadedInitialData] = useState(false);
  const cameraRef = useRef<Mapbox.Camera>(null);
  const appliedCamera = useRef<string | null>(null);
  const settings = useWidgetSettingsStore((state) => state.map);
  const visiblePins = useMemo(() => visibleMapPins(mapPins, settings), [mapPins, settings]);
  const cameraKey = JSON.stringify(settings);

  // Get auth and core store states
  const accessToken = useAuthStore((state) => state.accessToken);
  const isInitialized = useCoreStore((state) => state.isInitialized);
  const isAuthenticated = !!accessToken;

  // Get map store
  const setMapData = useMapStore((state) => state.setMapData);

  // Realtime unit/personnel positions move pins in place; every REST snapshot goes through applySnapshot
  const { applySnapshot } = useMapLiveLocations(mapPins, setMapPins);
  const handleMarkersUpdate = useCallback((markers: MapMakerInfoData[], fetchStartedAt: number) => setMapPins(applySnapshot(markers, fetchStartedAt)), [applySnapshot]);

  // Use SignalR updates to refresh map pins
  useMapSignalRUpdates(handleMarkersUpdate);

  // Load initial map data when conditions are met
  useEffect(() => {
    const loadInitialData = async () => {
      if (!isMapReady || !isAuthenticated || !isInitialized || hasLoadedInitialData) {
        return;
      }

      try {
        logger.info({ message: 'MapWidget: Loading initial map data' });

        // Fetch both map data and layers
        const fetchStartedAt = Date.now();
        const [mapDataResult, layersResult] = await Promise.all([
          getMapDataAndMarkers(),
          getMapLayers(0), // 0 = All layers
        ]);

        if (mapDataResult?.Data?.MapMakerInfos) {
          logger.info({
            message: 'MapWidget: Initial map data loaded',
            context: { markerCount: mapDataResult.Data.MapMakerInfos.length },
          });
          setMapPins(applySnapshot(mapDataResult.Data.MapMakerInfos, fetchStartedAt));

          // Store map data in the map store for other widgets to access
          setMapData(mapDataResult.Data);

          setHasLoadedInitialData(true);
        }

        if (layersResult?.Data) {
          logger.info({
            message: 'MapWidget: Map layers loaded',
            context: { layerCount: layersResult.Data.Layers?.length || 0 },
          });
          // Store layers if needed for future use
        }
      } catch (error) {
        logger.error({
          message: 'MapWidget: Failed to load initial map data',
          context: { error },
        });
      }
    };

    loadInitialData();
  }, [isMapReady, isAuthenticated, isInitialized, hasLoadedInitialData, setMapData, applySnapshot]);

  // Apply saved framing once per configuration change, preserving later operator pans and live updates.
  useEffect(() => {
    if (!isMapReady || appliedCamera.current === cameraKey) return;
    if (!cameraRef.current) return;
    if (settings.showAllMarkers && visiblePins.length === 0) return;
    const department = getDepartmentMapCenter();
    const center: [number, number] = validCoordinates(settings.latitude, settings.longitude) ? [settings.longitude, settings.latitude] : [department.longitude, department.latitude];
    const zoom = widgetZoom(settings.zoomLevel);
    if (settings.showAllMarkers && visiblePins.length > 1) {
      const [sw, ne] = pinBounds(visiblePins);
      cameraRef.current.fitBounds(ne, sw, 40, 0);
    } else {
      const position: [number, number] = settings.showAllMarkers && visiblePins.length === 1 ? [visiblePins[0].Longitude, visiblePins[0].Latitude] : center;
      cameraRef.current.setCamera({ centerCoordinate: position, zoomLevel: zoom, animationDuration: 0 });
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
        <Mapbox.MapView styleURL={mapStyle} style={styles.map} onDidFinishLoadingMap={() => setIsMapReady(true)}>
          <Mapbox.Camera ref={cameraRef} zoomLevel={10} animationDuration={0} />
          <MapPins pins={visiblePins} hideLabels={settings.hideLabels} />
        </Mapbox.MapView>
      </Box>
    </WidgetContainer>
  );
};
