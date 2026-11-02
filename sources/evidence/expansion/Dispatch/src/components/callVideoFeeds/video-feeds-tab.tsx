import { PlusIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Alert, FlatList } from 'react-native';

import { Box } from '@/components/ui/box';
import { Button, ButtonIcon, ButtonText } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { type CallVideoFeedResultData } from '@/models/v4/callVideoFeeds/callVideoFeedResultData';
import { useCallVideoFeedsStore } from '@/stores/callVideoFeeds/store';
import { useToastStore } from '@/stores/toast/store';

import { VideoFeedCard } from './video-feed-card';
import { VideoFeedFormSheet } from './video-feed-form-sheet';
import { VideoPlayer } from './video-player';

interface VideoFeedsTabProps {
  callId: string;
  canEdit: boolean;
}

export const VideoFeedsTab: React.FC<VideoFeedsTabProps> = ({ callId, canEdit }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const showToast = useToastStore((state) => state.showToast);
  const { feeds, isLoading, error, fetchFeeds, removeFeed, reset } = useCallVideoFeedsStore();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingFeed, setEditingFeed] = useState<CallVideoFeedResultData | null>(null);
  const [watchingFeed, setWatchingFeed] = useState<CallVideoFeedResultData | null>(null);

  useEffect(() => {
    if (callId) {
      fetchFeeds(callId);
    }
    return () => reset();
  }, [callId, fetchFeeds, reset]);

  const handleWatch = useCallback((feed: CallVideoFeedResultData) => {
    setWatchingFeed(feed);
  }, []);

  const handleEdit = useCallback((feed: CallVideoFeedResultData) => {
    setEditingFeed(feed);
    setIsFormOpen(true);
  }, []);

  const handleDelete = useCallback(
    (feedId: string) => {
      Alert.alert(t('videoFeeds.deleteFeed'), t('videoFeeds.deleteConfirm'), [
        { text: t('common.cancel'), style: 'cancel' },
        {
          text: t('common.delete'),
          style: 'destructive',
          onPress: async () => {
            const success = await removeFeed(feedId, callId);
            if (success) {
              showToast('success', t('videoFeeds.feedDeleted'));
            } else {
              showToast('error', t('videoFeeds.feedError'));
            }
          },
        },
      ]);
    },
    [callId, removeFeed, showToast, t]
  );

  const handleAddNew = useCallback(() => {
    setEditingFeed(null);
    setIsFormOpen(true);
  }, []);

  const handleCloseForm = useCallback(() => {
    setIsFormOpen(false);
    setEditingFeed(null);
  }, []);

  const renderFeed = useCallback(
    ({ item }: { item: CallVideoFeedResultData }) => <VideoFeedCard feed={item} onWatch={handleWatch} onEdit={canEdit ? handleEdit : undefined} onDelete={canEdit ? handleDelete : undefined} canEdit={canEdit} />,
    [canEdit, handleWatch, handleEdit, handleDelete]
  );

  if (isLoading) {
    return (
      <Box className="p-4">
        <Text className="text-center text-gray-500">{t('common.loading')}</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className="p-4">
        <Text className="text-center text-red-500">{error}</Text>
      </Box>
    );
  }

  return (
    <VStack className="flex-1 p-4">
      {feeds.length === 0 ? (
        <Box className="items-center py-8">
          <Text className="mb-4 text-center text-gray-500">{t('videoFeeds.noFeeds')}</Text>
          {canEdit && (
            <Button onPress={handleAddNew}>
              <ButtonIcon as={PlusIcon} className="mr-1" />
              <ButtonText>{t('videoFeeds.addFeed')}</ButtonText>
            </Button>
          )}
        </Box>
      ) : (
        <>
          <FlatList data={feeds} renderItem={renderFeed} keyExtractor={(item) => item.CallVideoFeedId} scrollEnabled={false} />
          {canEdit && (
            <Button onPress={handleAddNew} variant="outline" className="mt-2">
              <ButtonIcon as={PlusIcon} className="mr-1" />
              <ButtonText>{t('videoFeeds.addFeed')}</ButtonText>
            </Button>
          )}
        </>
      )}

      {/* Add/Edit Form */}
      <VideoFeedFormSheet isOpen={isFormOpen} onClose={handleCloseForm} callId={callId} editFeed={editingFeed} />

      {/* Video Player Modal */}
      {watchingFeed && <VideoPlayer feed={watchingFeed} visible={!!watchingFeed} onClose={() => setWatchingFeed(null)} />}
    </VStack>
  );
};
