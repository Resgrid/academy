import { type StyleProp, StyleSheet, type TextStyle } from 'react-native';

// Browser Text receives React Native props from shared app components.
const nativeOnlyProps = new Set([
  'testID',
  'onPress',
  'onLongPress',
  'numberOfLines',
  'ellipsizeMode',
  'adjustsFontSizeToFit',
  'allowFontScaling',
  'maxFontSizeMultiplier',
  'minimumFontScale',
  'suppressHighlighting',
  'selectable',
  'selectionColor',
  'textBreakStrategy',
  'lineBreakStrategyIOS',
  'dataDetectorType',
  'onTextLayout',
  'onLayout',
  'nativeID',
  'hitSlop',
  'collapsable',
  'needsOffscreenAlphaCompositing',
  'accessible',
  'accessibilityRole',
  'accessibilityLabel',
  'accessibilityHint',
  'accessibilityState',
  'accessibilityValue',
  'accessibilityActions',
  'onAccessibilityAction',
  'importantForAccessibility',
  'accessibilityLiveRegion',
  'accessibilityElementsHidden',
  'onStartShouldSetResponder',
  'onMoveShouldSetResponder',
  'onResponderGrant',
  'onResponderMove',
  'onResponderRelease',
  'onResponderTerminate',
  'onResponderTerminationRequest',
]);

const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);

/** Flatten native styles and preserve equivalent DOM actions and accessibility. */
export function toDomProps<T extends object>(props: T): Record<string, unknown> {
  const native = props as Record<string, unknown>;
  const dom: Record<string, unknown> = {};
  for (const [name, value] of Object.entries(native)) {
    if (!nativeOnlyProps.has(name)) {
      dom[name] = name === 'style' ? StyleSheet.flatten(value as StyleProp<TextStyle>) : value;
    }
  }

  const setDefault = (name: string, value: unknown) => {
    if (value !== undefined && dom[name] === undefined) dom[name] = value;
  };
  setDefault('data-testid', native.testID);
  setDefault('id', native.nativeID);
  setDefault('aria-label', native.accessibilityLabel);
  setDefault('aria-description', native.accessibilityHint);
  const role = native.accessibilityRole;
  if (typeof role === 'string' && role !== 'text') {
    const roleAliases: Record<string, string> = {
      header: 'heading',
      image: 'img',
      imagebutton: 'button',
      keyboardkey: 'button',
      none: 'presentation',
      adjustable: 'slider',
      summary: 'region',
    };
    setDefault('role', roleAliases[role] ?? role);
  }
  if (isRecord(native.accessibilityState)) {
    for (const state of ['disabled', 'selected', 'checked', 'busy', 'expanded']) {
      setDefault(`aria-${state}`, native.accessibilityState[state]);
    }
  }
  if (isRecord(native.accessibilityValue)) {
    for (const value of ['min', 'max', 'now', 'text']) {
      setDefault(`aria-value${value}`, native.accessibilityValue[value]);
    }
  }
  if (native.accessibilityLiveRegion !== undefined) {
    setDefault('aria-live', native.accessibilityLiveRegion === 'none' ? 'off' : native.accessibilityLiveRegion);
  }
  if (native.accessibilityElementsHidden === true || native.importantForAccessibility === 'no-hide-descendants') {
    setDefault('aria-hidden', true);
  }

  if (typeof native.onPress === 'function' && dom.onClick === undefined) {
    dom.onClick = native.onPress;
    setDefault('role', 'button');
    setDefault('tabIndex', 0);
    setDefault('onKeyDown', (event: { key: string; preventDefault: () => void; currentTarget: { click: () => void } }) => {
      if (event.key === 'Enter' || (event.key === ' ' && dom.role !== 'link')) {
        event.preventDefault();
        event.currentTarget.click();
      }
    });
  }
  return dom;
}
