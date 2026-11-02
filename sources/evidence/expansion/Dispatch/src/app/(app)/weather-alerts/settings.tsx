import { Stack } from 'expo-router';
import { PencilIcon, PlusIcon, Trash2Icon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Alert, Platform, ScrollView } from 'react-native';

import { FocusAwareStatusBar } from '@/components/ui';
import { Box } from '@/components/ui/box';
import { Button, ButtonIcon, ButtonText } from '@/components/ui/button';
import { Heading } from '@/components/ui/heading';
import { HStack } from '@/components/ui/hstack';
import { Select, SelectBackdrop, SelectContent, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Text } from '@/components/ui/text';
import { Textarea, TextareaInput } from '@/components/ui/textarea';
import { VStack } from '@/components/ui/vstack';
import { WeatherAlertSourceSheet } from '@/components/weatherAlerts/weather-alert-source-sheet';
import { WeatherAlertZoneSheet } from '@/components/weatherAlerts/weather-alert-zone-sheet';
import { WeatherAlertSeverity, WeatherAlertSourceType } from '@/models/v4/weatherAlerts/weatherAlertEnums';
import { type WeatherAlertSourceResultData } from '@/models/v4/weatherAlerts/weatherAlertSourceResultData';
import { type WeatherAlertZoneResultData } from '@/models/v4/weatherAlerts/weatherAlertZoneResultData';
import { useToastStore } from '@/stores/toast/store';
import { useWeatherAlertsStore } from '@/stores/weatherAlerts/store';

const SEVERITY_OPTIONS = [
  { value: WeatherAlertSeverity.Extreme, label: 'Extreme' },
  { value: WeatherAlertSeverity.Severe, label: 'Severe' },
  { value: WeatherAlertSeverity.Moderate, label: 'Moderate' },
  { value: WeatherAlertSeverity.Minor, label: 'Minor' },
  { value: WeatherAlertSeverity.Unknown, label: 'Unknown' },
];

const sourceTypeLabel = (type: number): string =>
  ({
    [WeatherAlertSourceType.NationalWeatherService]: 'National Weather Service',
    [WeatherAlertSourceType.EnvironmentCanada]: 'Environment Canada',
    [WeatherAlertSourceType.MeteoAlarm]: 'MeteoAlarm',
  })[type] ?? 'Source';

const confirmDelete = (message: string, onConfirm: () => void) => {
  if (Platform.OS === 'web') {
    // eslint-disable-next-line no-alert
    if (typeof window !== 'undefined' && window.confirm(message)) onConfirm();
    return;
  }
  Alert.alert('', message, [
    { text: 'Cancel', style: 'cancel' },
    { text: 'OK', style: 'destructive', onPress: onConfirm },
  ]);
};

/** Weather-alert configuration: department settings + alert zones + alert sources. */
export default function WeatherAlertSettingsScreen() {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const showToast = useToastStore((s) => s.showToast);
  const settings = useWeatherAlertsStore((s) => s.settings);
  const zones = useWeatherAlertsStore((s) => s.zones);
  const sources = useWeatherAlertsStore((s) => s.sources);
  const isSavingSettings = useWeatherAlertsStore((s) => s.isSavingSettings);

  const [enabled, setEnabled] = useState(true);
  const [minSeverity, setMinSeverity] = useState(String(WeatherAlertSeverity.Severe));
  const [autoSeverity, setAutoSeverity] = useState(String(WeatherAlertSeverity.Extreme));
  const [callIntegration, setCallIntegration] = useState(false);
  const [excludedEvents, setExcludedEvents] = useState('');

  const [zoneSheetOpen, setZoneSheetOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<WeatherAlertZoneResultData | null>(null);
  const [sourceSheetOpen, setSourceSheetOpen] = useState(false);
  const [editingSource, setEditingSource] = useState<WeatherAlertSourceResultData | null>(null);

  useEffect(() => {
    useWeatherAlertsStore.getState().fetchSettings();
    useWeatherAlertsStore.getState().fetchZones();
    useWeatherAlertsStore.getState().fetchSources();
  }, []);

  useEffect(() => {
    if (!settings) return;
    setEnabled(settings.WeatherAlertsEnabled);
    setMinSeverity(String(settings.MinimumSeverity));
    setAutoSeverity(String(settings.AutoMessageSeverity));
    setCallIntegration(settings.CallIntegrationEnabled);
    setExcludedEvents(settings.ExcludedEvents ?? '');
  }, [settings]);

  const handleSaveSettings = async () => {
    try {
      await useWeatherAlertsStore.getState().saveSettings({
        WeatherAlertsEnabled: enabled,
        MinimumSeverity: parseInt(minSeverity, 10),
        AutoMessageSeverity: parseInt(autoSeverity, 10),
        CallIntegrationEnabled: callIntegration,
        AutoMessageSchedule: settings?.AutoMessageSchedule ?? [],
        ExcludedEvents: excludedEvents.trim(),
      });
      showToast('success', t('weatherAlerts.settings.saved'));
    } catch {
      showToast('error', t('weatherAlerts.settings.save_error'));
    }
  };

  const cardClass = `mb-3 rounded-lg p-4 ${colorScheme === 'dark' ? 'bg-neutral-900' : 'bg-neutral-100'}`;

  const renderSeveritySelect = (value: string, onChange: (v: string) => void) => (
    <Select selectedValue={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectInput />
        <SelectIcon />
      </SelectTrigger>
      <SelectPortal>
        <SelectBackdrop />
        <SelectContent>
          {SEVERITY_OPTIONS.map((option) => (
            <SelectItem key={option.value} label={option.label} value={String(option.value)} />
          ))}
        </SelectContent>
      </SelectPortal>
    </Select>
  );

  return (
    <>
      <Stack.Screen options={{ title: t('weatherAlerts.settings.title'), headerShown: true, headerBackTitle: '' }} />
      <ScrollView className={`size-full flex-1 ${colorScheme === 'dark' ? 'bg-neutral-950' : 'bg-neutral-50'}`} contentContainerStyle={{ padding: 12 }}>
        <FocusAwareStatusBar />

        {/* Settings */}
        <Box className={cardClass}>
          <Heading size="sm" className="mb-3">
            {t('weatherAlerts.settings.general')}
          </Heading>
          <HStack className="mb-3 items-center justify-between">
            <Text className="flex-1 text-sm">{t('weatherAlerts.settings.enabled')}</Text>
            <Switch size="md" value={enabled} onValueChange={setEnabled} />
          </HStack>
          <VStack className="mb-3">
            <Text className="mb-1 text-sm text-gray-500">{t('weatherAlerts.settings.minimum_severity')}</Text>
            {renderSeveritySelect(minSeverity, setMinSeverity)}
          </VStack>
          <VStack className="mb-3">
            <Text className="mb-1 text-sm text-gray-500">{t('weatherAlerts.settings.auto_message_severity')}</Text>
            {renderSeveritySelect(autoSeverity, setAutoSeverity)}
          </VStack>
          <HStack className="mb-3 items-center justify-between">
            <Text className="flex-1 pr-2 text-sm">{t('weatherAlerts.settings.call_integration')}</Text>
            <Switch size="md" value={callIntegration} onValueChange={setCallIntegration} />
          </HStack>
          <VStack className="mb-3">
            <Text className="mb-1 text-sm text-gray-500">{t('weatherAlerts.settings.excluded_events')}</Text>
            <Textarea>
              <TextareaInput value={excludedEvents} onChangeText={setExcludedEvents} placeholder={t('weatherAlerts.settings.excluded_events_placeholder')} numberOfLines={2} />
            </Textarea>
          </VStack>
          <Button onPress={handleSaveSettings} disabled={isSavingSettings}>
            <ButtonText>{t('weatherAlerts.settings.save')}</ButtonText>
          </Button>
        </Box>

        {/* Zones */}
        <Box className={cardClass}>
          <HStack className="mb-2 items-center justify-between">
            <Heading size="sm">{t('weatherAlerts.settings.zones')}</Heading>
            <Button
              variant="link"
              size="xs"
              onPress={() => {
                setEditingZone(null);
                setZoneSheetOpen(true);
              }}
            >
              <ButtonIcon as={PlusIcon} size="xs" />
              <ButtonText className="text-xs">{t('weatherAlerts.settings.add_zone')}</ButtonText>
            </Button>
          </HStack>
          {zones.length === 0 ? (
            <Text className="text-sm text-gray-500">{t('weatherAlerts.settings.no_zones')}</Text>
          ) : (
            <VStack className="space-y-2">
              {zones.map((zone) => (
                <HStack key={zone.WeatherAlertZoneId} className="items-center justify-between border-b border-outline-100 pb-1">
                  <VStack className="flex-1 pr-2">
                    <Text className="text-sm font-medium">
                      {zone.Name} {zone.IsPrimary ? <Text className="text-xs text-blue-500">({t('weatherAlerts.settings.primary')})</Text> : null}
                    </Text>
                    <Text className="text-xs text-gray-500">
                      {zone.ZoneCode || '—'} · {zone.RadiusMiles} mi · {zone.IsActive ? t('weatherAlerts.settings.active') : t('weatherAlerts.settings.inactive')}
                    </Text>
                  </VStack>
                  <HStack className="items-center">
                    <Button
                      variant="link"
                      size="xs"
                      onPress={() => {
                        setEditingZone(zone);
                        setZoneSheetOpen(true);
                      }}
                    >
                      <ButtonIcon as={PencilIcon} size="xs" />
                    </Button>
                    <Button
                      variant="link"
                      size="xs"
                      onPress={() =>
                        confirmDelete(t('weatherAlerts.settings.delete_zone_confirm'), () => {
                          void useWeatherAlertsStore
                            .getState()
                            .deleteZone(zone.WeatherAlertZoneId)
                            .then(() => showToast('success', t('weatherAlerts.settings.saved')))
                            .catch(() => showToast('error', t('weatherAlerts.settings.save_error')));
                        })
                      }
                    >
                      <ButtonIcon as={Trash2Icon} size="xs" className="text-red-500" />
                    </Button>
                  </HStack>
                </HStack>
              ))}
            </VStack>
          )}
        </Box>

        {/* Sources */}
        <Box className={cardClass}>
          <HStack className="mb-2 items-center justify-between">
            <Heading size="sm">{t('weatherAlerts.settings.sources')}</Heading>
            <Button
              variant="link"
              size="xs"
              onPress={() => {
                setEditingSource(null);
                setSourceSheetOpen(true);
              }}
            >
              <ButtonIcon as={PlusIcon} size="xs" />
              <ButtonText className="text-xs">{t('weatherAlerts.settings.add_source')}</ButtonText>
            </Button>
          </HStack>
          {sources.length === 0 ? (
            <Text className="text-sm text-gray-500">{t('weatherAlerts.settings.no_sources')}</Text>
          ) : (
            <VStack className="space-y-2">
              {sources.map((source) => (
                <HStack key={source.WeatherAlertSourceId} className="items-center justify-between border-b border-outline-100 pb-1">
                  <VStack className="flex-1 pr-2">
                    <Text className="text-sm font-medium">{source.Name}</Text>
                    <Text className="text-xs text-gray-500">
                      {sourceTypeLabel(source.SourceType)} · {source.Active ? t('weatherAlerts.settings.active') : t('weatherAlerts.settings.inactive')}
                    </Text>
                    {source.IsFailure && source.ErrorMessage ? <Text className="text-xs text-red-500">{source.ErrorMessage}</Text> : null}
                  </VStack>
                  <HStack className="items-center">
                    <Button
                      variant="link"
                      size="xs"
                      onPress={() => {
                        setEditingSource(source);
                        setSourceSheetOpen(true);
                      }}
                    >
                      <ButtonIcon as={PencilIcon} size="xs" />
                    </Button>
                    <Button
                      variant="link"
                      size="xs"
                      onPress={() =>
                        confirmDelete(t('weatherAlerts.settings.delete_source_confirm'), () => {
                          void useWeatherAlertsStore
                            .getState()
                            .deleteSource(source.WeatherAlertSourceId)
                            .then(() => showToast('success', t('weatherAlerts.settings.saved')))
                            .catch(() => showToast('error', t('weatherAlerts.settings.save_error')));
                        })
                      }
                    >
                      <ButtonIcon as={Trash2Icon} size="xs" className="text-red-500" />
                    </Button>
                  </HStack>
                </HStack>
              ))}
            </VStack>
          )}
        </Box>
      </ScrollView>

      <WeatherAlertZoneSheet isOpen={zoneSheetOpen} onClose={() => setZoneSheetOpen(false)} zone={editingZone} />
      <WeatherAlertSourceSheet isOpen={sourceSheetOpen} onClose={() => setSourceSheetOpen(false)} source={editingSource} />
    </>
  );
}
