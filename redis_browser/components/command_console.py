import reflex as rx
from redis_browser.states.command_state import CommandState


def log_entry(entry: dict):
    is_error = entry["status"] == "error"
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                entry["timestamp"],
                class_name="text-[10px] text-slate-400 font-mono min-w-[60px]",
            ),
            rx.el.span(">", class_name="text-slate-400 mx-2 font-bold select-none"),
            rx.el.span(
                entry["command"],
                class_name="font-mono text-xs text-indigo-600 font-semibold break-all",
            ),
            class_name="flex items-start mb-1",
        ),
        rx.el.pre(
            entry["output"],
            class_name=rx.cond(
                is_error,
                "text-xs font-mono text-red-500 ml-[85px] whitespace-pre-wrap break-all",
                "text-xs font-mono text-slate-600 ml-[85px] whitespace-pre-wrap break-all",
            ),
        ),
        class_name="py-2 border-b border-slate-50 last:border-0",
    )


def command_console():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Console & Logs",
                    class_name="text-xs font-bold text-slate-500 uppercase tracking-wider",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                    "Clear",
                    on_click=CommandState.clear_logs,
                    class_name="text-[10px] flex items-center gap-1 text-slate-400 hover:text-red-500 transition-colors",
                ),
                class_name="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-100",
            ),
            rx.el.div(
                rx.cond(
                    CommandState.logs.length() > 0,
                    rx.el.div(
                        rx.foreach(CommandState.logs, log_entry),
                        class_name="p-4 flex flex-col-reverse justify-end min-h-full",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "No commands executed yet.",
                            class_name="text-xs text-slate-300 italic text-center mt-10",
                        ),
                        class_name="h-full",
                    ),
                ),
                class_name="flex-1 overflow-y-auto bg-white min-h-0",
            ),
            class_name="flex-1 flex flex-col min-h-0 overflow-hidden",
        ),
        rx.el.form(
            rx.el.div(
                rx.icon(
                    "terminal",
                    class_name="h-4 w-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2",
                ),
                rx.el.input(
                    placeholder="Enter Redis command (e.g., SET mykey 'hello')",
                    name="command",
                    class_name="w-full pl-9 pr-24 py-2.5 text-sm font-mono border-t border-slate-200 focus:outline-none focus:bg-slate-50 transition-colors placeholder:text-slate-300",
                    default_value="",
                    key=f"command_input_{CommandState.logs.length()}",
                ),
                rx.el.button(
                    rx.cond(
                        CommandState.is_executing,
                        rx.el.span(
                            class_name="animate-spin h-3 w-3 border-2 border-slate-400 border-t-transparent rounded-full"
                        ),
                        "Execute",
                    ),
                    type="submit",
                    disabled=CommandState.is_executing,
                    class_name="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 bg-slate-800 text-white text-xs font-bold rounded hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center min-w-[70px]",
                ),
                class_name="relative",
            ),
            on_submit=CommandState.execute_command,
            class_name="bg-white z-10",
        ),
        class_name="h-64 border-t border-slate-200 flex flex-col bg-white",
    )