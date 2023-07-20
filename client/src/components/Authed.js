import { useAuthState } from "react-firebase-hooks/auth";
import { useObject } from 'react-firebase-hooks/database';

import { ref, set } from "firebase/database";
import { v4 as uuidv4 } from 'uuid';

import { auth, db } from '../firebase';

import './Authed.css';

const Authed = () => {
    const [user, ,] = useAuthState(auth);

    const [snapshot, loading, error] = useObject(ref(db, 'gate-controller/status/current_status'));
    
    console.debug(user.displayName, user.email, user.photoURL);
    // Listen to gate status using firebase

    const onClick = () => {

        // Add status class

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

    return (
        <div className="grid-center">
            <div className="gate-button grid-center" onClick={onClick}>
                <span>OPEN GATE</span>
            </div>
            <div className="gate-status grid-center">
                <span>Gate Status</span>
                <span>{snapshot.val()}</span>
            </div>
        </div>
    );
};

export default Authed;