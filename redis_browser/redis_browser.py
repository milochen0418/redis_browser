import reflex as rx
from redis_browser.states.connection_state import ConnectionState
from redis_browser.components.sidebar import sidebar
from redis_browser.components.config_modal import config_modal
from redis_browser.components.key_browser import key_browser
from redis_browser.components.key_details import key_details_panel
from redis_browser.components.command_console import command_console


def empty_panel_placeholder(title: str, icon_name: str, message: str):
    return rx.el.div(
        rx.el.div(
            rx.icon(icon_name, class_name="h-12 w-12 text-slate-200 mb-4 mx-auto"),
            rx.el.h3(title, class_name="text-lg font-bold text-slate-400"),
            rx.el.p(
                message, class_name="text-sm text-slate-300 mt-2 max-w-[200px] mx-auto"
            ),
            class_name="text-center",
        ),
        class_name="flex items-center justify-center h-full border-2 border-dashed border-slate-100 rounded-2xl m-6 bg-slate-50/30",
    )


def main_content():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    rx.cond(
                        ConnectionState.selected_id != "",
                        ConnectionState.active_config["name"],
                        "No Connection Selected",
                    ),
                    class_name="text-sm font-bold text-slate-600",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.div(
                rx.cond(
                    ConnectionState.is_connected,
                    rx.el.button(
                        "Disconnect",
                        on_click=ConnectionState.disconnect_redis,
                        class_name="px-4 py-1.5 text-xs font-bold text-red-600 border border-red-200 bg-red-50 hover:bg-red-100 rounded-lg transition-all",
                    ),
                    rx.el.button(
                        rx.cond(
                            ConnectionState.is_connecting, "Connecting...", "Connect"
                        ),
                        on_click=ConnectionState.connect_redis,
                        disabled=ConnectionState.is_connecting
                        | (ConnectionState.selected_id == ""),
                        class_name="px-6 py-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm shadow-indigo-100 transition-all",
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="h-16 flex items-center justify-between px-6 border-b border-slate-100 bg-white",
        ),
        rx.el.div(
            rx.el.div(
                rx.cond(
                    ConnectionState.is_connected,
                    key_browser(),
                    empty_panel_placeholder(
                        "Disconnected",
                        "unplug",
                        "Connect to a Redis server to browse keys.",
                    ),
                ),
                class_name="flex-1 bg-white border-r border-slate-100 flex flex-col min-h-0",
            ),
            rx.el.div(
                rx.cond(
                    ConnectionState.is_connected,
                    key_details_panel(),
                    empty_panel_placeholder(
                        "No Data", "box-select", "Detailed information appears here."
                    ),
                ),
                class_name="w-[450px] bg-white border-l border-slate-100 flex flex-col",
            ),
            class_name="flex flex-1 overflow-hidden",
        ),
        rx.cond(ConnectionState.is_connected, command_console()),
        class_name="flex-1 flex flex-col min-w-0",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            sidebar(),
            main_content(),
            class_name="flex h-screen w-full bg-white overflow-hidden",
        ),
        config_modal(),
        class_name="font-['Inter'] antialiased text-slate-900",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")