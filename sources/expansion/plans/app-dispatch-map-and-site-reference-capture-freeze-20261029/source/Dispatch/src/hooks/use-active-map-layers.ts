import { type FeatureCollection } from 'geojson';
import { useCallback, useEffect, useRef, useState } from 'react';

import { getAllActiveLayers, getCustomMapRegionsGeoJSON } from '@/api/mapping/mapping';
import { logger } from '@/lib/logging';

export interface ActiveMapLayer {
  id: string;
  name: string;
  color: string;
  data: FeatureCollection;
}

const isAbort = (error: unknown): boolean => error instanceof Error && (error.name === 'AbortError' || error.message === 'canceled');

/**
 * Fetches the department's on-by-default custom-map region layers (RE1-T105) as GeoJSON so they can
 * be rendered on the live map. Legacy vector layers are already handled by useMapLayers, so only
 * "custommaplayer" active layers are resolved here to avoid double-rendering.
 */
export const useActiveMapLayers = (autoFetch = true) => {
  const [activeLayers, setActiveLayers] = useState<ActiveMapLayer[]>([]);
  const [isLoadingActiveLayers, setIsLoadingActiveLayers] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const refetchActiveLayers = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setIsLoadingActiveLayers(true);
    try {
      const result = await getAllActiveLayers(controller.signal);
      const custom = (result?.Data ?? []).filter((layer) => layer.IsOnByDefault && layer.LayerSource === 'custommaplayer');
      const resolved = await Promise.all(
        custom.map(async (layer) => {
          try {
            const data = await getCustomMapRegionsGeoJSON(layer.Id, controller.signal);
            if (!data || !Array.isArray((data as FeatureCollection).features)) return null;
            return { id: layer.Id, name: layer.Name, color: layer.Color || '#3b82f6', data: data as FeatureCollection } as ActiveMapLayer;
          } catch {
            return null;
          }
        })
      );
      setActiveLayers(resolved.filter((layer): layer is ActiveMapLayer => layer !== null));
    } catch (error) {
      if (!isAbort(error)) {
        logger.error({ message: 'Failed to fetch active custom map layers', context: { error } });
      }
    } finally {
      setIsLoadingActiveLayers(false);
    }
  }, []);

  useEffect(() => {
    if (autoFetch) refetchActiveLayers();
    return () => abortRef.current?.abort();
  }, [autoFetch, refetchActiveLayers]);

  return { activeLayers, isLoadingActiveLayers, refetchActiveLayers };
};
