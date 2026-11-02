import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CustomBottomSheet } from '@/components/ui/bottom-sheet';
import { Button, ButtonText } from '@/components/ui/button';
import { FormControl, FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';
import { HStack } from '@/components/ui/hstack';
import { Input, InputField } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { type WeatherAlertZoneResultData } from '@/models/v4/weatherAlerts/weatherAlertZoneResultData';
import { useToastStore } from '@/stores/toast/store';
import { useWeatherAlertsStore } from '@/stores/weatherAlerts/store';

interface WeatherAlertZoneSheetProps {
  isOpen: boolean;
  onClose: () => void;
  zone?: WeatherAlertZoneResultData | null;
}

export const WeatherAlertZoneSheet: React.FC<WeatherAlertZoneSheetProps> = ({ isOpen, onClose, zone }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const [name, setName] = useState('');
  const [zoneCode, setZoneCode] = useState('');
  const [center, setCenter] = useState('');
  const [radius, setRadius] = useState('25');
  const [isActive, setIsActive] = useState(true);
  const [isPrimary, setIsPrimary] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setName(zone?.Name ?? '');
    setZoneCode(zone?.ZoneCode ?? '');
    setCenter(zone?.CenterGeoLocation ?? '');
    setRadius(zone ? String(zone.RadiusMiles) : '25');
    setIsActive(zone ? zone.IsActive : true);
    setIsPrimary(zone ? zone.IsPrimary : false);
  }, [isOpen, zone]);

  const handleSubmit = async () => {
    if (!name.trim()) {
      showToast('error', t('weatherAlerts.settings.name_required'));
      return;
    }
    setBusy(true);
    try {
      await useWeatherAlertsStore.getState().saveZone({
        WeatherAlertZoneId: zone?.WeatherAlertZoneId || undefined,
        Name: name.trim(),
        ZoneCode: zoneCode.trim(),
        CenterGeoLocation: center.trim(),
        RadiusMiles: parseFloat(radius) || 0,
        IsActive: isActive,
        IsPrimary: isPrimary,
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
        <Text className="text-center text-lg font-semibold">{zone ? t('weatherAlerts.settings.edit_zone') : t('weatherAlerts.settings.add_zone')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.zone_name')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={name} onChangeText={setName} placeholder={t('weatherAlerts.settings.zone_name')} />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.zone_code')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={zoneCode} onChangeText={setZoneCode} placeholder="e.g. TXZ211" autoCapitalize="characters" />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.center_geo')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={center} onChangeText={setCenter} placeholder="lat,lng" autoCapitalize="none" />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('weatherAlerts.settings.radius_miles')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={radius} onChangeText={setRadius} keyboardType="numeric" placeholder="25" />
          </Input>
        </FormControl>
        <HStack className="items-center justify-between">
          <Text className="text-sm">{t('weatherAlerts.settings.active')}</Text>
          <Switch size="md" value={isActive} onValueChange={setIsActive} />
        </HStack>
        <HStack className="items-center justify-between">
          <Text className="text-sm">{t('weatherAlerts.settings.primary')}</Text>
          <Switch size="md" value={isPrimary} onValueChange={setIsPrimary} />
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
