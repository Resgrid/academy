import { addDays, addHours, format, isValid, parse, set } from 'date-fns';
import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CustomBottomSheet } from '@/components/ui/bottom-sheet';
import { Button, ButtonText } from '@/components/ui/button';
import { FormControl, FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';
import { HStack } from '@/components/ui/hstack';
import { Input, InputField } from '@/components/ui/input';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { useCallDetailStore } from '@/stores/calls/detail-store';
import { useScheduledCallsStore } from '@/stores/calls/scheduled-store';
import { useCallsStore } from '@/stores/calls/store';
import { useToastStore } from '@/stores/toast/store';

const FMT = 'yyyy-MM-dd HH:mm';

interface RescheduleCallSheetProps {
  isOpen: boolean;
  onClose: () => void;
  callId: string;
}

/**
 * Reschedules the dispatch time of a pending scheduled call. Uses text date/time entry with quick
 * presets (no native picker dependency); the value is sent as a department-local datetime.
 */
export const RescheduleCallSheet: React.FC<RescheduleCallSheetProps> = ({ isOpen, onClose, callId }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const call = useCallDetailStore((s) => s.call);
  const isLoading = useCallDetailStore((s) => s.isLoading);
  const [value, setValue] = useState('');

  useEffect(() => {
    if (!isOpen) return;
    const source = call?.ScheduledOn || call?.ScheduledOnUtc || call?.DispatchedOn || '';
    const parsedSource = source ? new Date(source) : new Date();
    setValue(format(isValid(parsedSource) ? parsedSource : new Date(), FMT));
  }, [isOpen, call?.ScheduledOn, call?.ScheduledOnUtc, call?.DispatchedOn]);

  const parsed = useMemo(() => parse(value, FMT, new Date()), [value]);
  const valid = isValid(parsed);
  const applyPreset = (date: Date) => setValue(format(date, FMT));

  const handleSubmit = async () => {
    if (!valid) {
      showToast('error', t('call_detail.reschedule_invalid'));
      return;
    }
    try {
      await useCallDetailStore.getState().rescheduleDispatchTime(callId, format(parsed, "yyyy-MM-dd'T'HH:mm:ss"));
      showToast('success', t('call_detail.reschedule_success'));
      await useScheduledCallsStore.getState().fetchScheduledCalls();
      await useCallsStore.getState().fetchCalls();
      onClose();
    } catch {
      showToast('error', t('call_detail.reschedule_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isLoading}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('call_detail.reschedule')}</Text>

        <HStack className="flex-wrap justify-center gap-2">
          <Button variant="outline" size="xs" onPress={() => applyPreset(addHours(new Date(), 1))}>
            <ButtonText className="text-xs">{t('call_detail.reschedule_in_1_hour')}</ButtonText>
          </Button>
          <Button variant="outline" size="xs" onPress={() => applyPreset(addDays(new Date(), 1))}>
            <ButtonText className="text-xs">{t('call_detail.reschedule_in_1_day')}</ButtonText>
          </Button>
          <Button variant="outline" size="xs" onPress={() => applyPreset(set(addDays(new Date(), 1), { hours: 8, minutes: 0, seconds: 0, milliseconds: 0 }))}>
            <ButtonText className="text-xs">{t('call_detail.reschedule_tomorrow_morning')}</ButtonText>
          </Button>
        </HStack>

        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('call_detail.reschedule_datetime')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={value} onChangeText={setValue} placeholder={FMT} autoCapitalize="none" />
          </Input>
        </FormControl>

        <Text className={`text-center text-sm ${valid ? 'text-gray-500' : 'text-red-500'}`}>{valid ? format(parsed, 'PPpp') : t('call_detail.reschedule_invalid')}</Text>

        <HStack className="space-x-3 pt-4">
          <Button variant="outline" className="mr-2 flex-1" onPress={onClose} disabled={isLoading}>
            <ButtonText>{t('common.cancel')}</ButtonText>
          </Button>
          <Button className="ml-2 flex-1" onPress={handleSubmit} disabled={isLoading || !valid}>
            <ButtonText>{t('call_detail.reschedule')}</ButtonText>
          </Button>
        </HStack>
      </VStack>
    </CustomBottomSheet>
  );
};
