import { useClosure } from './useClosure';

export function useInterval(
    callback,
    msDelay,
    ...callbackArgs
) {
    return useClosure({
        child: callback,
        parent: setInterval,
        parentArgs: [msDelay, ...callbackArgs],
        clearParent: clearInterval,
    });
}
