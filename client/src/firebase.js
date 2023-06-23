import { initializeApp } from "firebase/app";
import {
    GoogleAuthProvider,
    getAuth,
    signInWithPopup
} from "firebase/auth";
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
    apiKey: "AIzaSyB9U08NNpbmW3imdi76RsAPjMqTyp3qVZU",
    authDomain: "valla-projects.firebaseapp.com",
    databaseURL: "https://valla-projects-default-rtdb.firebaseio.com",
    projectId: "valla-projects",
    storageBucket: "valla-projects.appspot.com",
    messagingSenderId: "689423699997",
    appId: "1:689423699997:web:d8ea0ad38c70a9ce6636f4"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: 'select_account' });
export const signInWithGoogle = () => signInWithPopup(auth, provider);

export default app;