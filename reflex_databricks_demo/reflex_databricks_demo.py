import asyncio

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
    updating_patient_ids: list[str] = []

    @rx.event
    def load_patients(self):
        """Load patient data from Databricks."""

        self.databricks_error = ""

        try:
            self.patients = get_patients()

        except Exception as error:
            self.databricks_error = str(error)

    def _set_patient_status(self, patient_id: str, status: str):
        self.patients = [
            {**patient, "status": status}
            if patient["patient_id"] == patient_id
            else patient
            for patient in self.patients
        ]

    @rx.event(background=True)
    async def update_status(self, patient_id: str, status: str):
        """Update a patient's status in Databricks.

        Runs in the background so the row shows a spinner while the
        (possibly slow) SQL UPDATE is running.
        """

        async with self:
            self.databricks_error = ""
            old_status = next(
                (
                    patient["status"]
                    for patient in self.patients
                    if patient["patient_id"] == patient_id
                ),
                status,
            )
            self._set_patient_status(patient_id, status)
            self.updating_patient_ids.append(patient_id)

        try:
            await asyncio.to_thread(update_patient_status, patient_id, status)

        except Exception as error:
            async with self:
                self._set_patient_status(patient_id, old_status)
                self.databricks_error = str(error)

        finally:
            async with self:
                self.updating_patient_ids.remove(patient_id)


def patient_row(patient: dict) -> rx.Component:
    is_updating = State.updating_patient_ids.contains(
        patient["patient_id"].to(str)
    )

    return rx.table.row(
        rx.table.cell(patient["patient_id"]),
        rx.table.cell(patient["name"]),
        rx.table.cell(patient["department"]),
        rx.table.cell(patient["priority"]),
        rx.table.cell(
            rx.hstack(
                rx.select(
                    PATIENT_STATUSES,
                    value=patient["status"].to(str),
                    disabled=is_updating,
                    on_change=lambda status: State.update_status(
                        patient["patient_id"].to(str),
                        status,
                    ),
                ),
                rx.cond(
                    is_updating,
                    rx.hstack(
                        rx.spinner(size="2"),
                        rx.text("Updating…", size="1", color_scheme="gray"),
                        align="center",
                        spacing="1",
                    ),
                ),
                align="center",
                spacing="2",
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
