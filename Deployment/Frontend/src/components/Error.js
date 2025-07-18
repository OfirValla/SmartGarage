import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from '../firebase';

const Error = () => {
    const [,, error] = useAuthState(auth);
    return (
        <div>{ error }</div>
    )
};

export default Error;