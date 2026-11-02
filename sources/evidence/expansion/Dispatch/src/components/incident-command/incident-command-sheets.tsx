import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CustomBottomSheet } from '@/components/ui/bottom-sheet';
import { Button, ButtonText } from '@/components/ui/button';
import { FormControl, FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';
import { HStack } from '@/components/ui/hstack';
import { Input, InputField } from '@/components/ui/input';
import { Select, SelectBackdrop, SelectContent, SelectIcon, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select';
import { Text } from '@/components/ui/text';
import { Textarea, TextareaInput } from '@/components/ui/textarea';
import { VStack } from '@/components/ui/vstack';
import { CommandNodeType, ResourceAssignmentKind, TacticalObjectiveType } from '@/models/v4/incidentCommand/incidentCommandEnums';
import { useIncidentCommandStore } from '@/stores/incident-command/store';
import { usePersonnelStore } from '@/stores/personnel/store';
import { useToastStore } from '@/stores/toast/store';
import { useUnitsStore } from '@/stores/units/store';

import { NODE_TYPE_OPTIONS, nodeTypeLabel, OBJECTIVE_TYPE_OPTIONS, ROLE_TYPE_OPTIONS } from './ic-labels';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
}

/** Shared footer with cancel + submit buttons. */
const SheetActions: React.FC<{ onCancel: () => void; onSubmit: () => void; submitLabel: string; isBusy: boolean; disabled?: boolean }> = ({ onCancel, onSubmit, submitLabel, isBusy, disabled }) => {
  const { t } = useTranslation();
  return (
    <HStack className="space-x-3 pt-6">
      <Button variant="outline" className="mr-2 flex-1" onPress={onCancel} disabled={isBusy}>
        <ButtonText>{t('common.cancel')}</ButtonText>
      </Button>
      <Button className="ml-2 flex-1" onPress={onSubmit} disabled={isBusy || disabled}>
        <ButtonText>{submitLabel}</ButtonText>
      </Button>
    </HStack>
  );
};

// --- Establish command ------------------------------------------------------

export const EstablishCommandSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { establish, fetchTemplates, templates, isMutating } = useIncidentCommandStore();
  const [templateId, setTemplateId] = useState('');

  useEffect(() => {
    if (isOpen) fetchTemplates();
  }, [isOpen, fetchTemplates]);

  const handleSubmit = async () => {
    try {
      await establish(templateId ? parseInt(templateId, 10) : null);
      showToast('success', t('incident_command.establish_success'));
      onClose();
    } catch {
      showToast('error', t('incident_command.establish_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.establish_title')}</Text>
        <Text className="text-center text-sm text-gray-500">{t('incident_command.establish_description')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.template')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={templateId} onValueChange={setTemplateId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.no_template')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                <SelectItem label={t('incident_command.no_template')} value="" />
                {templates.map((template) => (
                  <SelectItem key={template.CommandDefinitionId} label={template.Name} value={String(template.CommandDefinitionId)} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.establish')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Action plan ------------------------------------------------------------

export const ActionPlanSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { updateActionPlan, isMutating, board } = useIncidentCommandStore();
  const [plan, setPlan] = useState('');

  useEffect(() => {
    if (isOpen) setPlan(board?.Command?.IncidentActionPlan ?? '');
  }, [isOpen, board?.Command?.IncidentActionPlan]);

  const handleSubmit = async () => {
    try {
      await updateActionPlan(plan);
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.edit_action_plan')}</Text>
        <FormControl>
          <Textarea>
            <TextareaInput placeholder={t('incident_command.action_plan_placeholder')} value={plan} onChangeText={setPlan} numberOfLines={6} />
          </Textarea>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.save')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Add objective ----------------------------------------------------------

export const AddObjectiveSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { saveObjective, isMutating } = useIncidentCommandStore();
  const [name, setName] = useState('');
  const [type, setType] = useState(String(TacticalObjectiveType.General));

  useEffect(() => {
    if (isOpen) {
      setName('');
      setType(String(TacticalObjectiveType.General));
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!name.trim()) {
      showToast('error', t('incident_command.name_required'));
      return;
    }
    try {
      await saveObjective({ Name: name.trim(), ObjectiveType: parseInt(type, 10) });
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.add_objective')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.objective_name')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={name} onChangeText={setName} placeholder={t('incident_command.objective_name')} />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.objective_type')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={type} onValueChange={setType}>
            <SelectTrigger>
              <SelectInput />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {OBJECTIVE_TYPE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} label={option.label} value={String(option.value)} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.add')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Add lane ---------------------------------------------------------------

export const AddLaneSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { saveNode, isMutating } = useIncidentCommandStore();
  const [name, setName] = useState('');
  const [nodeType, setNodeType] = useState(String(CommandNodeType.Division));

  useEffect(() => {
    if (isOpen) {
      setName('');
      setNodeType(String(CommandNodeType.Division));
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!name.trim()) {
      showToast('error', t('incident_command.name_required'));
      return;
    }
    try {
      await saveNode({ Name: name.trim(), NodeType: parseInt(nodeType, 10) });
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.add_lane')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.lane_name')}</FormControlLabelText>
          </FormControlLabel>
          <Input>
            <InputField value={name} onChangeText={setName} placeholder={t('incident_command.lane_name')} />
          </Input>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.lane_type')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={nodeType} onValueChange={setNodeType}>
            <SelectTrigger>
              <SelectInput />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {NODE_TYPE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} label={option.label} value={String(option.value)} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.add')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Assign resource --------------------------------------------------------

export const AssignResourceSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { assignResource, isMutating, board } = useIncidentCommandStore();
  const units = useUnitsStore((s) => s.units);
  const personnel = usePersonnelStore((s) => s.personnel);
  const [nodeId, setNodeId] = useState('');
  const [resourceKind, setResourceKind] = useState(String(ResourceAssignmentKind.RealUnit));
  const [resourceId, setResourceId] = useState('');

  useEffect(() => {
    if (isOpen) {
      useUnitsStore.getState().fetchUnits();
      usePersonnelStore.getState().fetchPersonnel();
      setNodeId('');
      setResourceId('');
      setResourceKind(String(ResourceAssignmentKind.RealUnit));
    }
  }, [isOpen]);

  const lanes = useMemo(() => (board?.Nodes ?? []).filter((node) => !node.DeletedOn), [board?.Nodes]);
  const isUnit = parseInt(resourceKind, 10) === ResourceAssignmentKind.RealUnit;

  const handleSubmit = async () => {
    if (!nodeId || !resourceId) {
      showToast('error', t('incident_command.assign_resource_required'));
      return;
    }
    try {
      await assignResource(nodeId, parseInt(resourceKind, 10), resourceId);
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.assign_resource')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.lane')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={nodeId} onValueChange={setNodeId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_lane')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {lanes.map((lane) => (
                  <SelectItem key={lane.CommandStructureNodeId} label={`${lane.Name} (${nodeTypeLabel(lane.NodeType)})`} value={lane.CommandStructureNodeId} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.resource_type')}</FormControlLabelText>
          </FormControlLabel>
          <Select
            selectedValue={resourceKind}
            onValueChange={(value) => {
              setResourceKind(value);
              setResourceId('');
            }}
          >
            <SelectTrigger>
              <SelectInput />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                <SelectItem label={t('incident_command.unit')} value={String(ResourceAssignmentKind.RealUnit)} />
                <SelectItem label={t('incident_command.personnel')} value={String(ResourceAssignmentKind.RealPersonnel)} />
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.resource')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={resourceId} onValueChange={setResourceId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_resource')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {isUnit
                  ? units.map((unit) => <SelectItem key={unit.UnitId} label={unit.Name} value={unit.UnitId} />)
                  : personnel.map((person) => <SelectItem key={person.UserId} label={`${person.FirstName} ${person.LastName}`.trim()} value={person.UserId} />)}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.assign')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Assign role ------------------------------------------------------------

export const AssignRoleSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { assignRole, isMutating } = useIncidentCommandStore();
  const personnel = usePersonnelStore((s) => s.personnel);
  const [userId, setUserId] = useState('');
  const [roleType, setRoleType] = useState('');

  useEffect(() => {
    if (isOpen) {
      usePersonnelStore.getState().fetchPersonnel();
      setUserId('');
      setRoleType('');
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!userId || !roleType) {
      showToast('error', t('incident_command.assign_role_required'));
      return;
    }
    try {
      await assignRole(userId, parseInt(roleType, 10));
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.assign_role')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.person')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={userId} onValueChange={setUserId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_person')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {personnel.map((person) => (
                  <SelectItem key={person.UserId} label={`${person.FirstName} ${person.LastName}`.trim()} value={person.UserId} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.role')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={roleType} onValueChange={setRoleType}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_role')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {ROLE_TYPE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} label={option.label} value={String(option.value)} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.assign')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Transfer command -------------------------------------------------------

export const TransferCommandSheet: React.FC<SheetProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const { transfer, isMutating } = useIncidentCommandStore();
  const personnel = usePersonnelStore((s) => s.personnel);
  const [userId, setUserId] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (isOpen) {
      usePersonnelStore.getState().fetchPersonnel();
      setUserId('');
      setNotes('');
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!userId) {
      showToast('error', t('incident_command.select_person'));
      return;
    }
    try {
      await transfer(userId, notes);
      showToast('success', t('incident_command.transfer_success'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={isOpen} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.transfer_title')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.person')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={userId} onValueChange={setUserId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_person')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {personnel.map((person) => (
                  <SelectItem key={person.UserId} label={`${person.FirstName} ${person.LastName}`.trim()} value={person.UserId} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.transfer_notes')}</FormControlLabelText>
          </FormControlLabel>
          <Textarea>
            <TextareaInput value={notes} onChangeText={setNotes} numberOfLines={3} />
          </Textarea>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.transfer')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Move lane (reparent) ---------------------------------------------------

export const MoveNodeSheet: React.FC<{ nodeId: string | null; onClose: () => void }> = ({ nodeId, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const board = useIncidentCommandStore((s) => s.board);
  const isMutating = useIncidentCommandStore((s) => s.isMutating);
  const [parentId, setParentId] = useState('');

  useEffect(() => {
    if (nodeId) setParentId('');
  }, [nodeId]);

  const lanes = useMemo(() => {
    const nodes = (board?.Nodes ?? []).filter((n) => !n.DeletedOn);
    if (!nodeId) return nodes;
    // Exclude the node itself and its descendants — moving under them would create a cycle.
    const blocked = new Set<string>([nodeId]);
    const stack = [nodeId];
    while (stack.length > 0) {
      const currentId = stack.pop() as string;
      for (const n of nodes) {
        if ((n.ParentNodeId || '') === currentId && !blocked.has(n.CommandStructureNodeId)) {
          blocked.add(n.CommandStructureNodeId);
          stack.push(n.CommandStructureNodeId);
        }
      }
    }
    return nodes.filter((n) => !blocked.has(n.CommandStructureNodeId));
  }, [board?.Nodes, nodeId]);

  const handleSubmit = async () => {
    if (!nodeId) return;
    try {
      await useIncidentCommandStore.getState().moveNode(nodeId, parentId);
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={!!nodeId} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.move_lane')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.parent_lane')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={parentId} onValueChange={setParentId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.top_level')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                <SelectItem label={t('incident_command.top_level')} value="" />
                {lanes.map((lane) => (
                  <SelectItem key={lane.CommandStructureNodeId} label={`${lane.Name} (${nodeTypeLabel(lane.NodeType)})`} value={lane.CommandStructureNodeId} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.move')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};

// --- Move resource (between lanes) ------------------------------------------

export const MoveResourceSheet: React.FC<{ assignmentId: string | null; onClose: () => void }> = ({ assignmentId, onClose }) => {
  const { t } = useTranslation();
  const showToast = useToastStore((s) => s.showToast);
  const board = useIncidentCommandStore((s) => s.board);
  const isMutating = useIncidentCommandStore((s) => s.isMutating);
  const [targetNodeId, setTargetNodeId] = useState('');

  useEffect(() => {
    if (assignmentId) setTargetNodeId('');
  }, [assignmentId]);

  const lanes = useMemo(() => (board?.Nodes ?? []).filter((n) => !n.DeletedOn), [board?.Nodes]);

  const handleSubmit = async () => {
    if (!assignmentId || !targetNodeId) {
      showToast('error', t('incident_command.select_lane'));
      return;
    }
    try {
      await useIncidentCommandStore.getState().moveResource(assignmentId, targetNodeId);
      showToast('success', t('incident_command.saved'));
      onClose();
    } catch {
      showToast('error', t('incident_command.save_error'));
    }
  };

  return (
    <CustomBottomSheet isOpen={!!assignmentId} onClose={onClose} isLoading={isMutating}>
      <VStack className="w-full flex-1 space-y-4 p-4">
        <Text className="text-center text-lg font-semibold">{t('incident_command.move_resource')}</Text>
        <FormControl>
          <FormControlLabel>
            <FormControlLabelText>{t('incident_command.lane')}</FormControlLabelText>
          </FormControlLabel>
          <Select selectedValue={targetNodeId} onValueChange={setTargetNodeId}>
            <SelectTrigger>
              <SelectInput placeholder={t('incident_command.select_lane')} />
              <SelectIcon />
            </SelectTrigger>
            <SelectPortal>
              <SelectBackdrop />
              <SelectContent>
                {lanes.map((lane) => (
                  <SelectItem key={lane.CommandStructureNodeId} label={`${lane.Name} (${nodeTypeLabel(lane.NodeType)})`} value={lane.CommandStructureNodeId} />
                ))}
              </SelectContent>
            </SelectPortal>
          </Select>
        </FormControl>
        <SheetActions onCancel={onClose} onSubmit={handleSubmit} submitLabel={t('incident_command.move')} isBusy={isMutating} />
      </VStack>
    </CustomBottomSheet>
  );
};
