import { useState } from "react";

import "./Auth.css";

import api from "../utils/api";

function RegisterPage({
    onBackToLogin
}) {

    const [
        username,
        setUsername
    ] = useState("");

    const [
        password,
        setPassword
    ] = useState("");

    const [
        role,
        setRole
    ] = useState("student");

    const register = async (event) => {

        event.preventDefault();

        try {

            await api.post(
                "/register",
                {
                    username,
                    password,
                    role
                }
            );

            alert(
                "Пользователь создан"
            );

            onBackToLogin();

        } catch {

            alert(
                "Ошибка регистрации"
            );
        }
    };

    return (
        <div className="auth-page">
            <form
                className="auth-card"
                onSubmit={register}
            >
                <h1>
                    Регистрация
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

                <select
                    value={role}
                    onChange={(event) =>
                        setRole(event.target.value)
                    }
                >
                    <option value="student">
                        Студент
                    </option>

                    <option value="teacher">
                        Преподаватель
                    </option>
                </select>

                <div className="auth-actions">
                    <button
                        type="submit"
                        className="auth-button auth-button-primary"
                    >
                        Создать аккаунт
                    </button>

                    <button
                        type="button"
                        className="auth-button auth-button-secondary"
                        onClick={onBackToLogin}
                    >
                        Уже есть аккаунт
                    </button>
                </div>
            </form>
        </div>
    );
}

export default RegisterPage;
