import asyncio

import reflex as rx
from .databricks_client import (
    PATIENT_STATUSES,
    get_patients,
    update_patient_status,
)

# Everyone who opens the app is linked to this token, so they all share
# one PatientQueueState (no underscores allowed in the token).
SHARED_QUEUE_TOKEN = "patient-queue"


class State(rx.State):
    """Per-user state."""

    databricks_error: str = ""


class PatientQueueState(rx.SharedState):
    """The patient queue, shared by every user of the app.

    Changes made here (loaded rows, status updates, spinners) are pushed to
    all connected users.
    """

    patients: list[dict[str, str | int]] = []
    updating_patient_ids: list[str] = []
    is_loading: bool = False
    has_loaded: bool = False

    @rx.event
    async def join_queue(self):
        """Link this user to the shared queue, loading it on first use."""

        shared_queue = await self._link_to(SHARED_QUEUE_TOKEN)

        if not shared_queue.has_loaded:
            return PatientQueueState.load_patients

    async def _set_error(self, message: str):
        user_state = await self.get_state(State)
        user_state.databricks_error = message

    @rx.event(background=True)
    async def load_patients(self):
        """Load patient data from Databricks.

        Runs in the background so the page shows a loading indicator while
        the (possibly slow) query is running.
        """

        async with self:
            await self._set_error("")
            if self.is_loading:
                return
            self.is_loading = True

        try:
            patients = await asyncio.to_thread(get_patients)

            async with self:
                self.patients = patients
                self.has_loaded = True

        except Exception as error:
            async with self:
                await self._set_error(str(error))

        finally:
            async with self:
                self.is_loading = False

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
            await self._set_error("")
            if patient_id in self.updating_patient_ids:
                return
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
                await self._set_error(str(error))

        finally:
            async with self:
                self.updating_patient_ids.remove(patient_id)


def patient_row(patient: dict) -> rx.Component:
    is_updating = PatientQueueState.updating_patient_ids.contains(
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
                    on_change=lambda status: PatientQueueState.update_status(
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

            rx.hstack(
                rx.button(
                    "Refresh from Databricks",
                    loading=PatientQueueState.is_loading,
                    on_click=PatientQueueState.load_patients,
                ),
                rx.cond(
                    PatientQueueState.is_loading,
                    rx.hstack(
                        rx.spinner(size="2"),
                        rx.text(
                            "Loading patients from Databricks…",
                            size="2",
                            color_scheme="gray",
                        ),
                        align="center",
                        spacing="2",
                    ),
                ),
                align="center",
                spacing="3",
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
                        PatientQueueState.patients,
                        patient_row,
                    )
                ),

                width="100%",
                opacity=rx.cond(PatientQueueState.is_loading, "0.5", "1"),
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
    on_load=PatientQueueState.join_queue,
)
