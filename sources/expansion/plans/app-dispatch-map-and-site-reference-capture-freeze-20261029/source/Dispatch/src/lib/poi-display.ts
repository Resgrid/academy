import { type PoiResultData } from '@/models/v4/mapping/poiResultData';

const getTrimmedValue = (value?: string | null) => value?.trim() ?? '';

export const getPoiPrimaryDisplayText = (poi: Pick<PoiResultData, 'Name' | 'Address' | 'Note' | 'PoiTypeName'>): string => {
  return getTrimmedValue(poi.Name) || getTrimmedValue(poi.Address) || getTrimmedValue(poi.Note) || getTrimmedValue(poi.PoiTypeName);
};

export const getPoiSelectionLabel = (poi: Pick<PoiResultData, 'Name' | 'Address' | 'Note' | 'PoiTypeName'>): string => {
  const name = getTrimmedValue(poi.Name);
  const address = getTrimmedValue(poi.Address);

  if (name && address) {
    return `${name} - ${address}`;
  }

  return getPoiPrimaryDisplayText(poi);
};

export const getPoiDestinationOptionLabel = (poi: Pick<PoiResultData, 'Name' | 'Address' | 'Note' | 'PoiTypeName'>): string => {
  const typeName = getTrimmedValue(poi.PoiTypeName);
  const label = getPoiSelectionLabel(poi);

  return typeName ? `${typeName}: ${label}` : label;
};

export const getPoiSecondaryDisplayText = (poi: Pick<PoiResultData, 'Address' | 'Note' | 'PoiTypeName'>): string => {
  return getTrimmedValue(poi.Address) || getTrimmedValue(poi.Note) || getTrimmedValue(poi.PoiTypeName);
};

export const getPoiSearchValue = (poi: Pick<PoiResultData, 'Name' | 'Address' | 'Note' | 'PoiTypeName'>): string => {
  return [poi.Name, poi.Address, poi.Note, poi.PoiTypeName]
    .map((value) => getTrimmedValue(value))
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
};
