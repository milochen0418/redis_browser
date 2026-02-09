import reflex as rx
from redis_browser.states.connection_state import ConnectionState, RedisConfig


def connection_item(config: RedisConfig):
    is_selected = ConnectionState.selected_id == config["id"]
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("database", class_name="h-4 w-4 text-slate-500"),
                    rx.el.span(
                        config["name"], class_name="font-semibold text-sm truncate"
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.span(
                    f"{config['host']}:{config['port']}",
                    class_name="text-[10px] text-slate-400 font-mono mt-1 block",
                ),
                class_name="flex-1",
                on_click=lambda: ConnectionState.select_connection(config["id"]),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="h-3 w-3"),
                    on_click=lambda: ConnectionState.edit_config(config["id"]),
                    class_name="p-1 hover:bg-slate-200 rounded text-slate-500",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-3 w-3"),
                    on_click=lambda: ConnectionState.delete_config(config["id"]),
                    class_name="p-1 hover:bg-red-100 hover:text-red-600 rounded text-slate-400",
                ),
                class_name="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name=rx.cond(
            is_selected,
            "p-3 rounded-lg border-2 border-indigo-500 bg-indigo-50 cursor-pointer group mb-2 shadow-sm transition-all",
            "p-3 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer group mb-2 transition-all",
        ),
    )


def sidebar():
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("zap", class_name="h-6 w-6 text-indigo-600"),
                rx.el.div(
                    rx.el.h1(
                        "Redis Browser",
                        class_name="text-xl font-bold text-slate-800 tracking-tight",
                    ),
                    rx.el.p(
                        "Built with Python Reflex",
                        class_name="text-[11px] text-slate-400 font-medium",
                    ),
                    class_name="flex flex-col",
                ),
                class_name="flex items-center gap-2 p-6 border-b border-slate-100 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Connections",
                        class_name="text-xs font-bold text-slate-400 uppercase tracking-widest",
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4"),
                        on_click=ConnectionState.toggle_modal,
                        class_name="p-1 rounded bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm",
                    ),
                    class_name="flex items-center justify-between px-6 mb-4",
                ),
                rx.el.div(
                    rx.foreach(ConnectionState.configs, connection_item),
                    class_name="px-4 overflow-y-auto max-h-[calc(100vh-250px)]",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.cond(
                    ConnectionState.is_connected,
                    rx.el.div(
                        rx.el.div(
                            class_name="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"
                        ),
                        rx.el.span(
                            "Connected",
                            class_name="text-xs font-medium text-emerald-700",
                        ),
                        class_name="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-full border border-emerald-100",
                    ),
                    rx.el.div(
                        rx.el.div(class_name="h-2 w-2 rounded-full bg-slate-300"),
                        rx.el.span(
                            "Disconnected",
                            class_name="text-xs font-medium text-slate-500",
                        ),
                        class_name="flex items-center gap-2 bg-slate-100 px-3 py-2 rounded-full border border-slate-200",
                    ),
                ),
                class_name="mt-auto p-6 border-t border-slate-100",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="w-72 bg-slate-50 border-r border-slate-200 h-screen shrink-0",
    )