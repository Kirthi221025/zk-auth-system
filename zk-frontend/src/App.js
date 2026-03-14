import axios from "axios";
import { useState } from "react";

function App() {

  const [username, setUsername] = useState("");
  const [challenge, setChallenge] = useState("");
  const [proof, setProof] = useState("");
  const [result, setResult] = useState("");

  const getChallenge = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/get_challenge/",
        { username }
      );
      setChallenge(res.data.challenge);
    } catch {
      setResult("Error fetching challenge");
    }
  };

  const verify = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/verify/",
        { username, proof }
      );
      setResult("Login success ✅ Token: " + res.data.access);
    } catch {
      setResult("Verification failed ❌");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>ZKP Authentication</h2>

      <input
        placeholder="Enter username"
        onChange={(e) => setUsername(e.target.value)}
      />

      <br /><br />

      <button onClick={getChallenge}>Get Challenge</button>

      <p>{challenge}</p>

      <input
        placeholder="Enter proof"
        onChange={(e) => setProof(e.target.value)}
      />

      <br /><br />

      <button onClick={verify}>Verify</button>

      <p>{result}</p>
    </div>
  );
}

export default App;