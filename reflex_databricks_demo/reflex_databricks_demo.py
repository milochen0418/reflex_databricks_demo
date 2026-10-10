import reflex as rx
from .databricks_client import (
    PATIENT_STATUSES,
    get_patients,
    update_patient_status,
)

class State(rx.State):
    """The app state."""

    patients: list[dict[str, str | int]] = []
    databricks_error: str = ""

    @rx.event
    def load_patients(self):
        """Load patient data from Databricks."""

        self.databricks_error = ""

        try:
            self.patients = get_patients()

        except Exception as error:
            self.databricks_error = str(error)

    @rx.event
    def update_status(self, patient_id: str, status: str):
        """Update a patient's status in Databricks."""

        self.databricks_error = ""

        try:
            update_patient_status(patient_id, status)

            self.patients = [
                {**patient, "status": status}
                if patient["patient_id"] == patient_id
                else patient
                for patient in self.patients
            ]

        except Exception as error:
            self.databricks_error = str(error)


def patient_row(patient: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(patient["patient_id"]),
        rx.table.cell(patient["name"]),
        rx.table.cell(patient["department"]),
        rx.table.cell(patient["priority"]),
        rx.table.cell(
            rx.select(
                PATIENT_STATUSES,
                value=patient["status"].to(str),
                on_change=lambda status: State.update_status(
                    patient["patient_id"].to(str),
                    status,
                ),
            )
        ),
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading(
                "🏥 Patient Queue",
                size="9",
            ),

            rx.text(
                "Patient data powered by Databricks"
            ),

            rx.button(
                "Refresh from Databricks",
                on_click=State.load_patients,
            ),

            rx.cond(
                State.databricks_error != "",
                rx.text(
                    State.databricks_error,
                    color="red",
                ),
            ),

            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Patient ID"),
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Department"),
                        rx.table.column_header_cell("Priority"),
                        rx.table.column_header_cell("Status"),
                    )
                ),

                rx.table.body(
                    rx.foreach(
                        State.patients,
                        patient_row,
                    )
                ),

                width="100%",
            ),

            spacing="5",
            width="100%",
        ),

        max_width="1000px",
        padding="2em",
    )


app = rx.App()
app.add_page(
    index,
    route="/",
    on_load=State.load_patients,
)
