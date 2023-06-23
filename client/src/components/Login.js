import { useEffect } from 'react';
import { signInWithGoogle } from '../firebase';

import { ReactComponent as GoogleLogo } from './Google.svg';

import './Login.css';

const Login = () => {

    // On login immideatly request login
    useEffect(() => {
        signInWithGoogle();
    }, []);

    return (
        <div className="login">
            <div
                label="Sign in with Google"
                style={{ backgroundColor: 'rgb(66, 133, 244)', color: 'rgb(255, 255, 255)', height: '50px', width: '240px', border: 'none', textAlign: 'center', boxShadow: 'rgba(0, 0, 0, 0.25) 0px 2px 4px 0px', fontSize: '16px', lineHeight: '48px', display: 'block', borderRadius: '1px', transition: 'background-color 0.218s ease 0s, border-color 0.218s ease 0s, box-shadow 0.218s ease 0s', fontFamily: 'Roboto, arial, sans-serif', cursor: 'pointer' }}
                onClick={signInWithGoogle}
            >
                <div style={{ width: '48px', height: '48px', textAlign: 'center', display: 'block', marginTop: '1px', marginLeft: '1px', float: 'left', backgroundColor: 'rgb(255, 255, 255)', borderRadius: '1px', whiteSpace: 'nowrap' }} >
                    <GoogleLogo />
                </div>
                <span>Sign in with Google</span>
            </div>
        </div>
    );
};

export default Login;