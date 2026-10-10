import reflex as rx


class State(rx.State):
    """The app state."""


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
