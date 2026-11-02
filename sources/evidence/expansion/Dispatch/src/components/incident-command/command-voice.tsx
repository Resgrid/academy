import { MicIcon, PhoneOffIcon, PlusIcon, RadioIcon } from 'lucide-react-native';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { getConnectToSession } from '@/api/voice';
import { Box } from '@/components/ui/box';
import { Button, ButtonIcon, ButtonText } from '@/components/ui/button';
import { Heading } from '@/components/ui/heading';
import { HStack } from '@/components/ui/hstack';
import { Input, InputField } from '@/components/ui/input';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { hasIncidentCapability, IncidentCapabilities, IncidentCommandStatus } from '@/models/v4/incidentCommand/incidentCommandEnums';
import { type DepartmentVoiceChannel } from '@/models/v4/incidentCommand/incidentVoiceChannel';
import { useLiveKitStore } from '@/stores/app/livekit-store';
import { useIncidentCommandStore } from '@/stores/incident-command/store';
import { useToastStore } from '@/stores/toast/store';

/** Incident voice channels: create / list / join on-demand PTT channels via the LiveKit stack. */
export const CommandVoice: React.FC = () => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const channels = useIncidentCommandStore((s) => s.voiceChannels);
  const capabilities = useIncidentCommandStore((s) => s.capabilities);
  const board = useIncidentCommandStore((s) => s.board);
  const isConnected = useLiveKitStore((s) => s.isConnected);
  const currentRoomInfo = useLiveKitStore((s) => s.currentRoomInfo);
  const isTalking = useLiveKitStore((s) => s.isTalking);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);

  const canManageChannels = hasIncidentCapability(capabilities, IncidentCapabilities.ManageChannels);
  const isClosed = board?.Command?.Status === IncidentCommandStatus.Closed;

  useEffect(() => {
    useIncidentCommandStore.getState().fetchChannels();
  }, []);

  const openChannels = channels.filter((c) => !c.ClosedOn);

  const join = async (channel: DepartmentVoiceChannel) => {
    setBusy(true);
    try {
      await useLiveKitStore.getState().fetchVoiceSettings();
      const result = await getConnectToSession(channel.SystemConferenceId);
      const token = result?.Data?.Token;
      if (!token) throw new Error('No voice token issued');
      await useLiveKitStore.getState().connectToRoom({ Id: channel.DepartmentVoiceChannelId, Name: channel.Name, ConferenceNumber: channel.ConferenceNumber, IsDefault: channel.IsDefault, Token: token }, token);
      showToast('success', t('incident_command.voice_joined'));
    } catch {
      showToast('error', t('incident_command.voice_join_error'));
    } finally {
      setBusy(false);
    }
  };

  const leave = async () => {
    try {
      await useLiveKitStore.getState().disconnectFromRoom();
    } catch {
      // ignore — already disconnected
    }
  };

  const setTalking = async (on: boolean) => {
    const room = useLiveKitStore.getState().currentRoom;
    if (!room) return;
    try {
      await room.localParticipant.setMicrophoneEnabled(on);
      useLiveKitStore.getState().setIsTalking(on);
    } catch {
      // ignore transient mic errors
    }
  };

  const createChannel = async () => {
    if (!name.trim()) return;
    setBusy(true);
    try {
      await useIncidentCommandStore.getState().createChannel(name.trim());
      showToast('success', t('incident_command.saved'));
      setName('');
      setCreating(false);
    } catch {
      showToast('error', t('incident_command.save_error'));
    } finally {
      setBusy(false);
    }
  };

  const closeAll = async () => {
    setBusy(true);
    try {
      await useIncidentCommandStore.getState().closeChannels();
      showToast('success', t('incident_command.saved'));
    } catch {
      showToast('error', t('incident_command.save_error'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box className="mb-3 rounded-lg bg-background-50 p-3">
      <HStack className="mb-2 items-center justify-between">
        <HStack className="items-center space-x-2">
          <RadioIcon size={16} />
          <Heading size="sm">{t('incident_command.voice_channels')}</Heading>
        </HStack>
        {!isClosed && canManageChannels ? (
          <Button variant="link" size="xs" onPress={() => setCreating((v) => !v)}>
            <ButtonIcon as={PlusIcon} size="xs" />
            <ButtonText className="text-xs">{t('incident_command.add_channel')}</ButtonText>
          </Button>
        ) : null}
      </HStack>

      {creating ? (
        <HStack className="mb-2 items-center space-x-2">
          <Box className="mr-2 flex-1">
            <Input>
              <InputField value={name} onChangeText={setName} placeholder={t('incident_command.channel_name')} />
            </Input>
          </Box>
          <Button size="xs" onPress={createChannel} disabled={busy}>
            <ButtonText className="text-xs">{t('incident_command.save')}</ButtonText>
          </Button>
        </HStack>
      ) : null}

      {openChannels.length === 0 ? (
        <Text className="text-sm text-gray-500">{t('incident_command.no_channels')}</Text>
      ) : (
        <VStack className="space-y-2">
          {openChannels.map((channel) => {
            const joined = isConnected && currentRoomInfo?.Id === channel.DepartmentVoiceChannelId;
            return (
              <HStack key={channel.DepartmentVoiceChannelId} className="items-center justify-between border-b border-outline-100 pb-1">
                <Text className="flex-1 text-sm">{channel.Name}</Text>
                {joined ? (
                  <HStack className="items-center space-x-2">
                    <Button size="xs" variant={isTalking ? 'solid' : 'outline'} onPressIn={() => setTalking(true)} onPressOut={() => setTalking(false)}>
                      <ButtonIcon as={MicIcon} size="xs" className="mr-1" />
                      <ButtonText className="text-xs">{isTalking ? t('incident_command.talking') : t('incident_command.hold_to_talk')}</ButtonText>
                    </Button>
                    <Button size="xs" variant="outline" className="ml-2" onPress={leave}>
                      <ButtonIcon as={PhoneOffIcon} size="xs" className="text-red-500" />
                    </Button>
                  </HStack>
                ) : (
                  <Button size="xs" variant="outline" onPress={() => join(channel)} disabled={busy}>
                    <ButtonText className="text-xs">{t('incident_command.join')}</ButtonText>
                  </Button>
                )}
              </HStack>
            );
          })}
        </VStack>
      )}

      {!isClosed && canManageChannels && openChannels.length > 0 ? (
        <Button variant="link" size="xs" className="mt-2" onPress={closeAll}>
          <ButtonText className="text-xs text-red-500">{t('incident_command.close_all_channels')}</ButtonText>
        </Button>
      ) : null}
    </Box>
  );
};

export default CommandVoice;
