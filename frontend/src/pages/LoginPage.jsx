import { useState } from "react";

import "./Auth.css";

import api from "../utils/api";

import {
    saveAuthData
} from "../utils/auth";

function LoginPage({
    setIsLoggedIn,
    onShowRegister
}) {

    const [
        username,
        setUsername
    ] = useState("");

    const [
        password,
        setPassword
    ] = useState("");

    const login = async (event) => {

        event.preventDefault();

        try {

            const response = await api.post(
                "/login",
                {
                    username,
                    password
                }
            );

            saveAuthData(
                response.data.access_token,
                response.data.role
            );

            setIsLoggedIn(true);

        } catch {

            alert(
                "Ошибка входа"
            );
        }
    };

    return (
        <div className="auth-page">
            <form
                className="auth-card"
                onSubmit={login}
            >
                <h1>
                    Вход
                </h1>

                <input
                    type="text"
                    placeholder="Логин"
                    value={username}
                    required
                    onChange={(event) =>
                        setUsername(event.target.value)
                    }
                />

                <input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    required
                    onChange={(event) =>
                        setPassword(event.target.value)
                    }
                />

                <div className="auth-actions">
                    <button
                        type="submit"
                        className="auth-button auth-button-primary"
                    >
                        Войти
                    </button>

                    <button
                        type="button"
                        className="auth-button auth-button-secondary"
                        onClick={onShowRegister}
                    >
                        Зарегистрироваться
                    </button>
                </div>
            </form>
        </div>
    );
}

export default LoginPage;
