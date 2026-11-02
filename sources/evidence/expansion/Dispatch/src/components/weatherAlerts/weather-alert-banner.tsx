import { AlertTriangle, Cloud, Flame, Heart, Leaf } from 'lucide-react-native';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Platform, Pressable, StyleSheet, View } from 'react-native';

import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { SEVERITY_COLORS, WeatherAlertCategory, WeatherAlertSeverity } from '@/models/v4/weatherAlerts/weatherAlertEnums';
import { type WeatherAlertResultData } from '@/models/v4/weatherAlerts/weatherAlertResultData';

const getCategoryIcon = (category: number) => {
  switch (category) {
    case WeatherAlertCategory.Fire:
      return Flame;
    case WeatherAlertCategory.Health:
      return Heart;
    case WeatherAlertCategory.Env:
      return Leaf;
    case WeatherAlertCategory.Met:
      return Cloud;
    default:
      return AlertTriangle;
  }
};

interface WeatherAlertBannerProps {
  alerts: WeatherAlertResultData[];
  onPress: () => void;
}

export const WeatherAlertBanner: React.FC<WeatherAlertBannerProps> = ({ alerts, onPress }) => {
  const { t } = useTranslation();

  if (alerts.length === 0) return null;

  // Sort by severity to show highest first
  const sorted = [...alerts].sort((a, b) => a.Severity - b.Severity);
  const topAlert = sorted[0];
  const remaining = alerts.length - 1;
  const bgColor = SEVERITY_COLORS[topAlert.Severity] ?? SEVERITY_COLORS[WeatherAlertSeverity.Unknown];
  const CategoryIcon = getCategoryIcon(topAlert.AlertCategory);

  const containerStyle = StyleSheet.flatten([styles.container, { backgroundColor: bgColor }]);

  return (
    <Pressable onPress={onPress} style={containerStyle}>
      <HStack className="items-center" space="sm">
        <Icon as={CategoryIcon} size="sm" color="#FFFFFF" />
        <View style={styles.textContainer}>
          <HStack className="items-center" space="xs">
            <Text className="text-sm font-bold text-white" numberOfLines={1}>
              {topAlert.Event}
            </Text>
            {remaining > 0 && <Text className="text-xs font-semibold text-white/85">{t('weatherAlerts.moreAlerts', { count: remaining })}</Text>}
          </HStack>
          <Text className="mt-0.5 text-xs text-white/90" numberOfLines={1}>
            {topAlert.AreaDescription}
            {topAlert.ExpiresUtc ? ` — ${t('weatherAlerts.detail.expires')} ${topAlert.ExpiresUtc}` : ''}
          </Text>
        </View>
      </HStack>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 8,
    marginVertical: 4,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  textContainer: {
    flex: 1,
  },
});
