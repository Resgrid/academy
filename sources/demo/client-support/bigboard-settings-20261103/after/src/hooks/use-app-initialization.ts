import { type MutableRefObject, useEffect } from 'react';

export const useCommittedInitialization = (signedIn: boolean, initialized: boolean, inFlight: MutableRefObject<boolean>, initialize: () => Promise<void>): void => {
  useEffect(() => {
    if (signedIn && !initialized && !inFlight.current) void initialize();
  }, [signedIn, initialized, inFlight, initialize]);
};
