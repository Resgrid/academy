import { CameraIcon, CircleIcon, CloudIcon, EllipsisVerticalIcon, EyeIcon, GlobeIcon, MonitorIcon, PencilIcon, PlayIcon, SatelliteIcon, TrafficConeIcon, Trash2Icon, VideoIcon } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable } from 'react-native';

import { Box } from '@/components/ui/box';
import { Button, ButtonIcon, ButtonText } from '@/components/ui/button';
import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { CallVideoFeedFormat, CallVideoFeedStatus, CallVideoFeedType } from '@/models/v4/callVideoFeeds/callVideoFeedEnums';
import { type CallVideoFeedResultData } from '@/models/v4/callVideoFeeds/callVideoFeedResultData';

interface VideoFeedCardProps {
  feed: CallVideoFeedResultData;
  onWatch: (feed: CallVideoFeedResultData) => void;
  onEdit?: (feed: CallVideoFeedResultData) => void;
  onDelete?: (feedId: string) => void;
  canEdit: boolean;
}

const getFeedTypeIcon = (feedType: number | null) => {
  switch (feedType) {
    case CallVideoFeedType.Drone:
      return GlobeIcon;
    case CallVideoFeedType.FixedCamera:
      return CameraIcon;
    case CallVideoFeedType.BodyCam:
      return EyeIcon;
    case CallVideoFeedType.TrafficCam:
      return TrafficConeIcon;
    case CallVideoFeedType.WeatherCam:
      return CloudIcon;
    case CallVideoFeedType.SatelliteFeed:
      return SatelliteIcon;
    case CallVideoFeedType.WebCam:
      return MonitorIcon;
    default:
      return VideoIcon;
  }
};

const getFeedTypeName = (feedType: number | null, t: (key: string) => string): string => {
  switch (feedType) {
    case CallVideoFeedType.Drone:
      return t('videoFeeds.type.drone');
    case CallVideoFeedType.FixedCamera:
      return t('videoFeeds.type.fixedCamera');
    case CallVideoFeedType.BodyCam:
      return t('videoFeeds.type.bodyCam');
    case CallVideoFeedType.TrafficCam:
      return t('videoFeeds.type.trafficCam');
    case CallVideoFeedType.WeatherCam:
      return t('videoFeeds.type.weatherCam');
    case CallVideoFeedType.SatelliteFeed:
      return t('videoFeeds.type.satelliteFeed');
    case CallVideoFeedType.WebCam:
      return t('videoFeeds.type.webCam');
    default:
      return t('videoFeeds.type.other');
  }
};

const getFeedFormatName = (feedFormat: number | null, t: (key: string) => string): string => {
  switch (feedFormat) {
    case CallVideoFeedFormat.RTSP:
      return t('videoFeeds.format.rtsp');
    case CallVideoFeedFormat.HLS:
      return t('videoFeeds.format.hls');
    case CallVideoFeedFormat.MJPEG:
      return t('videoFeeds.format.mjpeg');
    case CallVideoFeedFormat.YouTubeLive:
      return t('videoFeeds.format.youtubeLive');
    case CallVideoFeedFormat.WebRTC:
      return t('videoFeeds.format.webrtc');
    case CallVideoFeedFormat.DASH:
      return t('videoFeeds.format.dash');
    case CallVideoFeedFormat.Embed:
      return t('videoFeeds.format.embed');
    default:
      return t('videoFeeds.format.other');
  }
};

const getStatusColor = (status: number): string => {
  switch (status) {
    case CallVideoFeedStatus.Active:
      return '#22c55e';
    case CallVideoFeedStatus.Inactive:
      return '#9ca3af';
    case CallVideoFeedStatus.Error:
      return '#ef4444';
    default:
      return '#9ca3af';
  }
};

const getStatusName = (status: number, t: (key: string) => string): string => {
  switch (status) {
    case CallVideoFeedStatus.Active:
      return t('videoFeeds.status.active');
    case CallVideoFeedStatus.Inactive:
      return t('videoFeeds.status.inactive');
    case CallVideoFeedStatus.Error:
      return t('videoFeeds.status.error');
    default:
      return t('videoFeeds.status.inactive');
  }
};

export const VideoFeedCard: React.FC<VideoFeedCardProps> = ({ feed, onWatch, onEdit, onDelete, canEdit }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';
  const [showMenu, setShowMenu] = useState(false);
  const TypeIcon = getFeedTypeIcon(feed.FeedType);

  return (
    <Box className={`mb-3 rounded-lg border p-3 ${isDark ? 'border-neutral-700 bg-neutral-800' : 'border-neutral-200 bg-white'}`}>
      <HStack className="items-center justify-between">
        <HStack className="flex-1 items-center gap-2">
          <TypeIcon size={20} color={isDark ? '#d1d5db' : '#374151'} />
          <VStack className="flex-1">
            <HStack className="items-center gap-2">
              <Text className="font-semibold">{feed.Name}</Text>
              <HStack className="items-center gap-1">
                <CircleIcon size={8} color={getStatusColor(feed.Status)} fill={getStatusColor(feed.Status)} />
                <Text className="text-xs" style={{ color: getStatusColor(feed.Status) }}>
                  {getStatusName(feed.Status, t)}
                </Text>
              </HStack>
            </HStack>
            <Text className="text-xs text-gray-500">
              {getFeedTypeName(feed.FeedType, t)} · {getFeedFormatName(feed.FeedFormat, t)}
            </Text>
            <Text className="text-xs text-gray-400">
              {feed.FullName} · {feed.AddedOnFormatted}
            </Text>
          </VStack>
        </HStack>

        <HStack className="items-center gap-2">
          <Button size="sm" variant="solid" onPress={() => onWatch(feed)}>
            <ButtonIcon as={PlayIcon} className="mr-1" />
            <ButtonText className="text-xs">{t('videoFeeds.watch')}</ButtonText>
          </Button>

          {canEdit && (
            <Pressable onPress={() => setShowMenu(!showMenu)}>
              <EllipsisVerticalIcon size={20} color={isDark ? '#d1d5db' : '#6b7280'} />
            </Pressable>
          )}
        </HStack>
      </HStack>

      {showMenu && canEdit && (
        <HStack className={`mt-2 gap-2 border-t pt-2 ${isDark ? 'border-neutral-700' : 'border-neutral-200'}`}>
          {onEdit && (
            <Button
              size="xs"
              variant="outline"
              onPress={() => {
                onEdit(feed);
                setShowMenu(false);
              }}
            >
              <ButtonIcon as={PencilIcon} className="mr-1" />
              <ButtonText className="text-xs">{t('common.edit')}</ButtonText>
            </Button>
          )}
          {onDelete && (
            <Button
              size="xs"
              variant="outline"
              className="border-red-300"
              onPress={() => {
                onDelete(feed.CallVideoFeedId);
                setShowMenu(false);
              }}
            >
              <ButtonIcon as={Trash2Icon} className="mr-1 text-red-500" />
              <ButtonText className="text-xs text-red-500">{t('common.delete')}</ButtonText>
            </Button>
          )}
        </HStack>
      )}
    </Box>
  );
};
