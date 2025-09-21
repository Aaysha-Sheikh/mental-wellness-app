
// Firebase setup
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCgui2NNBgL-lgBNmfOkzlmq9AprHSMNr0",
  authDomain: "me-well-61f74.firebaseapp.com",
  projectId: "me-well-61f74",
  storageBucket: "me-well-61f74.firebasestorage.app",
  messagingSenderId: "209468975899",
  appId: "1:209468975899:web:b8919c9ec65b0c1974c1be"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Toggle login/signup forms
window.toggleForms = function () {
  document.getElementById("login-box").classList.toggle("hidden");
  document.getElementById("signup-box").classList.toggle("hidden");
};

// Login
window.login = function () {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  signInWithEmailAndPassword(auth, email, password)
    .then(userCred => {
      localStorage.setItem("uid", userCred.user.uid); // important!
      window.location.href = "dashboard.html";       // redirects after login
    })
    .catch(err => alert(err.message));
};


// Signup
window.signup = function () {
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  createUserWithEmailAndPassword(auth, email, password)
    .then(userCred => {
      localStorage.setItem("uid", userCred.user.uid);
      alert("Signup successful!");
    })
    .catch(err => alert(err.message));
};

// Logout
window.logout = function () {
  signOut(auth).then(() => {
    localStorage.removeItem("uid");
    alert("Logged out!");
  });
};




// Connect YouTube

// Connect YouTube
window.connectYouTube = async function () {
  const uid = localStorage.getItem("uid");
  if (!uid) return alert("Not logged in");

  // Open OAuth in a new window
  const authWindow = window.open(
    `http://localhost:8000/authorize?uid=${uid}`,
    "_blank",
    "width=600,height=700"
  );

  // Poll until the OAuth window is closed
  const poll = setInterval(async () => {
    if (authWindow.closed) {
      clearInterval(poll);

      // Fetch analysis immediately after OAuth
      await getAnalysis();

      // Enable the story and image buttons
      document.getElementById("story-btn").disabled = false;
      document.getElementById("image-btn").disabled = false;
    }
  }, 500);
};


// window.connectYouTube = async function () {
//   const uid = localStorage.getItem("uid");
//   if (!uid) return alert("Not logged in");

//   // Open OAuth in a new popup window
//   const authWindow = window.open(
//     `http://localhost:8000/authorize?uid=${uid}`,
//     "_blank",
//     "width=600,height=700"
//   );

//   // Poll until the OAuth window is closed
//   const poll = setInterval(async () => {
//     if (authWindow.closed) {
//       clearInterval(poll);

//       // After OAuth completes, fetch analysis automatically
//       await getAnalysis();
//     }
//   }, 500);
// };

// window.connectYouTube = async function () {
//   const uid = localStorage.getItem("uid");
//   if (!uid) return alert("Not logged in");

//   // Open OAuth in a new window
//   const authWindow = window.open(`http://localhost:8000/authorize?uid=${uid}`, "_blank", "width=600,height=700");

//   // Poll until the OAuth window is closed
//   const poll = setInterval(async () => {
//     if (authWindow.closed) {
//       clearInterval(poll);
//       // After OAuth is done, fetch analysis automatically
//       await getAnalysis();
//     }
//   }, 500);
// };


let currentAnalysis = ""; // global variable

window.getAnalysis = async function() {
  try {
    const res = await fetch("/analyze", { credentials: "include" });
    const data = await res.json();
    if (data.error) return alert(data.error);

    currentAnalysis = JSON.stringify(data, null, 2); // save analysis globally
    document.getElementById("analysis-box").classList.remove("hidden");
    document.getElementById("analysis-text").innerText = currentAnalysis;
  } catch (err) {
    console.error(err);
    alert("Failed to fetch analysis.");
  }
};


// window.getAnalysis = async function () {
//   try {
//     const res = await fetch("http://localhost:8000/analyze", { credentials: "include" });
//     const data = await res.json();
//     if (data.error) return alert(data.error);

//     document.getElementById("analysis-box").classList.remove("hidden");
//     document.getElementById("analysis-text").innerText = JSON.stringify(data, null, 2);
//   } catch (err) {
//     console.error(err);
//     alert("Failed to fetch analysis.");
//   }
// };


window.generateFromAnalysis = async function(type) {
  if (!currentAnalysis) return alert("No analysis available yet."); // use global variable

  try {
    const res = await fetch("http://localhost:8000/generate_from_analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, analysis: currentAnalysis }),
      credentials: "include"
    });
    const data = await res.json();
    if (data.error) return alert(data.error);

    const resultBox = document.getElementById("gen-result");
    resultBox.classList.remove("hidden");

    if (type === "story") {
      resultBox.innerText = data.result;
    } else if (type === "image") {
      resultBox.innerHTML = `<img src="${data.result}" alt="Generated Image" class="rounded-lg w-full">`;
    }
  } catch (err) {
    console.error(err);
    alert("Failed to generate content from analysis.");
  }
};


// window.generateFromAnalysis = async function(type) {
//   const analysisText = document.getElementById("analysis-text").innerText;
//   if (!analysisText) return alert("No analysis available yet.");

//   try {
//     const res = await fetch("http://localhost:8000/generate_from_analysis", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ type, analysis: analysisText }),
//       credentials: "include"
//     });
//     const data = await res.json();
//     if (data.error) return alert(data.error);

//     const resultBox = document.getElementById("gen-result");
//     resultBox.classList.remove("hidden");

//     if (type === "story") {
//       resultBox.innerText = data.result;
//     } else if (type === "image") {
//       resultBox.innerHTML = `<img src="${data.result}" alt="Generated Image" class="rounded-lg w-full">`;
//     }
//   } catch (err) {
//     console.error(err);
//     alert("Failed to generate content from analysis.");
//   }
// };
