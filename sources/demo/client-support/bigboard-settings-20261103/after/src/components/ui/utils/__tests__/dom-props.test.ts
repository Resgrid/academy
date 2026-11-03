import { toDomProps } from '../dom-props';
describe('Native text properties on the browser DOM', () => {
  it('flattens style arrays, removes native-only attributes and preserves accessibility', () => {
    const press = jest.fn();
    const props = toDomProps({
      numberOfLines: 2,
      onLayout: jest.fn(),
      onPress: press,
      testID: 'label',
      accessibilityLabel: 'Status',
      accessibilityState: { disabled: true },
      style: [{ fontSize: 14 }, { fontSize: 18, color: 'red' }],
    });
    expect(props).toEqual(expect.objectContaining({ 'data-testid': 'label', 'aria-label': 'Status', 'aria-disabled': true, style: { fontSize: 18, color: 'red' }, onClick: press }));
    expect(props).not.toHaveProperty('numberOfLines');
    expect(props).not.toHaveProperty('onLayout');
    expect(props).not.toHaveProperty('onPress');
  });
  it('keeps a native press keyboard-accessible while preserving explicit browser handlers', () => {
    const props = toDomProps({ onPress: jest.fn() });
    const click = jest.fn();
    const preventDefault = jest.fn();
    (props.onKeyDown as (event: unknown) => void)({ key: 'Enter', preventDefault, currentTarget: { click } });
    (props.onKeyDown as (event: unknown) => void)({ key: ' ', preventDefault, currentTarget: { click } });
    (props.onKeyDown as (event: unknown) => void)({ key: 'Escape', preventDefault, currentTarget: { click } });
    expect(click).toHaveBeenCalledTimes(2);
    expect(preventDefault).toHaveBeenCalledTimes(2);
    const explicit = jest.fn();
    expect(toDomProps({ onPress: jest.fn(), onClick: explicit }).onClick).toBe(explicit);
  });
});
