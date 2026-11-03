import * as Location from 'expo-location';
import { Cloud, CloudDrizzle, CloudRain, CloudSnow, Sun, Wind } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useEffect, useState } from 'react';
import { ScrollView } from 'react-native';

import { getWeatherOutlook, type WeatherOutlook } from '@/api/weather/weather';
import { Box } from '@/components/ui/box';
import { Divider } from '@/components/ui/divider';
import { HStack } from '@/components/ui/hstack';
import { Spinner } from '@/components/ui/spinner';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { validCoordinates } from '@/lib/widget-map-settings';
import { useCoreStore } from '@/stores/app/core-store';
import { useLocationStore } from '@/stores/app/location-store';
import { useMapStore } from '@/stores/mapping/map-store';
import { useWidgetSettingsStore } from '@/stores/widget-settings/store';

import { WidgetContainer } from './WidgetContainer';

interface WeatherWidgetProps {
  onRemove?: () => void;
  isEditMode?: boolean;
  width?: number;
  height?: number;
  containerWidth?: number;
  containerHeight?: number;
  metadata?: { lat?: number; lon?: number };
}

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ onRemove, isEditMode, width = 2, height = 2, containerWidth, containerHeight, metadata }) => {
  const metadataLat = metadata?.lat;
  const metadataLon = metadata?.lon;
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';
  const config = useCoreStore((state) => state.config);
  const latitude = useLocationStore((state) => state.latitude);
  const longitude = useLocationStore((state) => state.longitude);
  const setLocation = useLocationStore((state) => state.setLocation);
  const mapData = useMapStore((state) => state.mapData);
  const fetchMapData = useMapStore((state) => state.fetchMapData);
  const weatherSettings = useWidgetSettingsStore((state) => state.weather);
  const units = weatherSettings.units;
  const [weatherData, setWeatherData] = useState<WeatherOutlook | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fetchWeather = async () => {
      setIsLoading(true);
      setError(null);
      setWeatherData(null);
      const apiKey = config?.OpenWeatherApiKey;
      if (!apiKey) {
        setError('API key not configured');
        setIsLoading(false);
        return;
      }
      try {
        let coordinates: [number, number] | undefined;
        if (validCoordinates(weatherSettings.latitude, weatherSettings.longitude)) {
          coordinates = [weatherSettings.latitude, weatherSettings.longitude];
        } else if (validCoordinates(metadataLat, metadataLon)) {
          coordinates = [metadataLat!, metadataLon!];
        } else {
          // Prefer the department map centre before requesting a device location.
          if (!mapData) await fetchMapData();
          if (cancelled) return;
          const center = useMapStore.getState().mapData;
          const numericCoordinate = (value: unknown) => (typeof value === 'number' ? value : typeof value === 'string' && value.trim() ? Number(value) : NaN);
          const mapLat = numericCoordinate(center?.CenterLat);
          const mapLon = numericCoordinate(center?.CenterLon);
          if (validCoordinates(mapLat, mapLon)) coordinates = [mapLat, mapLon];
          else if (validCoordinates(latitude, longitude)) coordinates = [latitude!, longitude!];
        }
        if (!coordinates) {
          const { status } = await Location.requestForegroundPermissionsAsync();
          if (cancelled) return;
          if (status !== 'granted') throw new Error('Location permission denied');
          const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
          if (cancelled) return;
          if (!validCoordinates(location.coords.latitude, location.coords.longitude)) throw new Error('Unable to get location');
          coordinates = [location.coords.latitude, location.coords.longitude];
          setLocation(location);
        }
        const data = await getWeatherOutlook(apiKey, coordinates[0], coordinates[1], units);
        if (cancelled) return;
        if (!data) throw new Error('Failed to load weather');
        setWeatherData(data);
      } catch (failure) {
        if (!cancelled) setError(failure instanceof Error ? failure.message : 'Failed to load weather');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    void fetchWeather();
    return () => {
      cancelled = true;
    };
  }, [config?.OpenWeatherApiKey, weatherSettings.latitude, weatherSettings.longitude, metadataLat, metadataLon, mapData, fetchMapData, latitude, longitude, setLocation, units]);

  const getWeatherIcon = (condition: string, size: number = 48) => {
    const iconColor = isDark ? '#FCD34D' : '#F59E0B';
    const conditionLower = condition.toLowerCase();

    if (conditionLower.includes('rain') || conditionLower.includes('thunderstorm')) {
      return <CloudRain size={size} color={iconColor} />;
    } else if (conditionLower.includes('drizzle')) {
      return <CloudDrizzle size={size} color={iconColor} />;
    } else if (conditionLower.includes('snow')) {
      return <CloudSnow size={size} color={iconColor} />;
    } else if (conditionLower.includes('cloud')) {
      return <Cloud size={size} color={iconColor} />;
    } else if (conditionLower.includes('wind')) {
      return <Wind size={size} color={iconColor} />;
    }
    return <Sun size={size} color={iconColor} />;
  };

  if (error) {
    return (
      <WidgetContainer title="Weather" onRemove={onRemove} isEditMode={isEditMode} testID="weather-widget" width={containerWidth} height={containerHeight}>
        <Box className="flex-1 items-center justify-center">
          <Text className={`text-sm ${isDark ? 'text-red-400' : 'text-red-600'}`}>{error}</Text>
        </Box>
      </WidgetContainer>
    );
  }

  if (isLoading) {
    return (
      <WidgetContainer title="Weather" onRemove={onRemove} isEditMode={isEditMode} testID="weather-widget" width={containerWidth} height={containerHeight}>
        <Box className="flex-1 items-center justify-center">
          <Spinner size="small" />
        </Box>
      </WidgetContainer>
    );
  }

  if (!weatherData) {
    return (
      <WidgetContainer title="Weather" onRemove={onRemove} isEditMode={isEditMode} testID="weather-widget" width={containerWidth} height={containerHeight}>
        <Box className="flex-1 items-center justify-center">
          <Text className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>No data</Text>
        </Box>
      </WidgetContainer>
    );
  }

  // Determine if we should use horizontal layout (need at least 500px for comfortable horizontal display)
  const useHorizontalLayout = containerWidth && containerWidth >= 500;

  // Unit labels follow the OpenWeatherMap units the data was fetched with:
  // metric -> Celsius / m/s, imperial -> Fahrenheit / mph, standard -> Kelvin / m/s.
  const tempUnitLabel = units === 'metric' ? '°C' : units === 'standard' ? 'K' : '°F';
  const windUnitLabel = units === 'imperial' ? 'mph' : 'm/s';

  return (
    <WidgetContainer title={`Weather - ${weatherData.location}`} onRemove={onRemove} isEditMode={isEditMode} testID="weather-widget" width={containerWidth} height={containerHeight}>
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        <VStack space="sm" className="p-2">
          {/* Current Weather */}
          <VStack space="xs" className="items-center">
            {getWeatherIcon(weatherData.current.condition, 64)}
            <Text className={`text-5xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {weatherData.current.temperature}
              {tempUnitLabel}
            </Text>
            <Text className={`text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{weatherData.current.condition}</Text>
            <HStack space="md" className="mt-1">
              <VStack space="xs" className="items-center">
                <Text className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Humidity</Text>
                <Text className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{weatherData.current.humidity}%</Text>
              </VStack>
              <VStack space="xs" className="items-center">
                <Text className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Wind</Text>
                <Text className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {weatherData.current.windSpeed} {windUnitLabel}
                </Text>
              </VStack>
            </HStack>
          </VStack>

          <Divider className="my-1" />

          {/* 5-Day Forecast */}
          <VStack space="xs">
            <Text className={`text-sm font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'} mb-1`}>5-Day Forecast</Text>

            {useHorizontalLayout ? (
              // Horizontal layout for wider screens
              <ScrollView horizontal showsHorizontalScrollIndicator={false} className="-mx-2 px-2">
                <HStack space="xs">
                  {weatherData.forecast.map((day, index) => (
                    <Box key={index} className={`w-20 rounded-lg p-2 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                      <VStack space="xs" className="items-center">
                        <Text className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'} text-center`}>{day.dayName}</Text>
                        {getWeatherIcon(day.condition, 32)}
                        <VStack space="xs" className="items-center">
                          <Text className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>{day.tempHigh}°</Text>
                          <Text className={`text-sm font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{day.tempLow}°</Text>
                        </VStack>
                        <Text className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'} text-center`} numberOfLines={2}>
                          {day.condition}
                        </Text>
                      </VStack>
                    </Box>
                  ))}
                </HStack>
              </ScrollView>
            ) : (
              // Vertical layout for narrower screens
              weatherData.forecast.map((day, index) => (
                <Box key={index} className={`rounded-lg p-2 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                  <HStack className="items-center justify-between">
                    <HStack space="sm" className="flex-1 items-center">
                      {getWeatherIcon(day.condition, 32)}
                      <VStack space="xs" className="flex-1">
                        <Text className={`text-sm font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{day.dayName}</Text>
                        <Text className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{day.condition}</Text>
                      </VStack>
                    </HStack>
                    <HStack space="xs" className="items-center">
                      <VStack space="xs" className="items-center">
                        <Text className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>High</Text>
                        <Text className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>{day.tempHigh}°</Text>
                      </VStack>
                      <VStack space="xs" className="items-center">
                        <Text className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Low</Text>
                        <Text className={`text-lg font-semibold ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{day.tempLow}°</Text>
                      </VStack>
                    </HStack>
                  </HStack>
                </Box>
              ))
            )}
          </VStack>
        </VStack>
      </ScrollView>
    </WidgetContainer>
  );
};
