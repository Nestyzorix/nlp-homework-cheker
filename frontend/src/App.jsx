import { useState } from "react";

import TeacherPage from "./pages/TeacherPage";
import StudentPage from "./pages/StudentPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

import {
    getRole,
    isAuthenticated,
    logout
} from "./utils/auth";

function App() {

    const [
        isLoggedIn,
        setIsLoggedIn
    ] = useState(
        isAuthenticated()
    );

    const [
        showRegister,
        setShowRegister
    ] = useState(false);

    if (!isLoggedIn) {

        if (showRegister) {

            return (
                <RegisterPage
                    onBackToLogin={() =>
                        setShowRegister(false)
                    }
                />
            );
        }

        return (
            <LoginPage
                setIsLoggedIn={setIsLoggedIn}
                onShowRegister={() =>
                    setShowRegister(true)
                }
            />
        );
    }

    const role = getRole();

    const handleLogout = () => {

        logout();
        setShowRegister(false);
        setIsLoggedIn(false);
    };

    if (role === "teacher") {

        return (
            <TeacherPage
                onLogout={handleLogout}
            />
        );
    }

    return (
        <StudentPage
            onLogout={handleLogout}
        />
    );
}

export default App;
