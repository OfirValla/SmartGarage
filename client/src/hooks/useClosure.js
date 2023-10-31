import { useRef, useEffect } from 'react';

export function useClosure({
    child,
    parent,
    parentArgs,
    clearParent,
}) {
    const childRef = useRef();
    const parentArgsRef = useRef();

    useEffect(() => {
        childRef.current = child;
    }, [child]);

    useEffect(() => {
        parentArgsRef.current = parentArgs;
    }, [parentArgs]);

    useEffect(() => {
        const run = (() => {
            childRef.current();
        });

        const parentId = parentArgsRef.current
            ? parent(run, ...parentArgsRef.current)
            : parent(run);

        return () => clearParent?.(parentId);
    }, [parent, clearParent]);
};