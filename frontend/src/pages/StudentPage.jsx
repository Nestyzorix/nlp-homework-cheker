import { useState } from "react";

import Header from "../components/Header";
import StudentSidebar from "../components/StudentSidebar";

import StudentGrades from "./StudentGrades";
import StudentTasks from "./StudentTasks";

function StudentPage({
    onLogout
}) {

    const [
        activeSection,
        setActiveSection
    ] = useState("tasks");

    return (

        <div
            style={{
                display: "flex",
                backgroundColor:
                    "#020617",

                color: "white"
            }}
        >

            <StudentSidebar
                activeSection={activeSection}
                setActiveSection={setActiveSection}
            />

            <div
                style={{
                    flex: 1
                }}
            >

                <Header
                    onLogout={onLogout}
                />

                <div
                    style={{
                        padding: "40px"
                    }}
                >

                    {
                        activeSection === "tasks" && (
                            <StudentTasks />
                        )
                    }

                    {
                        activeSection === "grades" && (
                            <StudentGrades />
                        )
                    }

                </div>

            </div>

        </div>
    );
}

export default StudentPage;
