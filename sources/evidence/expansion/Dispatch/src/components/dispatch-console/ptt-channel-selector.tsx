import { Check, Radio } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FlatList, Pressable, StyleSheet, View } from 'react-native';

import { type DepartmentVoiceChannelResultData } from '@/models/v4/voice/departmentVoiceResultData';

import { Actionsheet, ActionsheetBackdrop, ActionsheetContent, ActionsheetDragIndicator, ActionsheetDragIndicatorWrapper } from '../ui/actionsheet';
import { Badge, BadgeText } from '../ui/badge';
import { Button, ButtonText } from '../ui/button';
import { Heading } from '../ui/heading';
import { HStack } from '../ui/hstack';
import { Icon } from '../ui/icon';
import { Text } from '../ui/text';
import { VStack } from '../ui/vstack';

interface PTTChannelSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  channels: DepartmentVoiceChannelResultData[];
  selectedChannelId?: string;
  onSelectChannel: (channelId: string) => void;
  isConnected: boolean;
}

export const PTTChannelSelector: React.FC<PTTChannelSelectorProps> = ({ isOpen, onClose, channels, selectedChannelId, onSelectChannel, isConnected }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';

  const renderChannelItem = ({ item }: { item: DepartmentVoiceChannelResultData }) => {
    const isSelected = item.Id === selectedChannelId;

    return (
      <Pressable onPress={() => onSelectChannel(item.Id)} style={StyleSheet.flatten([styles.channelItem, { backgroundColor: isDark ? '#1f2937' : '#f9fafb' }, isSelected && styles.channelItemSelected])}>
        <HStack className="flex-1 items-center justify-between">
          <HStack className="items-center" space="md">
            <View style={StyleSheet.flatten([styles.channelIcon, { backgroundColor: isSelected ? '#3b82f6' : isDark ? '#374151' : '#e5e7eb' }])}>
              <Icon as={Radio} size="sm" color={isSelected ? '#fff' : isDark ? '#9ca3af' : '#6b7280'} />
            </View>
            <VStack>
              <Text className={`font-medium ${isSelected ? 'text-blue-600 dark:text-blue-400' : ''}`}>{item.Name}</Text>
              {item.IsDefault ? (
                <Badge size="sm" variant="outline" action="info">
                  <BadgeText>{t('dispatch.default_channel')}</BadgeText>
                </Badge>
              ) : null}
            </VStack>
          </HStack>

          {isSelected ? (
            <View style={styles.checkIcon}>
              <Icon as={Check} size="sm" color="#22c55e" />
            </View>
          ) : null}
        </HStack>
      </Pressable>
    );
  };

  return (
    <Actionsheet isOpen={isOpen} onClose={onClose}>
      <ActionsheetBackdrop />
      <ActionsheetContent className={isDark ? 'bg-gray-900' : 'bg-white'}>
        <ActionsheetDragIndicatorWrapper>
          <ActionsheetDragIndicator />
        </ActionsheetDragIndicatorWrapper>

        <VStack className="w-full p-4" space="md">
          {/* Header */}
          <VStack space="xs" className="items-center">
            <Heading size="lg">{t('dispatch.select_channel')}</Heading>
            <Text className="text-center text-sm text-gray-500">{isConnected ? t('dispatch.change_channel_warning') : t('dispatch.select_channel_description')}</Text>
          </VStack>

          {/* Channel List */}
          {channels.length > 0 ? (
            <FlatList data={channels} renderItem={renderChannelItem} keyExtractor={(item) => item.Id} style={styles.channelList} contentContainerStyle={styles.channelListContent} showsVerticalScrollIndicator={false} />
          ) : (
            <VStack className="items-center py-8" space="sm">
              <Icon as={Radio} size="xl" color={isDark ? '#6b7280' : '#9ca3af'} />
              <Text className="text-center text-gray-500">{t('dispatch.no_channels_available')}</Text>
            </VStack>
          )}

          {/* Close Button */}
          <Button onPress={onClose} variant="outline" size="lg" className="mt-2">
            <ButtonText>{t('common.close')}</ButtonText>
          </Button>
        </VStack>
      </ActionsheetContent>
    </Actionsheet>
  );
};

const styles = StyleSheet.create({
  channelList: {
    maxHeight: 300,
  },
  channelListContent: {
    paddingVertical: 4,
  },
  channelItem: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  channelItemSelected: {
    borderWidth: 2,
    borderColor: '#3b82f6',
  },
  channelIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
