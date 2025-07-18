import Loader from './components/Loader';
import Authed from './components/Authed';
import Login from './components/Login';
import Error from './components/Error';

import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from './firebase';

import './App.css';

const ComponentSelector = {
    'loading': Loader,
    'authed': Authed,
    'not-authed': Login,
    'error': Error
}

function App() {
    const [user, loading, error] = useAuthState(auth);

    let state = 'loading';
    if (user) state = 'authed';
    if (!user && !loading) state = 'not-authed';
    if (error) state = 'error';

    console.debug({ user, loading, state });
    const Component = ComponentSelector[state];
    return (
        <div className="App grid-center">
            <Component />
        </div>
    );
}

export default App;
