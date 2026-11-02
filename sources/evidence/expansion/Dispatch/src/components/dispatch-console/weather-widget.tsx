import { Cloud, CloudDrizzle, CloudFog, CloudLightning, CloudRain, CloudSnow, CloudSun, Droplets, Sun, Thermometer, Wind } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { logger } from '@/lib/logging';

interface WeatherData {
  temperature: number;
  condition: string;
  humidity: number;
  windSpeed: number;
  description: string;
  icon: string;
}

interface WeatherWidgetProps {
  /** Latitude for weather location */
  latitude?: number | null;
  /** Longitude for weather location */
  longitude?: number | null;
  /** Compact mode for smaller display */
  compact?: boolean;
}

// Weather condition codes mapping to icons
const getWeatherIcon = (iconCode: string) => {
  // OpenWeatherMap icon codes: https://openweathermap.org/weather-conditions
  const code = iconCode?.substring(0, 2);
  switch (code) {
    case '01': // clear sky
      return Sun;
    case '02': // few clouds
      return CloudSun;
    case '03': // scattered clouds
    case '04': // broken/overcast clouds
      return Cloud;
    case '09': // shower rain
    case '10': // rain
      return CloudRain;
    case '11': // thunderstorm
      return CloudLightning;
    case '13': // snow
      return CloudSnow;
    case '50': // mist/fog
      return CloudFog;
    default:
      return Cloud;
  }
};

// Map Open-Meteo weather codes to conditions and icons
const mapWeatherCode = (code: number, t: (key: string) => string): { condition: string; icon: string; description: string } => {
  // WMO Weather interpretation codes (WW)
  // https://open-meteo.com/en/docs
  if (code === 0) return { condition: 'Clear', icon: '01d', description: t('dispatch.weather.clear') };
  if (code === 1) return { condition: 'Mainly Clear', icon: '01d', description: t('dispatch.weather.mainly_clear') };
  if (code === 2) return { condition: 'Partly Cloudy', icon: '02d', description: t('dispatch.weather.partly_cloudy') };
  if (code === 3) return { condition: 'Overcast', icon: '04d', description: t('dispatch.weather.overcast') };
  if (code === 45 || code === 48) return { condition: 'Fog', icon: '50d', description: t('dispatch.weather.fog') };
  if (code >= 51 && code <= 55) return { condition: 'Drizzle', icon: '09d', description: t('dispatch.weather.drizzle') };
  if (code >= 56 && code <= 57) return { condition: 'Freezing Drizzle', icon: '09d', description: t('dispatch.weather.freezing_drizzle') };
  if (code >= 61 && code <= 65) return { condition: 'Rain', icon: '10d', description: t('dispatch.weather.rain') };
  if (code >= 66 && code <= 67) return { condition: 'Freezing Rain', icon: '10d', description: t('dispatch.weather.freezing_rain') };
  if (code >= 71 && code <= 77) return { condition: 'Snow', icon: '13d', description: t('dispatch.weather.snow') };
  if (code >= 80 && code <= 82) return { condition: 'Rain Showers', icon: '09d', description: t('dispatch.weather.rain_showers') };
  if (code >= 85 && code <= 86) return { condition: 'Snow Showers', icon: '13d', description: t('dispatch.weather.snow_showers') };
  if (code === 95) return { condition: 'Thunderstorm', icon: '11d', description: t('dispatch.weather.thunderstorm') };
  if (code >= 96 && code <= 99) return { condition: 'Thunderstorm with Hail', icon: '11d', description: t('dispatch.weather.thunderstorm_hail') };
  return { condition: 'Unknown', icon: '03d', description: t('dispatch.weather.unknown') };
};

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ latitude, longitude, compact = true }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';

  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWeather = useCallback(async () => {
    if (!latitude || !longitude) {
      setError('no_location');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Using Open-Meteo API (free, no API key required)
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph`
      );

      if (!response.ok) {
        throw new Error('Weather API request failed');
      }

      const data = await response.json();

      if (data.current) {
        // Map Open-Meteo weather codes to conditions
        const weatherCode = data.current.weather_code;
        const { condition, icon, description } = mapWeatherCode(weatherCode, t);

        setWeather({
          temperature: Math.round(data.current.temperature_2m),
          condition,
          humidity: data.current.relative_humidity_2m,
          windSpeed: Math.round(data.current.wind_speed_10m),
          description,
          icon,
        });
      }
    } catch (err) {
      logger.error({
        message: 'Failed to fetch weather data',
        context: { error: err, latitude, longitude },
      });
      setError('fetch_error');
    } finally {
      setIsLoading(false);
    }
  }, [latitude, longitude, t]);

  useEffect(() => {
    fetchWeather();

    // Refresh weather every 15 minutes
    const interval = setInterval(fetchWeather, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchWeather]);

  const WeatherIcon = weather ? getWeatherIcon(weather.icon) : Cloud;

  if (isLoading) {
    return (
      <View style={StyleSheet.flatten([styles.container, styles.compactContainer, { backgroundColor: isDark ? '#374151' : '#f3f4f6' }])}>
        <ActivityIndicator size="small" color={isDark ? '#9ca3af' : '#6b7280'} />
      </View>
    );
  }

  if (error || !weather) {
    return (
      <View style={StyleSheet.flatten([styles.container, styles.compactContainer, { backgroundColor: isDark ? '#374151' : '#f3f4f6' }])}>
        <Icon as={Cloud} size="sm" className="text-gray-400" />
        <Text className="ml-1 text-xs text-gray-500 dark:text-gray-400">--°F</Text>
      </View>
    );
  }

  if (compact) {
    return (
      <HStack className="items-center rounded-lg bg-gray-100 px-2 py-1 dark:bg-gray-800" space="xs">
        <Icon as={WeatherIcon} size="sm" className="text-blue-500 dark:text-blue-400" />
        <VStack>
          <Text className="text-sm font-bold text-gray-800 dark:text-gray-100">{weather.temperature}°F</Text>
          <Text className="text-xs text-gray-500 dark:text-gray-400" numberOfLines={1}>
            {weather.description}
          </Text>
        </VStack>
      </HStack>
    );
  }

  return (
    <View style={StyleSheet.flatten([styles.container, { backgroundColor: isDark ? '#374151' : '#f3f4f6' }])}>
      <HStack className="items-center" space="sm">
        <Icon as={WeatherIcon} size="lg" className="text-blue-500 dark:text-blue-400" />
        <VStack>
          <Text className="text-lg font-bold text-gray-800 dark:text-gray-100">{weather.temperature}°F</Text>
          <Text className="text-xs text-gray-500 dark:text-gray-400">{weather.description}</Text>
        </VStack>
      </HStack>
      <HStack className="mt-1 items-center" space="md">
        <HStack className="items-center" space="xs">
          <Icon as={Droplets} size="xs" className="text-blue-400" />
          <Text className="text-xs text-gray-500 dark:text-gray-400">{weather.humidity}%</Text>
        </HStack>
        <HStack className="items-center" space="xs">
          <Icon as={Wind} size="xs" className="text-gray-400" />
          <Text className="text-xs text-gray-500 dark:text-gray-400">{weather.windSpeed} mph</Text>
        </HStack>
      </HStack>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 8,
    padding: 8,
  },
  compactContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
});
