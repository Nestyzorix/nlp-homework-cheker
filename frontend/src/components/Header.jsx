import {
    getRole
} from "../utils/auth";

function Header({
    onLogout
}) {

    const role = getRole();

    const roleLabel =
        role === "teacher"
            ? "Преподаватель"
            : "Студент";

    return (

        <div
            style={{
                height: "70px",
                backgroundColor: "#111827",
                color: "white",
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
                gap: "16px",
                paddingRight: "30px",
                borderBottom: "1px solid #374151"
            }}
        >

            <div
                style={{
                    color: "#cbd5e1"
                }}
            >
                {roleLabel}
            </div>

            <button
                type="button"
                onClick={onLogout}
                style={{
                    minHeight: "38px",
                    padding: "0 14px",
                    border: "1px solid #475569",
                    borderRadius: "6px",
                    backgroundColor: "transparent",
                    color: "#f8fafc",
                    cursor: "pointer",
                    font: "inherit"
                }}
            >
                Выйти
            </button>

        </div>
    );
}

export default Header;
