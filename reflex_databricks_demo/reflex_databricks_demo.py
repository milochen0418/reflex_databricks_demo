import reflex as rx
from .databricks_client import get_patients

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




def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Reflex Databricks Demo", size="9"),
            rx.text("Blank Reflex project. Start building here."),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App()
app.add_page(index, route="/")
