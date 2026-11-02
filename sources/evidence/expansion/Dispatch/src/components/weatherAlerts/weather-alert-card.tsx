import { AlertTriangle, Cloud, Flame, Heart, Leaf } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, View } from 'react-native';

import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { SEVERITY_COLORS, WeatherAlertCategory, WeatherAlertCertainty, WeatherAlertSeverity, WeatherAlertUrgency } from '@/models/v4/weatherAlerts/weatherAlertEnums';
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

const getSeverityLabel = (severity: number, t: (key: string) => string): string => {
  switch (severity) {
    case WeatherAlertSeverity.Extreme:
      return t('weatherAlerts.severity.extreme');
    case WeatherAlertSeverity.Severe:
      return t('weatherAlerts.severity.severe');
    case WeatherAlertSeverity.Moderate:
      return t('weatherAlerts.severity.moderate');
    case WeatherAlertSeverity.Minor:
      return t('weatherAlerts.severity.minor');
    default:
      return t('weatherAlerts.severity.unknown');
  }
};

const getUrgencyLabel = (urgency: number, t: (key: string) => string): string => {
  switch (urgency) {
    case WeatherAlertUrgency.Immediate:
      return t('weatherAlerts.urgency.immediate');
    case WeatherAlertUrgency.Expected:
      return t('weatherAlerts.urgency.expected');
    case WeatherAlertUrgency.Future:
      return t('weatherAlerts.urgency.future');
    case WeatherAlertUrgency.Past:
      return t('weatherAlerts.urgency.past');
    default:
      return t('weatherAlerts.urgency.unknown');
  }
};

const getCertaintyLabel = (certainty: number, t: (key: string) => string): string => {
  switch (certainty) {
    case WeatherAlertCertainty.Observed:
      return t('weatherAlerts.certainty.observed');
    case WeatherAlertCertainty.Likely:
      return t('weatherAlerts.certainty.likely');
    case WeatherAlertCertainty.Possible:
      return t('weatherAlerts.certainty.possible');
    case WeatherAlertCertainty.Unlikely:
      return t('weatherAlerts.certainty.unlikely');
    default:
      return t('weatherAlerts.certainty.unknown');
  }
};

interface WeatherAlertCardProps {
  alert: WeatherAlertResultData;
  onPress: (alertId: string) => void;
}

export const WeatherAlertCard: React.FC<WeatherAlertCardProps> = ({ alert, onPress }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';
  const severityColor = SEVERITY_COLORS[alert.Severity] ?? SEVERITY_COLORS[WeatherAlertSeverity.Unknown];
  const CategoryIcon = getCategoryIcon(alert.AlertCategory);

  const cardStyle = StyleSheet.flatten([styles.card, { borderLeftColor: severityColor }, isDark ? styles.cardDark : styles.cardLight]);

  return (
    <Pressable onPress={() => onPress(alert.WeatherAlertId)} style={cardStyle}>
      <VStack space="xs">
        <HStack className="items-center justify-between">
          <HStack className="items-center" space="xs">
            <View style={StyleSheet.flatten([styles.severityDot, { backgroundColor: severityColor }])} />
            <Text style={{ color: severityColor, fontSize: 11, fontWeight: '700', textTransform: 'uppercase' }}>{getSeverityLabel(alert.Severity, t)}</Text>
          </HStack>
          <Icon as={CategoryIcon} size="sm" color={isDark ? '#9ca3af' : '#6b7280'} />
        </HStack>

        <Text className="text-sm font-semibold text-gray-900 dark:text-gray-100" numberOfLines={1}>
          {alert.Event}
        </Text>

        <Text className="text-xs text-gray-600 dark:text-gray-400" numberOfLines={2}>
          {alert.AreaDescription}
        </Text>

        {alert.ExpiresUtc && (
          <Text className="text-xs text-gray-500 dark:text-gray-500">
            {t('weatherAlerts.detail.expires')}: {alert.ExpiresUtc}
          </Text>
        )}

        <Text className="text-xs text-gray-400 dark:text-gray-500">
          {t('weatherAlerts.detail.urgency')}: {getUrgencyLabel(alert.Urgency, t)} · {t('weatherAlerts.detail.certainty')}: {getCertaintyLabel(alert.Certainty, t)}
        </Text>
      </VStack>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  card: {
    borderLeftWidth: 4,
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  cardLight: {
    backgroundColor: '#ffffff',
  },
  cardDark: {
    backgroundColor: '#1f2937',
  },
  severityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});
