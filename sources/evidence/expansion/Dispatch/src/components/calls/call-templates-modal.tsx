import { FileTextIcon, SearchIcon, X } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityIndicator, Modal, ScrollView, StyleSheet, TextInput, TouchableOpacity, View } from 'react-native';

import { getAllCallQuickTemplates } from '@/api/calls/callTemplates';
import { Text } from '@/components/ui/text';
import { type CallQuickTemplateResultData } from '@/models/v4/templates/callQuickTemplateResultData';

export interface TemplateSelection {
  name: string;
  nature: string;
  type: string;
  priority: number;
}

interface CallTemplatesModalProps {
  isVisible: boolean;
  onClose: () => void;
  onSelect: (template: TemplateSelection) => void;
}

export const CallTemplatesModal: React.FC<CallTemplatesModalProps> = ({ isVisible, onClose, onSelect }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';

  const [templates, setTemplates] = useState<CallQuickTemplateResultData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isVisible) {
      loadTemplates();
    } else {
      setSearchQuery('');
    }
  }, [isVisible]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const result = await getAllCallQuickTemplates();
      setTemplates((result?.Data ?? []).filter((t) => !t.IsDisabled));
    } catch {
      // silently handle
    } finally {
      setIsLoading(false);
    }
  };

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return templates;
    const q = searchQuery.toLowerCase();
    return templates.filter((t) => t.Name.toLowerCase().includes(q) || t.CallName.toLowerCase().includes(q) || t.CallNature.toLowerCase().includes(q));
  }, [templates, searchQuery]);

  const handleSelect = useCallback(
    (template: CallQuickTemplateResultData) => {
      onSelect({
        name: template.CallName,
        nature: template.CallNature,
        type: template.CallType,
        priority: template.CallPriority,
      });
      onClose();
    },
    [onSelect, onClose]
  );

  if (!isVisible) return null;

  return (
    <Modal visible={isVisible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={StyleSheet.flatten([styles.container, isDark ? styles.containerDark : styles.containerLight])}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <FileTextIcon size={20} color={isDark ? '#e5e7eb' : '#111827'} />
              <Text style={StyleSheet.flatten([styles.title, isDark ? styles.titleDark : styles.titleLight])}>{t('calls.templates.title', 'Call Templates')}</Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn} accessibilityLabel={t('common.close')}>
              <X size={20} color={isDark ? '#9ca3af' : '#6b7280'} />
            </TouchableOpacity>
          </View>

          {/* Search */}
          <View style={StyleSheet.flatten([styles.searchContainer, isDark ? styles.searchContainerDark : styles.searchContainerLight])}>
            <SearchIcon size={16} color={isDark ? '#9ca3af' : '#6b7280'} />
            <TextInput
              style={StyleSheet.flatten([styles.searchInput, isDark ? styles.searchInputDark : styles.searchInputLight])}
              placeholder={t('calls.templates.search_placeholder', 'Search templates...')}
              placeholderTextColor={isDark ? '#6b7280' : '#9ca3af'}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>

          {/* Content */}
          {isLoading ? (
            <View style={styles.center}>
              <ActivityIndicator color="#2563eb" />
            </View>
          ) : filtered.length === 0 ? (
            <View style={styles.center}>
              <Text style={StyleSheet.flatten([styles.emptyText, isDark ? styles.emptyTextDark : styles.emptyTextLight])}>{t('calls.templates.none', 'No templates available')}</Text>
            </View>
          ) : (
            <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
              {filtered.map((template) => (
                <TouchableOpacity
                  key={template.Id}
                  style={StyleSheet.flatten([styles.item, isDark ? styles.itemDark : styles.itemLight])}
                  onPress={() => handleSelect(template)}
                  accessibilityRole="button"
                  accessibilityLabel={template.Name}
                >
                  <Text style={StyleSheet.flatten([styles.itemName, isDark ? styles.itemNameDark : styles.itemNameLight])}>{template.Name}</Text>
                  {!!template.CallName && (
                    <Text style={StyleSheet.flatten([styles.itemMeta, isDark ? styles.itemMetaDark : styles.itemMetaLight])}>
                      {t('calls.name')}: {template.CallName}
                    </Text>
                  )}
                  {!!template.CallNature && (
                    <Text style={StyleSheet.flatten([styles.itemMeta, isDark ? styles.itemMetaDark : styles.itemMetaLight])} numberOfLines={2}>
                      {t('calls.nature')}: {template.CallNature}
                    </Text>
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  container: {
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: '80%',
    paddingBottom: 24,
  },
  containerDark: { backgroundColor: '#171717' },
  containerLight: { backgroundColor: '#ffffff' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center' },
  title: { fontSize: 18, fontWeight: '600', marginLeft: 8 },
  titleDark: { color: '#ffffff' },
  titleLight: { color: '#111827' },
  closeBtn: { padding: 4 },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
    marginVertical: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
  },
  searchContainerDark: { backgroundColor: '#262626', borderColor: '#404040' },
  searchContainerLight: { backgroundColor: '#f9fafb', borderColor: '#d1d5db' },
  searchInput: { flex: 1, fontSize: 14, marginLeft: 8 },
  searchInputDark: { color: '#ffffff' },
  searchInputLight: { color: '#111827' },
  center: { padding: 32, alignItems: 'center' },
  emptyText: { fontSize: 14 },
  emptyTextDark: { color: '#9ca3af' },
  emptyTextLight: { color: '#6b7280' },
  list: { paddingHorizontal: 16 },
  item: {
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
  },
  itemDark: { backgroundColor: '#262626', borderColor: '#404040' },
  itemLight: { backgroundColor: '#f9fafb', borderColor: '#e5e7eb' },
  itemName: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  itemNameDark: { color: '#ffffff' },
  itemNameLight: { color: '#111827' },
  itemMeta: { fontSize: 12 },
  itemMetaDark: { color: '#9ca3af' },
  itemMetaLight: { color: '#6b7280' },
});
