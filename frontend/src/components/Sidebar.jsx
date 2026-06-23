function Sidebar({
    activeSection,
    setActiveSection
}) {

    const buttonStyle = (section) => ({
        width: "100%",
        marginTop: section === "create" ? "20px" : "10px",
        padding: "10px",
        border: "0",
        borderRadius: "3px",
        backgroundColor:
            activeSection === section
                ? "#4b5563"
                : "#6b7280",
        color: "white",
        cursor: "pointer",
        fontWeight: 700
    });

    return (

        <div
            style={{
                width: "220px",
                backgroundColor: "#0f172a",
                color: "white",
                padding: "20px",
                minHeight: "100vh",
                borderRight: "1px solid #374151"
            }}
        >

            <h2>
                Меню
            </h2>

            <button
                onClick={() =>
                    setActiveSection("create")
                }
                style={buttonStyle("create")}
            >
                Создать задание
            </button>

            <button
                onClick={() =>
                    setActiveSection("assignments")
                }
                style={buttonStyle("assignments")}
            >
                Посмотреть задания
            </button>

            <button
                onClick={() =>
                    setActiveSection("answers")
                }
                style={buttonStyle("answers")}
            >
                Просмотреть ответы
            </button>

        </div>
    );
}

export default Sidebar;
