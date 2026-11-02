import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CustomBottomSheet } from '@/components/ui/bottom-sheet';
import { Button, ButtonText } from '@/components/ui/button';
import { FormControl, FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';
import { HStack } from '@/components/ui/hstack';
import { Input, InputField } from '@/components/ui/input';
import { Select, SelectBackdrop, SelectContent, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { WeatherAlertSourceType } from '@/models/v4/weatherAlerts/weatherAlertEnums';
import { type WeatherAlertSourceResultData } from '@/models/v4/weatherAlerts/weatherAlertSourceResultData';
import { useToastStore } from '@/stores/toast/store';
import { useWeatherAlertsStore } from '@/stores/weatherAlerts/store';

interface WeatherAlertSourceSheetProps {
  isOpen: boolean;
  onClose: () => void;
  source?: WeatherAlertSourceResultData | null;
}

export const WeatherAlertSourceSheet: React.FC<WeatherAlertSourceSheetProps> = ({ isOpen, onClose, source }) => {
  const { t } = useTranslation();

  // Organization names map to localized display strings (values are the same brand names across locales).
  const sourceTypeOptions = [
    { value: WeatherAlertSourceType.NationalWeatherService, label: t('weatherAlerts.settings.source_type_national_weather_service') },
    { value: WeatherAlertSourceType.EnvironmentCanada, label: t('weatherAlerts.settings.source_type_environment_canada') },
    { value: WeatherAlertSourceType.MeteoAlarm, label: t('weatherAlerts.settings.source_type_meteoalarm') },
  ];
  const showToast = useToastStore((s) => s.showToast);
  const [name, setName] = useState('');
  const [sourceType, setSourceType] = useState(String(WeatherAlertSourceType.NationalWeatherService));
  const [areaFilter, setAreaFilter] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [customEndpoint, setCustomEndpoint] = useState('');
  const [pollInterval, setPollInterval] = useState('15');
  const [active, setActive] = useState(true);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setName(source?.Name ?? '');
    setSourceType(source ? String(source.SourceType) : String(WeatherAlertSourceType.NationalWeatherService));
    setAreaFilter(source?.AreaFilter ?? '');
    setApiKey(''); // never returned by the server (HasApiKey only); leave blank to keep existing
    setCustomEndpoint(source?.CustomEndpoint ?? '');
    setPollInterval(source ? String(source.PollIntervalMinutes) : '15');
    setActive(source ? source.Active : true);
  }, [isOpen, source]);

  const handleSubmit = async () => {
    if (!name.trim()) {
      showToast('error', t('weatherAlerts.settings.name_required'));
      return;
    }
    setBusy(true);
    try {
      await useWeatherAlertsStore.getState().saveSource({
        WeatherAlertSourceId: source?.WeatherAlertSourceId || undefined,
        Name: name.trim(),
        SourceType: parseInt(sourceType, 10),
        AreaFilter: areaFilter.trim(),
        ApiKey: apiKey.trim(),
        CustomEndpoint: customEndpoint.trim(),
        PollIntervalMinutes: parseInt(pollInterval, 10) || 15,
        Active: active,
      });
      showToast('success', t('weatherAlerts.settings.saved'));
      onClose();
    } catch {
      showToast('error', t('weatherAlerts.settings.save_error'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={busy}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{source ? t('weatherAlerts.settings.edit_source') : t('weatherAlerts.settings.add_source')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.source_name')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={name} onChangeText={setName} placeholder={t('weatherAlerts.settings.source_name')} />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.source_type')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={sourceType} onValueChange={setSourceType}>
            <SelectTrigger>
              <SelectInput />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {sourceTypeOptions.map((option) => (
                  <SelectItem key={option.value} label={option.label} value={String(option.value)} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.area_filter')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={areaFilter} onChangeText={setAreaFilter} placeholder={t('weatherAlerts.settings.area_filter')} autoCapitalize="none" />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.api_key')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={apiKey} onChangeText={setApiKey} placeholder={source?.HasApiKey ? t('weatherAlerts.settings.api_key_set') : ''} autoCapitalize="none" secureTextEntry />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.custom_endpoint')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={customEndpoint} onChangeText={setCustomEndpoint} placeholder="https://" autoCapitalize="none" />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.poll_interval')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={pollInterval} onChangeText={setPollInterval} keyboardType="numeric" placeholder="15" />
          </Input>
        </FormControl>
        <HStack className="items-center justify-between">
          <Text className="text-sm">{t('weatherAlerts.settings.active')}</Text>
          <Switch size="md" value={active} onValueChange={setActive} />
        </HStack>
        <HStack className="space-x-3 pt-2">
          <Button variant="outline" className="mr-2 flex-1" onPress={onClose} disabled={busy}>
            <ButtonText>{t('common.cancel')}</ButtonText>
          </Button>
          <Button className="ml-2 flex-1" onPress={handleSubmit} disabled={busy}>
            <ButtonText>{t('weatherAlerts.settings.save')}</ButtonText>
          </Button>
        </HStack>
      </VStack>
    </CustomBottomSheet>
  );
};
