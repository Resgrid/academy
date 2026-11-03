import { renderHook } from '@testing-library/react-native';

import { useCommittedInitialization } from '../use-app-initialization';

describe('Committed app initialization', () => {
  it('starts signed-in initialization after commit, once while pending', () => {
    const inFlight = { current: false };
    let rendering = false;
    const initialize = jest.fn(async () => {
      expect(rendering).toBe(false);
      inFlight.current = true;
    });
    const view = renderHook(
      ({ initialized }) => {
        rendering = true;
        useCommittedInitialization(true, initialized, inFlight, initialize);
        rendering = false;
      },
      { initialProps: { initialized: false } }
    );
    expect(initialize).toHaveBeenCalledTimes(1);
    view.rerender({ initialized: false });
    expect(initialize).toHaveBeenCalledTimes(1);
    view.rerender({ initialized: true });
    expect(initialize).toHaveBeenCalledTimes(1);
    view.unmount();
  });
  it('waits until authentication is hydrated and signed in', () => {
    const initialize = jest.fn(async () => {});
    const inFlight = { current: false };
    const view = renderHook(({ signedIn }) => useCommittedInitialization(signedIn, false, inFlight, initialize), { initialProps: { signedIn: false } });
    expect(initialize).not.toHaveBeenCalled();
    view.rerender({ signedIn: true });
    expect(initialize).toHaveBeenCalledTimes(1);
    view.unmount();
  });
});
