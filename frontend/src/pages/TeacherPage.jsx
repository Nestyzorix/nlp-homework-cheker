import { useState } from "react";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";

import CreateAssignment from "./CreateAssignment";
import TeacherAnswers from "./TeacherAnswers";
import TeacherAssignments from "./TeacherAssignments";

function TeacherPage({
    onLogout
}) {

    const [
        activeSection,
        setActiveSection
    ] = useState("create");

    return (

        <div
            style={{
                display: "flex",
                backgroundColor: "#020617",
                color: "white"
            }}
        >

            <Sidebar
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
                        activeSection === "create" && (
                            <CreateAssignment />
                        )
                    }

                    {
                        activeSection === "assignments" && (
                            <TeacherAssignments />
                        )
                    }

                    {
                        activeSection === "answers" && (
                            <TeacherAnswers />
                        )
                    }

                </div>

            </div>

        </div>
    );
}

export default TeacherPage;
