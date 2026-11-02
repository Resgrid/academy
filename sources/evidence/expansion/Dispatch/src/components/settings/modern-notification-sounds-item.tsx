import { useColorScheme } from 'nativewind';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Platform } from 'react-native';

import { useModernNotificationSounds } from '@/lib/hooks/use-modern-notification-sounds';

import { Switch } from '../ui/switch';
import { Text } from '../ui/text';
import { View } from '../ui/view';
import { VStack } from '../ui/vstack';

export const ModernNotificationSoundsItem = () => {
  const { isModernNotificationSoundsEnabled, setModernNotificationSoundsEnabled } = useModernNotificationSounds();
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();

  const handleToggle = React.useCallback(
    (value: boolean) => {
      setModernNotificationSoundsEnabled(value);
    },
    [setModernNotificationSoundsEnabled]
  );

  // Notification sounds are bound to Android channels; this setting is Android-only.
  if (Platform.OS !== 'android') {
    return null;
  }

  return (
    <VStack space="sm">
      <View className="flex-1 flex-row items-center justify-between px-4 py-2">
        <View className="flex-1 flex-row items-center pr-2">
          <Text>{t('settings.modern_notification_sounds')}</Text>
        </View>
        <View className="flex-row items-center">
          <Switch size="md" value={isModernNotificationSoundsEnabled} onValueChange={handleToggle} />
        </View>
      </View>

      <View className="px-4">
        <Text className={`text-sm ${colorScheme === 'dark' ? 'text-neutral-400' : 'text-neutral-500'}`}>{t('settings.modern_notification_sounds_description')}</Text>
      </View>
    </VStack>
  );
};
