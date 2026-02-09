import reflex as rx
from redis_browser.states.key_browser_state import KeyBrowserState, TreeItem


def tree_node(item: TreeItem):
    """Renders a single node in the tree (folder or key)."""
    padding_left = f"{item['level'] * 1.5}rem"
    is_selected = KeyBrowserState.selected_key == item["full_path"]
    return rx.el.div(
        rx.el.div(
            rx.cond(
                item["type"] == "folder",
                rx.el.div(
                    rx.icon(
                        rx.cond(item["expanded"], "folder-open", "folder"),
                        class_name="h-4 w-4 text-indigo-400 mr-2",
                    ),
                    class_name="cursor-pointer",
                    on_click=lambda: KeyBrowserState.toggle_expand(item["full_path"]),
                ),
                rx.icon("key", class_name="h-4 w-4 text-slate-400 mr-2"),
            ),
            rx.el.span(
                item["label"],
                class_name="flex-1 truncate text-sm font-medium text-slate-700 select-none",
            ),
            rx.cond(
                item["type"] == "folder",
                rx.el.span(
                    item["children_count"],
                    class_name="ml-2 px-1.5 py-0.5 text-[10px] font-bold bg-slate-100 text-slate-500 rounded-full",
                ),
            ),
            class_name="flex items-center w-full min-w-0",
        ),
        class_name=rx.cond(
            is_selected,
            "flex items-center py-1.5 px-3 bg-indigo-50 border-r-2 border-indigo-500 cursor-pointer hover:bg-indigo-100 transition-colors",
            "flex items-center py-1.5 px-3 border-r-2 border-transparent cursor-pointer hover:bg-slate-50 transition-colors",
        ),
        style={
            "padding_left": rx.cond(
                item["level"] == 0, "12px", f"calc({padding_left} + 12px)"
            )
        },
        on_click=rx.cond(
            item["type"] == "folder",
            KeyBrowserState.toggle_expand(item["full_path"]),
            KeyBrowserState.select_key(item["full_path"]),
        ),
    )


def key_browser():
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400",
                ),
                rx.el.input(
                    placeholder="Filter keys...",
                    on_change=KeyBrowserState.set_filter_query,
                    class_name="w-full pl-9 pr-3 py-1.5 text-sm border border-slate-200 rounded-md focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-slate-50",
                    default_value=KeyBrowserState.filter_query,
                ),
                class_name="relative flex-1",
            ),
            rx.el.button(
                rx.icon(
                    "refresh-cw",
                    class_name=rx.cond(
                        KeyBrowserState.is_loading_keys,
                        "h-4 w-4 text-slate-600 animate-spin",
                        "h-4 w-4 text-slate-600",
                    ),
                ),
                on_click=KeyBrowserState.scan_keys,
                disabled=KeyBrowserState.is_loading_keys,
                title="Refresh Keys",
                class_name="p-2 hover:bg-slate-100 rounded-md border border-slate-200 bg-white ml-2",
            ),
            class_name="p-3 border-b border-slate-100 flex items-center bg-white sticky top-0 z-10",
        ),
        rx.el.div(
            rx.cond(
                KeyBrowserState.is_loading_keys,
                rx.el.div(
                    rx.el.div(
                        class_name="h-8 w-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4"
                    ),
                    rx.el.p(
                        "Scanning Redis keys...",
                        class_name="text-sm text-slate-500 font-medium",
                    ),
                    class_name="flex flex-col items-center justify-center h-full py-12",
                ),
                rx.cond(
                    KeyBrowserState.keys.length() > 0,
                    rx.el.div(
                        rx.foreach(KeyBrowserState.flat_tree, tree_node),
                        class_name="py-2",
                    ),
                    rx.el.div(
                        rx.icon("search-x", class_name="h-12 w-12 text-slate-200 mb-2"),
                        rx.el.p("No keys found", class_name="text-sm text-slate-400"),
                        class_name="flex flex-col items-center justify-center h-64",
                    ),
                ),
            ),
            class_name="flex-1 overflow-y-auto overflow-x-hidden bg-white custom-scrollbar",
        ),
        rx.el.div(
            rx.el.span(
                f"{KeyBrowserState.keys.length()} keys found",
                class_name="text-xs font-medium text-slate-500",
            ),
            rx.el.span(
                f"Namespace: {KeyBrowserState.delimiter}",
                class_name="text-xs text-slate-400 ml-auto font-mono bg-slate-100 px-1.5 rounded",
            ),
            class_name="h-8 flex items-center px-4 border-t border-slate-100 bg-slate-50",
        ),
        class_name="flex flex-col h-full bg-white border-r border-slate-100",
    )