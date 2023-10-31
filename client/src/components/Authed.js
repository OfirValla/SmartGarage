import { useState } from 'react';

import { useAuthState } from "react-firebase-hooks/auth";
import { useObject } from 'react-firebase-hooks/database';

import { ref, set } from "firebase/database";
import { v4 as uuidv4 } from 'uuid';

import { auth, db } from '../firebase';
import { useInterval } from '../hooks/useInterval';

import './Authed.css';
import Loader from './Loader';

const statusToButtonText = {
    'Open': 'CLOSE',
    'Opening': 'CLOSE',
    'Closed': 'OPEN',
    'Closing': 'OPEN'
};


const Authed = () => {
    const [isProgramOnline, setIsProgramOnline] = useState(false);
    const [user,] = useAuthState(auth);

    const [snapshot, loading, error] = useObject(ref(db, 'gate-controller/status/current_status'));
    const [isOnlineSnapshot, ] = useObject(ref(db, 'gate-controller/program-status'));

    // Listen to gate status using firebase
    useInterval(() => {
        if (!isOnlineSnapshot) return; // Dont check if the value is null/undefined

        const currentDate = new Date();
        const programDate = Date.parse(isOnlineSnapshot.val());

        console.debug(currentDate.getTime(), programDate, Math.abs((currentDate.getTime() - programDate) / 1000));
        setIsProgramOnline(Math.abs((currentDate.getTime() - programDate) / 1000) < 5);
    }, 100);

    // Send open|close request to control the gate
    const onClick = () => {
        set(
            ref(db, `gate-controller/commands/${uuidv4()}`),
            {
                type: 'open|close',
                user: {
                    name: user.displayName,
                    email: user.email,
                    photo: user.photoURL,
                },
                data: {}
            }
        );
    };

    // While the information is loading render the loader
    if (loading)
        return <Loader/>

    // Available gate statuses: Open / Closed / Opening / Closing
    const gateStatus = snapshot.val();

    return (
        <div className="grid-center">
            <div className={`gate-button grid-center ${isProgramOnline ? 'program-online' : 'program-offline'}`} onClick={onClick}>
                <span>{statusToButtonText[gateStatus]} GATE</span>
            </div>
            <div className="gate-status grid-center">
                <span>Gate Status</span>
                <span>{isProgramOnline ? gateStatus : "Offline"}</span>
                <span className="error">{error}</span>
            </div>
        </div>
    );
};

export default Authed;