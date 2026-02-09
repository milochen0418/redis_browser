import reflex as rx
from redis_browser.states.connection_state import ConnectionState


def config_modal():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        rx.cond(
                            ConnectionState.editing_id != "",
                            "Edit Connection",
                            "New Redis Connection",
                        ),
                        class_name="text-lg font-bold text-slate-800",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=ConnectionState.toggle_modal,
                        class_name="text-slate-400 hover:text-slate-600",
                    ),
                    class_name="flex items-center justify-between mb-6",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Connection Name",
                            class_name="block text-xs font-bold text-slate-500 mb-1",
                        ),
                        rx.el.input(
                            placeholder="Production DB",
                            name="name",
                            default_value=ConnectionState.form_name,
                            class_name="w-full px-3 py-2 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Hostname",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.input(
                                    placeholder="127.0.0.1",
                                    name="host",
                                    default_value=ConnectionState.form_host,
                                    class_name="w-full px-3 py-2 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm",
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Port",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.input(
                                    type="number",
                                    name="port",
                                    default_value=ConnectionState.form_port.to_string(),
                                    class_name="w-full px-3 py-2 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm",
                                ),
                                class_name="w-24",
                            ),
                            class_name="flex gap-4",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Password",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.input(
                                    type="password",
                                    placeholder="••••••••",
                                    name="password",
                                    default_value=ConnectionState.form_password,
                                    class_name="w-full px-3 py-2 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm",
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Database",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.input(
                                    type="number",
                                    name="db",
                                    default_value=ConnectionState.form_db.to_string(),
                                    class_name="w-full px-3 py-2 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm",
                                ),
                                class_name="w-24",
                            ),
                            class_name="flex gap-4",
                        ),
                        class_name="mb-8",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=ConnectionState.toggle_modal,
                            class_name="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded transition-colors",
                        ),
                        rx.el.button(
                            "Save Connection",
                            type="submit",
                            class_name="px-4 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded shadow-sm shadow-indigo-200 transition-all",
                        ),
                        class_name="flex justify-end gap-3",
                    ),
                    on_submit=ConnectionState.save_config,
                ),
                class_name="bg-white rounded-xl shadow-2xl p-8 w-[450px] max-w-full",
            ),
            class_name="fixed inset-0 flex items-center justify-center bg-slate-900/40 backdrop-blur-[2px] z-50",
        ),
        class_name=rx.cond(ConnectionState.show_config_modal, "block", "hidden"),
    )