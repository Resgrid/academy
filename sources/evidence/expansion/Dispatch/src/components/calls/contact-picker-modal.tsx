import { SearchIcon, UserIcon, X } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityIndicator, Modal, ScrollView, StyleSheet, TextInput, TouchableOpacity, View } from 'react-native';

import { Text } from '@/components/ui/text';
import { type ContactResultData } from '@/models/v4/contacts/contactResultData';
import { useContactsStore } from '@/stores/contacts/store';

interface ContactPickerModalProps {
  isVisible: boolean;
  onClose: () => void;
  onSelect: (contact: ContactResultData) => void;
}

export const ContactPickerModal: React.FC<ContactPickerModalProps> = ({ isVisible, onClose, onSelect }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';

  const { contacts, fetchContacts } = useContactsStore();
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isVisible && contacts.length === 0) {
      setIsLoading(true);
      fetchContacts().finally(() => setIsLoading(false));
    }
  }, [isVisible]); // eslint-disable-line react-hooks/exhaustive-deps

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return contacts;
    const q = searchQuery.toLowerCase();
    return contacts.filter((c) => {
      const displayName = getDisplayName(c).toLowerCase();
      const email = (c.Email ?? '').toLowerCase();
      const phone = String(c.Phone ?? '').toLowerCase();
      return displayName.includes(q) || email.includes(q) || phone.includes(q);
    });
  }, [contacts, searchQuery]);

  function getDisplayName(c: ContactResultData): string {
    if (c.CompanyName) return c.CompanyName;
    const parts = [c.FirstName, c.MiddleName, c.LastName].filter(Boolean);
    if (parts.length > 0) return parts.join(' ');
    return c.Name ?? c.OtherName ?? '';
  }

  function getContactInfo(c: ContactResultData): string {
    if (c.Email) return c.Email;
    if (c.Phone) return String(c.Phone);
    if (c.Mobile) return String(c.Mobile);
    return '';
  }

  const handleSelect = (contact: ContactResultData) => {
    onSelect(contact);
    onClose();
  };

  if (!isVisible) return null;

  return (
    <Modal visible={isVisible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={StyleSheet.flatten([styles.container, isDark ? styles.containerDark : styles.containerLight])}>
          {/* Header */}
          <View style={StyleSheet.flatten([styles.header, isDark ? styles.headerDark : styles.headerLight])}>
            <View style={styles.headerLeft}>
              <UserIcon size={20} color={isDark ? '#e5e7eb' : '#111827'} />
              <Text style={StyleSheet.flatten([styles.title, isDark ? styles.titleDark : styles.titleLight])}>{t('calls.contact_picker.title', 'Select Contact')}</Text>
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
              placeholder={t('calls.contact_picker.search_placeholder', 'Search contacts...')}
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
              <Text style={StyleSheet.flatten([styles.emptyText, isDark ? styles.emptyTextDark : styles.emptyTextLight])}>{t('calls.contact_picker.none', 'No contacts available')}</Text>
            </View>
          ) : (
            <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
              {filtered.map((contact) => {
                const displayName = getDisplayName(contact);
                const info = getContactInfo(contact);
                return (
                  <TouchableOpacity
                    key={contact.ContactId}
                    style={StyleSheet.flatten([styles.item, isDark ? styles.itemDark : styles.itemLight])}
                    onPress={() => handleSelect(contact)}
                    accessibilityRole="button"
                    accessibilityLabel={displayName}
                  >
                    <View style={styles.avatar}>
                      <Text style={styles.avatarText}>{displayName.charAt(0).toUpperCase()}</Text>
                    </View>
                    <View style={styles.itemContent}>
                      <Text style={StyleSheet.flatten([styles.itemName, isDark ? styles.itemNameDark : styles.itemNameLight])}>{displayName}</Text>
                      {!!info && <Text style={StyleSheet.flatten([styles.itemInfo, isDark ? styles.itemInfoDark : styles.itemInfoLight])}>{info}</Text>}
                    </View>
                  </TouchableOpacity>
                );
              })}
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
  },
  headerDark: { borderBottomColor: '#262626' },
  headerLight: { borderBottomColor: '#e5e7eb' },
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
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
  },
  itemDark: { backgroundColor: '#262626', borderColor: '#404040' },
  itemLight: { backgroundColor: '#f9fafb', borderColor: '#e5e7eb' },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2563eb',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  avatarText: { color: '#ffffff', fontWeight: '700', fontSize: 16 },
  itemContent: { flex: 1 },
  itemName: { fontSize: 15, fontWeight: '600' },
  itemNameDark: { color: '#ffffff' },
  itemNameLight: { color: '#111827' },
  itemInfo: { fontSize: 12, marginTop: 2 },
  itemInfoDark: { color: '#9ca3af' },
  itemInfoLight: { color: '#6b7280' },
});
