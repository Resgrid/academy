import { AlertTriangle, X } from 'lucide-react-native';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Platform, Pressable, StyleSheet } from 'react-native';

import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { type CallPriorityResultData } from '@/models/v4/callPriorities/callPriorityResultData';
import { type CallResultData } from '@/models/v4/calls/callResultData';

interface ActiveCallFilterBannerProps {
  call: CallResultData;
  priority?: CallPriorityResultData;
  onClearFilter: () => void;
}

export const ActiveCallFilterBanner: React.FC<ActiveCallFilterBannerProps> = ({ call, priority, onClearFilter }) => {
  const { t } = useTranslation();
  const bgColor = priority?.Color || '#6366f1';

  return (
    <HStack style={StyleSheet.flatten([styles.banner, { backgroundColor: bgColor }])} className="items-center justify-between rounded-lg px-3 py-2">
      <HStack className="flex-1 items-center" space="sm">
        <Icon as={AlertTriangle} size="sm" color="#fff" />
        <Text className="flex-1 text-sm font-semibold text-white" numberOfLines={1}>
          {t('dispatch.filtering_by_call')}: #{call.Number} - {call.Name || call.Nature}
        </Text>
      </HStack>
      <Pressable onPress={onClearFilter} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }} style={styles.clearButton}>
        <HStack className="items-center" space="xs">
          <Text className="text-xs font-medium text-white opacity-90">{t('dispatch.clear_filter')}</Text>
          <Icon as={X} size="xs" color="#fff" />
        </HStack>
      </Pressable>
    </HStack>
  );
};

const styles = StyleSheet.create({
  banner: {
    ...Platform.select({
      web: {
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.15)',
      },
      default: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.15,
        shadowRadius: 4,
        elevation: 3,
      },
    }),
  } as any,
  clearButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
});
