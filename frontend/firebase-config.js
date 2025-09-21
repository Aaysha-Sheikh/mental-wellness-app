const firebaseConfig = {
  apiKey: "AIzaSyCgui2NNBgL-lgBNmfOkzlmq9AprHSMNr0",
  authDomain: "me-well-61f74.firebaseapp.com",
  projectId: "me-well-61f74",
  storageBucket: "me-well-61f74.firebasestorage.app",
  messagingSenderId: "209468975899",
  appId: "1:209468975899:web:b8919c9ec65b0c1974c1be"
};

// Initialize Firebase (compat mode)
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
window.auth = auth;
