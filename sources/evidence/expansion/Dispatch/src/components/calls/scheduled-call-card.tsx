import { format } from 'date-fns';
import { AlertTriangle, CalendarClock, MapPin, Radio } from 'lucide-react-native';
import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { StyleSheet, Text as RNText, View } from 'react-native';

import { invertColor, stripHtmlTags, toRgbaWithAlpha } from '@/lib/utils';
import { type CallPriorityResultData } from '@/models/v4/callPriorities/callPriorityResultData';
import { type CallResultData } from '@/models/v4/calls/callResultData';
import { type DispatchedEventResultData } from '@/models/v4/calls/dispatchedEventResultData';

function getColor(call: CallResultData, priority: CallPriorityResultData | undefined) {
  if (!call || call.CallId === '0') return '#808080';
  if (priority?.Color) return priority.Color;
  return '#808080';
}

const getDispatchTypeStyle = (type: string): { bg: string; fg: string; label: string } => {
  const t = (type || '').toLowerCase();
  if (t.includes('user') || t.includes('personnel')) return { bg: '#2563eb', fg: '#ffffff', label: 'P' };
  if (t.includes('unit')) return { bg: '#d97706', fg: '#ffffff', label: 'U' };
  if (t.includes('group')) return { bg: '#059669', fg: '#ffffff', label: 'G' };
  if (t.includes('role')) return { bg: '#7c3aed', fg: '#ffffff', label: 'R' };
  return { bg: '#6b7280', fg: '#ffffff', label: '•' };
};

const DispatchBadge: React.FC<{ dispatch: DispatchedEventResultData; textColor: string }> = React.memo(({ dispatch, textColor: _ }) => {
  const ts = getDispatchTypeStyle(dispatch.Type);
  return (
    <View style={StyleSheet.flatten([styles.dispatchBadge, { backgroundColor: ts.bg }])}>
      <RNText style={StyleSheet.flatten([styles.dispatchBadgeLabel, { color: ts.fg }])}>{ts.label}</RNText>
      <View style={styles.dispatchBadgeDivider} />
      <RNText style={StyleSheet.flatten([styles.dispatchBadgeName, { color: ts.fg }])} numberOfLines={1}>
        {dispatch.Name}
      </RNText>
    </View>
  );
});

DispatchBadge.displayName = 'DispatchBadge';

interface ScheduledCallCardProps {
  call: CallResultData;
  priority: CallPriorityResultData | undefined;
  dispatches?: DispatchedEventResultData[];
  isLoadingDispatches?: boolean;
}

export const ScheduledCallCard: React.FC<ScheduledCallCardProps> = React.memo(({ call, priority, dispatches, isLoadingDispatches }) => {
  const { t } = useTranslation();
  const bgColor = getColor(call, priority);
  const textColor = invertColor(bgColor, true);

  const natureText = useMemo(() => {
    if (!call.Nature) return '';
    return stripHtmlTags(call.Nature).trim();
  }, [call.Nature]);

  const scheduledDateDisplay = useMemo(() => {
    const dateStr = call.ScheduledOn || call.ScheduledOnUtc || call.DispatchedOn || call.DispatchedOnUtc;
    if (!dateStr) return null;
    try {
      return format(new Date(dateStr), 'MMM d, yyyy h:mm a');
    } catch {
      return null;
    }
  }, [call.ScheduledOn, call.ScheduledOnUtc, call.DispatchedOn, call.DispatchedOnUtc]);

  return (
    <View style={StyleSheet.flatten([styles.card, { backgroundColor: bgColor }])}>
      {/* Header Row: Call Number, Name */}
      <View style={styles.headerRow}>
        <View style={styles.titleGroup}>
          <AlertTriangle size={14} color={textColor} />
          <RNText style={StyleSheet.flatten([styles.callNumber, { color: textColor }])}>#{call.Number}</RNText>
          <RNText style={StyleSheet.flatten([styles.callName, { color: textColor }])} numberOfLines={1} ellipsizeMode="tail">
            {call.Name}
          </RNText>
        </View>
      </View>

      {/* Scheduled Date/Time - prominent display */}
      {scheduledDateDisplay ? (
        <View style={styles.scheduledRow}>
          <CalendarClock size={12} color={textColor} style={styles.rowIcon} />
          <RNText style={StyleSheet.flatten([styles.scheduledText, { color: textColor }])}>
            {t('scheduled_calls.scheduled_for')}: {scheduledDateDisplay}
          </RNText>
        </View>
      ) : null}

      {/* Address Row */}
      {call.Address ? (
        <View style={styles.addressRow}>
          <MapPin size={12} color={textColor} style={styles.rowIcon} />
          <RNText style={StyleSheet.flatten([styles.addressText, { color: textColor }])} numberOfLines={1} ellipsizeMode="tail">
            {call.Address}
          </RNText>
        </View>
      ) : null}

      {/* Nature Preview */}
      {natureText ? (
        <View style={styles.natureContainer}>
          <RNText style={StyleSheet.flatten([styles.natureText, { color: textColor }])} numberOfLines={1} ellipsizeMode="tail">
            {natureText}
          </RNText>
        </View>
      ) : null}

      {/* Dispatched Units Row */}
      <View style={StyleSheet.flatten([styles.dispatchDivider, { backgroundColor: toRgbaWithAlpha(textColor, 0.25) }])} />
      <View style={styles.dispatchRow}>
        <Radio size={10} color={textColor} style={styles.dispatchIcon} />
        {isLoadingDispatches ? (
          <RNText style={StyleSheet.flatten([styles.dispatchPlaceholder, { color: toRgbaWithAlpha(textColor, 0.5) }])}>…</RNText>
        ) : dispatches && dispatches.length > 0 ? (
          <View style={styles.dispatchBadgeList}>
            {dispatches.map((d, i) => (
              <React.Fragment key={d.Id || `${d.Name}-${i}`}>
                {i > 0 ? <View style={styles.dispatchBadgeGap} /> : null}
                <DispatchBadge dispatch={d} textColor={textColor} />
              </React.Fragment>
            ))}
          </View>
        ) : (
          <RNText style={StyleSheet.flatten([styles.dispatchPlaceholder, { color: toRgbaWithAlpha(textColor, 0.5) }])}>—</RNText>
        )}
      </View>
    </View>
  );
});

ScheduledCallCard.displayName = 'ScheduledCallCard';

const styles = StyleSheet.create({
  card: {
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    marginBottom: 8,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  titleGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 8,
  },
  callNumber: {
    fontSize: 13,
    fontWeight: '700',
    marginLeft: 6,
    marginRight: 4,
  },
  callName: {
    fontSize: 13,
    fontWeight: '600',
    flex: 1,
  },
  scheduledRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 3,
  },
  scheduledText: {
    fontSize: 12,
    fontWeight: '600',
  },
  addressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 3,
  },
  addressText: {
    fontSize: 11,
    flex: 1,
    opacity: 0.9,
  },
  rowIcon: {
    marginRight: 4,
    opacity: 0.85,
  },
  natureContainer: {
    marginBottom: 3,
    paddingTop: 3,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(255, 255, 255, 0.2)',
  },
  natureText: {
    fontSize: 11,
    fontStyle: 'italic',
    opacity: 0.85,
  },
  dispatchDivider: {
    height: StyleSheet.hairlineWidth,
    marginTop: 4,
    marginBottom: 4,
  },
  dispatchRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dispatchIcon: {
    marginRight: 5,
    opacity: 0.8,
  },
  dispatchBadgeList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    flex: 1,
  },
  dispatchBadgeGap: {
    width: 4,
  },
  dispatchBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 10,
    paddingVertical: 1,
    paddingHorizontal: 5,
    marginBottom: 2,
  },
  dispatchBadgeLabel: {
    fontSize: 9,
    fontWeight: '700',
  },
  dispatchBadgeDivider: {
    width: 1,
    height: 10,
    backgroundColor: 'rgba(255,255,255,0.4)',
    marginHorizontal: 3,
  },
  dispatchBadgeName: {
    fontSize: 9,
    maxWidth: 80,
  },
  dispatchPlaceholder: {
    fontSize: 11,
  },
});
