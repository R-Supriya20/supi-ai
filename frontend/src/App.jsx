
import { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";

export default function App() {
  const [page, setPage] = useState(() =>
    localStorage.getItem("access_token") ? "chat" : "login"
  );

  const handleLoginSuccess = () => {
    setPage("chat");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setPage("login");
  };

  if (page === "chat" && localStorage.getItem("access_token")) {
    return <Chat onLogout={handleLogout} />;
  }

  if (page === "register") {
    return (
      <Register
        onRegisterSuccess={() => setPage("login")}
        onLoginClick={() => setPage("login")}
      />
    );
  }

  return (
    <Login
      onLoginSuccess={handleLoginSuccess}
      onRegisterClick={() => setPage("register")}
    />
  );
}
