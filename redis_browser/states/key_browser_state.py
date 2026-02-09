import reflex as rx
import redis
import logging
from typing import TypedDict, Optional, Any
from redis_browser.states.connection_state import ConnectionState


class TreeItem(TypedDict):
    id: str
    label: str
    level: int
    type: str
    has_children: bool
    expanded: bool
    children_count: int
    full_path: str


class KeyBrowserState(rx.State):
    keys: list[str] = []
    expanded_paths: list[str] = []
    selected_key: str = ""
    filter_query: str = ""
    is_loading_keys: bool = False
    delimiter: str = ":"

    @rx.var
    def flat_tree(self) -> list[TreeItem]:
        """
        Computes the flat list of visible tree items based on keys, filter, and expansion state.
        """
        filtered_keys = [k for k in self.keys if self.filter_query.lower() in k.lower()]
        filtered_keys.sort()
        tree_root = {}
        for key in filtered_keys:
            parts = key.split(self.delimiter)
            current_level = tree_root
            for i, part in enumerate(parts):
                is_last = i == len(parts) - 1
                if part not in current_level:
                    current_level[part] = {
                        "__children__": {},
                        "__count__": 0,
                        "__is_key__": False,
                        "__path__": self.delimiter.join(parts[: i + 1]),
                    }
                node = current_level[part]
                node["__count__"] += 1
                if is_last:
                    node["__is_key__"] = True
                current_level = node["__children__"]
        visible_items: list[TreeItem] = []

        def traverse(node_dict: dict, level: int):
            sorted_parts = sorted(node_dict.keys())
            for part in sorted_parts:
                info = node_dict[part]
                full_path = info["__path__"]
                is_folder = bool(info["__children__"])
                is_key = info["__is_key__"]
                type_ = "folder" if is_folder else "key"
                is_expanded = full_path in self.expanded_paths
                item: TreeItem = {
                    "id": full_path,
                    "label": part,
                    "level": level,
                    "type": type_,
                    "has_children": is_folder,
                    "expanded": is_expanded,
                    "children_count": info["__count__"] if is_folder else 0,
                    "full_path": full_path,
                }
                visible_items.append(item)
                if is_folder and is_expanded:
                    traverse(info["__children__"], level + 1)

        traverse(tree_root, 0)
        return visible_items

    @rx.event
    def toggle_expand(self, path: str):
        if path in self.expanded_paths:
            self.expanded_paths = [p for p in self.expanded_paths if p != path]
        else:
            self.expanded_paths.append(path)

    @rx.event
    def select_key(self, key: str):
        self.selected_key = key
        from redis_browser.states.key_details_state import KeyDetailsState

        yield KeyDetailsState.fetch_key_details(key)

    @rx.event
    def set_filter_query(self, query: str):
        self.filter_query = query

    @rx.event(background=True)
    async def scan_keys(self):
        async with self:
            self.is_loading_keys = True
            self.keys = []
            self.expanded_paths = []
            self.selected_key = ""
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
            if not config:
                self.is_loading_keys = False
                return
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"] if config["password"] else None,
                db=config["db"],
                socket_timeout=5,
                decode_responses=True,
            )
            keys = []
            count = 0
            limit = 10000
            for key in r.scan_iter(match="*", count=100):
                keys.append(key)
                count += 1
                if count >= limit:
                    break
            async with self:
                self.keys = keys
        except Exception as e:
            logging.exception(f"Error scanning keys: {e}")
            async with self:
                yield rx.toast(f"Failed to scan keys: {str(e)}")
        finally:
            async with self:
                self.is_loading_keys = False