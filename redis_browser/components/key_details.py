import reflex as rx
from redis_browser.states.key_details_state import KeyDetailsState


def type_badge(ktype: str):
    bg_color = rx.match(
        ktype,
        ("string", "bg-blue-100 text-blue-700"),
        ("hash", "bg-purple-100 text-purple-700"),
        ("list", "bg-emerald-100 text-emerald-700"),
        ("set", "bg-orange-100 text-orange-700"),
        ("zset", "bg-indigo-100 text-indigo-700"),
        "bg-slate-100 text-slate-700",
    )
    return rx.el.span(
        ktype.upper(),
        class_name=f"px-2 py-0.5 rounded-full text-[10px] font-bold {bg_color} w-fit",
    )


def string_handler():
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                "Value",
                class_name="text-xs font-bold text-slate-400 uppercase mb-2 block",
            ),
            rx.el.div(
                rx.el.pre(
                    KeyDetailsState.string_value,
                    class_name="text-sm font-mono whitespace-pre-wrap break-all text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-100",
                ),
                class_name="relative",
            ),
            class_name="mb-6",
        ),
        rx.el.button(
            rx.icon("pencil", class_name="h-4 w-4 mr-2"),
            "Edit Value",
            on_click=lambda: KeyDetailsState.open_edit_modal(
                "", KeyDetailsState.string_value
            ),
            class_name="w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg font-bold text-sm hover:bg-indigo-700 transition-all",
        ),
    )


def hash_row(field: str, value: str):
    return rx.el.tr(
        rx.el.td(
            field, class_name="px-4 py-3 text-sm font-mono text-slate-600 font-semibold"
        ),
        rx.el.td(value, class_name="px-4 py-3 text-sm font-mono text-slate-500"),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                    on_click=lambda: KeyDetailsState.open_edit_modal(field, value),
                    class_name="p-1.5 hover:bg-indigo-50 text-slate-400 hover:text-indigo-600 rounded",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                    on_click=lambda: KeyDetailsState.delete_hash_field(field),
                    class_name="p-1.5 hover:bg-red-50 text-slate-400 hover:text-red-600 rounded",
                ),
                class_name="flex items-center gap-1",
            ),
            class_name="px-4 py-3",
        ),
        class_name="hover:bg-slate-50 border-b border-slate-50 last:border-0 transition-colors",
    )


def hash_handler():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4("Fields", class_name="text-sm font-bold text-slate-700"),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-1.5"),
                    "Add Field",
                    on_click=lambda: KeyDetailsState.open_edit_modal(),
                    class_name="flex items-center text-xs font-bold text-indigo-600 hover:text-indigo-700",
                ),
                class_name="flex items-center justify-between mb-4",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Field",
                                class_name="px-4 py-2 text-left text-[10px] font-bold text-slate-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Value",
                                class_name="px-4 py-2 text-left text-[10px] font-bold text-slate-400 uppercase tracking-wider",
                            ),
                            rx.el.th("", class_name="w-20"),
                            class_name="bg-slate-50",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            KeyDetailsState.hash_value,
                            lambda kv: hash_row(kv[0], kv[1]),
                        )
                    ),
                    class_name="w-full table-auto",
                ),
                class_name="border border-slate-100 rounded-xl overflow-hidden",
            ),
        )
    )


def edit_modal():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Edit Data", class_name="text-lg font-bold text-slate-800"
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=KeyDetailsState.set_show_edit_modal(False),
                        class_name="text-slate-400 hover:text-slate-600",
                    ),
                    class_name="flex items-center justify-between mb-6",
                ),
                rx.match(
                    KeyDetailsState.key_type,
                    (
                        "string",
                        rx.el.form(
                            rx.el.textarea(
                                name="value",
                                default_value=KeyDetailsState.string_value,
                                class_name="w-full h-40 p-4 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-mono mb-6 shadow-sm",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    type="button",
                                    on_click=KeyDetailsState.set_show_edit_modal(False),
                                    class_name="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded",
                                ),
                                rx.el.button(
                                    "Save",
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-bold text-white bg-indigo-600 rounded-lg",
                                ),
                                class_name="flex justify-end gap-3",
                            ),
                            on_submit=KeyDetailsState.update_string_value,
                        ),
                    ),
                    (
                        "hash",
                        rx.el.form(
                            rx.el.div(
                                rx.el.label(
                                    "Field",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.input(
                                    name="field",
                                    default_value=KeyDetailsState.edit_field_name,
                                    placeholder="Field name",
                                    class_name="w-full p-2 border border-slate-200 rounded mb-4 text-sm",
                                ),
                                rx.el.label(
                                    "Value",
                                    class_name="block text-xs font-bold text-slate-500 mb-1",
                                ),
                                rx.el.textarea(
                                    name="value",
                                    default_value=KeyDetailsState.edit_field_value,
                                    placeholder="Value",
                                    class_name="w-full h-32 p-2 border border-slate-200 rounded text-sm font-mono mb-6",
                                ),
                                class_name="mb-2",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    type="button",
                                    on_click=KeyDetailsState.set_show_edit_modal(False),
                                    class_name="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded",
                                ),
                                rx.el.button(
                                    "Save Field",
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-bold text-white bg-indigo-600 rounded-lg",
                                ),
                                class_name="flex justify-end gap-3",
                            ),
                            on_submit=KeyDetailsState.set_hash_field,
                        ),
                    ),
                    rx.el.p("Edit modal not yet available for this type."),
                ),
                class_name="bg-white rounded-2xl p-8 w-[500px] shadow-2xl",
            ),
            class_name="fixed inset-0 flex items-center justify-center bg-slate-900/60 backdrop-blur-[2px] z-[60]",
        ),
        class_name=rx.cond(KeyDetailsState.show_edit_modal, "block", "hidden"),
    )


def key_details_panel():
    return rx.el.div(
        rx.cond(
            KeyDetailsState.key_name == "",
            rx.el.div(
                rx.icon("info", class_name="h-12 w-12 text-slate-200 mb-4"),
                rx.el.p(
                    "Select a key to view details",
                    class_name="text-slate-400 font-medium",
                ),
                class_name="flex flex-col items-center justify-center h-full",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            type_badge(KeyDetailsState.key_type),
                            rx.el.h2(
                                KeyDetailsState.key_name,
                                class_name="text-xl font-bold text-slate-800 break-all font-mono",
                            ),
                            class_name="flex flex-col gap-2",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("copy", class_name="h-4 w-4"),
                                on_click=rx.set_clipboard(KeyDetailsState.key_name),
                                class_name="p-2 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-4 w-4 text-red-500"),
                                on_click=KeyDetailsState.delete_key,
                                class_name="p-2 hover:bg-red-50 rounded-lg transition-colors",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        class_name="flex items-start justify-between p-6 border-b border-slate-100",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon("clock", class_name="h-4 w-4 text-slate-400"),
                            rx.el.span(
                                "TTL:",
                                class_name="text-xs font-bold text-slate-400 uppercase",
                            ),
                            rx.el.span(
                                KeyDetailsState.ttl_display,
                                class_name="text-sm font-semibold text-slate-600",
                            ),
                            class_name="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100",
                        ),
                        class_name="px-6 py-4",
                    ),
                    rx.el.div(
                        rx.cond(
                            KeyDetailsState.is_loading,
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-8 w-8 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin"
                                ),
                                class_name="flex items-center justify-center py-20",
                            ),
                            rx.el.div(
                                rx.match(
                                    KeyDetailsState.key_type,
                                    ("string", string_handler()),
                                    ("hash", hash_handler()),
                                    rx.el.div(
                                        rx.el.p(
                                            "Handler for type "
                                            + KeyDetailsState.key_type
                                            + " is in progress.",
                                            class_name="text-slate-400 italic",
                                        ),
                                        class_name="p-8 text-center",
                                    ),
                                ),
                                class_name="px-6 pb-6",
                            ),
                        ),
                        class_name="flex-1 overflow-y-auto",
                    ),
                    class_name="flex flex-col h-full",
                ),
                edit_modal(),
                class_name="h-full",
            ),
        ),
        class_name="h-full w-full bg-white",
    )