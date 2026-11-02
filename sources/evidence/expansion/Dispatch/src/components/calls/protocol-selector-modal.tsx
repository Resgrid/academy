import { CheckIcon, ChevronDownIcon, ChevronUpIcon, ClipboardListIcon, X } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityIndicator, Modal, ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';

import { Text } from '@/components/ui/text';
import { type CallProtocolsResultData, type ProtocolTriggerQuestionResultData } from '@/models/v4/callProtocols/callProtocolsResultData';
import { useProtocolsStore } from '@/stores/protocols/store';

export interface SelectedProtocol {
  protocolId: string;
  answers: Record<string, string>; // questionId -> answerId
}

interface ProtocolSelectorModalProps {
  isVisible: boolean;
  onClose: () => void;
  onConfirm: (selected: SelectedProtocol[]) => void;
  initialSelected?: SelectedProtocol[];
}

export const ProtocolSelectorModal: React.FC<ProtocolSelectorModalProps> = ({ isVisible, onClose, onConfirm, initialSelected = [] }) => {
  const { t } = useTranslation();
  const { colorScheme } = useColorScheme();
  const isDark = colorScheme === 'dark';

  const { protocols, fetchProtocols } = useProtocolsStore();
  const [isLoading, setIsLoading] = useState(false);
  const [selected, setSelected] = useState<SelectedProtocol[]>(initialSelected);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (isVisible) {
      setSelected(initialSelected);
      if (protocols.length === 0) {
        setIsLoading(true);
        fetchProtocols().finally(() => setIsLoading(false));
      }
    }
  }, [isVisible]); // eslint-disable-line react-hooks/exhaustive-deps

  const activeProtocols = protocols.filter((p) => !p.IsDisabled);

  function getStableId(protocol: CallProtocolsResultData, index: number): string {
    return protocol.Id || `protocol-index-${index}`;
  }

  function isProtocolSelected(id: string): boolean {
    return selected.some((s) => s.protocolId === id);
  }

  function getAnswerForQuestion(protocolId: string, questionId: string): string | undefined {
    return selected.find((s) => s.protocolId === protocolId)?.answers[questionId];
  }

  function toggleProtocol(stableId: string) {
    setSelected((prev) => {
      const exists = prev.findIndex((s) => s.protocolId === stableId);
      if (exists >= 0) {
        return prev.filter((s) => s.protocolId !== stableId);
      }
      return [...prev, { protocolId: stableId, answers: {} }];
    });
  }

  function selectAnswer(protocolId: string, question: ProtocolTriggerQuestionResultData, answerId: string) {
    setSelected((prev) =>
      prev.map((s) => {
        if (s.protocolId !== protocolId) return s;
        const newAnswers = { ...s.answers, [question.Id]: answerId };
        return { ...s, answers: newAnswers };
      })
    );
  }

  const handleConfirm = () => {
    onConfirm(selected);
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
              <ClipboardListIcon size={20} color={isDark ? '#e5e7eb' : '#111827'} />
              <Text style={StyleSheet.flatten([styles.title, isDark ? styles.titleDark : styles.titleLight])}>{t('calls.protocols.title', 'Protocols')}</Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn} accessibilityLabel={t('common.close')}>
              <X size={20} color={isDark ? '#9ca3af' : '#6b7280'} />
            </TouchableOpacity>
          </View>

          {/* Content */}
          {isLoading ? (
            <View style={styles.center}>
              <ActivityIndicator color="#2563eb" />
            </View>
          ) : activeProtocols.length === 0 ? (
            <View style={styles.center}>
              <Text style={StyleSheet.flatten([styles.emptyText, isDark ? styles.emptyTextDark : styles.emptyTextLight])}>{t('calls.protocols.none', 'No protocols available')}</Text>
            </View>
          ) : (
            <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
              {activeProtocols.map((protocol, index) => {
                const stableId = getStableId(protocol, index);
                const isChecked = isProtocolSelected(stableId);
                const isExpanded = expandedId === stableId;
                const hasQuestions = protocol.Questions && protocol.Questions.length > 0;

                return (
                  <View key={stableId} style={StyleSheet.flatten([styles.item, isDark ? styles.itemDark : styles.itemLight, isChecked ? styles.itemSelected : {}])}>
                    {/* Protocol row */}
                    <View style={styles.protocolRow}>
                      <TouchableOpacity
                        style={styles.protocolRowPressable}
                        onPress={() => toggleProtocol(stableId)}
                        accessibilityRole="checkbox"
                        accessibilityState={{ checked: isChecked }}
                        accessibilityLabel={protocol.Name}
                      >
                        <View style={StyleSheet.flatten([styles.checkbox, isChecked ? styles.checkboxChecked : isDark ? styles.checkboxDark : styles.checkboxLight])}>
                          {isChecked ? <CheckIcon size={12} color="#ffffff" /> : null}
                        </View>
                        <View style={styles.protocolInfo}>
                          <Text style={StyleSheet.flatten([styles.protocolName, isDark ? styles.protocolNameDark : styles.protocolNameLight])}>{protocol.Name}</Text>
                          {!!protocol.Code && <Text style={StyleSheet.flatten([styles.protocolCode, isDark ? styles.protocolCodeDark : styles.protocolCodeLight])}>{protocol.Code}</Text>}
                        </View>
                      </TouchableOpacity>
                      {hasQuestions && isChecked ? (
                        <TouchableOpacity
                          onPress={() => setExpandedId(isExpanded ? null : stableId)}
                          style={styles.expandBtn}
                          accessibilityLabel={isExpanded ? t('calls.protocols.collapse') : t('calls.protocols.expand_questions')}
                        >
                          {isExpanded ? <ChevronUpIcon size={16} color={isDark ? '#9ca3af' : '#6b7280'} /> : <ChevronDownIcon size={16} color={isDark ? '#9ca3af' : '#6b7280'} />}
                        </TouchableOpacity>
                      ) : null}
                    </View>

                    {/* Questions */}
                    {isChecked && isExpanded && hasQuestions ? (
                      <View style={StyleSheet.flatten([styles.questionsContainer, isDark ? styles.questionsContainerDark : styles.questionsContainerLight])}>
                        {protocol.Questions.map((question) => (
                          <View key={question.Id || question.Question} style={styles.question}>
                            <Text style={StyleSheet.flatten([styles.questionText, isDark ? styles.questionTextDark : styles.questionTextLight])}>{question.Question}</Text>
                            <View style={styles.answersRow}>
                              {question.Answers.map((answer) => {
                                const isAnswerSelected = getAnswerForQuestion(stableId, question.Id) === answer.Id;
                                return (
                                  <TouchableOpacity
                                    key={answer.Id || answer.Answer}
                                    style={StyleSheet.flatten([styles.answerBtn, isDark ? styles.answerBtnDark : styles.answerBtnLight, isAnswerSelected ? styles.answerBtnSelected : {}])}
                                    onPress={() => selectAnswer(stableId, question, answer.Id)}
                                    accessibilityRole="radio"
                                    accessibilityState={{ selected: isAnswerSelected }}
                                  >
                                    <Text style={StyleSheet.flatten([styles.answerText, isAnswerSelected ? styles.answerTextSelected : isDark ? styles.answerTextDark : styles.answerTextLight])}>{answer.Answer}</Text>
                                  </TouchableOpacity>
                                );
                              })}
                            </View>
                          </View>
                        ))}
                      </View>
                    ) : null}
                  </View>
                );
              })}
            </ScrollView>
          )}

          {/* Footer */}
          {!isLoading && activeProtocols.length > 0 ? (
            <View style={StyleSheet.flatten([styles.footer, isDark ? styles.footerDark : styles.footerLight])}>
              <Text style={StyleSheet.flatten([styles.selectedCount, isDark ? styles.selectedCountDark : styles.selectedCountLight])}>
                {selected.length} {t('calls.protocols.selected_count', 'selected')}
              </Text>
              <TouchableOpacity style={styles.confirmBtn} onPress={handleConfirm} accessibilityRole="button">
                <Text style={styles.confirmBtnText}>{t('common.confirm', 'Confirm')}</Text>
              </TouchableOpacity>
            </View>
          ) : null}
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
    maxHeight: '85%',
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
  center: { padding: 32, alignItems: 'center' },
  emptyText: { fontSize: 14 },
  emptyTextDark: { color: '#9ca3af' },
  emptyTextLight: { color: '#6b7280' },
  list: { paddingHorizontal: 16, paddingTop: 8 },
  item: {
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    overflow: 'hidden',
  },
  itemDark: { backgroundColor: '#262626', borderColor: '#404040' },
  itemLight: { backgroundColor: '#f9fafb', borderColor: '#e5e7eb' },
  itemSelected: { borderColor: '#2563eb' },
  protocolRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  protocolRowPressable: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxChecked: { backgroundColor: '#2563eb', borderColor: '#2563eb' },
  checkboxDark: { borderColor: '#6b7280' },
  checkboxLight: { borderColor: '#d1d5db' },
  protocolInfo: { flex: 1 },
  protocolName: { fontSize: 14, fontWeight: '600' },
  protocolNameDark: { color: '#ffffff' },
  protocolNameLight: { color: '#111827' },
  protocolCode: { fontSize: 11, marginTop: 2 },
  protocolCodeDark: { color: '#9ca3af' },
  protocolCodeLight: { color: '#6b7280' },
  expandBtn: { padding: 12 },
  questionsContainer: {
    paddingHorizontal: 16,
    paddingBottom: 12,
    borderTopWidth: 1,
  },
  questionsContainerDark: { borderTopColor: '#404040' },
  questionsContainerLight: { borderTopColor: '#e5e7eb' },
  question: { marginTop: 10 },
  questionText: { fontSize: 13, fontWeight: '500', marginBottom: 6 },
  questionTextDark: { color: '#d1d5db' },
  questionTextLight: { color: '#374151' },
  answersRow: { flexDirection: 'row', flexWrap: 'wrap' },
  answerBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 16,
    borderWidth: 1,
    marginRight: 6,
    marginBottom: 6,
  },
  answerBtnDark: { borderColor: '#6b7280', backgroundColor: '#404040' },
  answerBtnLight: { borderColor: '#d1d5db', backgroundColor: '#ffffff' },
  answerBtnSelected: { borderColor: '#2563eb', backgroundColor: '#dbeafe' },
  answerText: { fontSize: 12 },
  answerTextDark: { color: '#d1d5db' },
  answerTextLight: { color: '#374151' },
  answerTextSelected: { color: '#1d4ed8', fontWeight: '600' },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
  },
  footerDark: { borderTopColor: '#262626' },
  footerLight: { borderTopColor: '#e5e7eb' },
  selectedCount: { fontSize: 13 },
  selectedCountDark: { color: '#9ca3af' },
  selectedCountLight: { color: '#6b7280' },
  confirmBtn: {
    backgroundColor: '#2563eb',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  confirmBtnText: { color: '#ffffff', fontWeight: '600', fontSize: 14 },
});
