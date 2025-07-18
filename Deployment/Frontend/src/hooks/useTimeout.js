import { useClosure } from './useClosure';

export function useTimeout(
    callback,
    msDelay,
    ...callbackArgs
) {
    return useClosure({
        child: callback,
        parent: setTimeout,
        parentArgs: [msDelay, ...callbackArgs],
        clearParent: clearTimeout,
    });
}