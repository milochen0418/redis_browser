import reflex as rx
import redis
import logging
from typing import Any, Optional, Union
from redis_browser.states.connection_state import ConnectionState


class KeyDetailsState(rx.State):
    """Manages the detailed view and operations for a specific Redis key."""

    key_name: str = ""
    key_type: str = ""
    ttl: int = -1
    string_value: str = ""
    list_value: list[str] = []
    set_value: list[str] = []
    hash_value: dict[str, str] = {}
    zset_value: list[tuple[str, float]] = []
    is_loading: bool = False
    show_edit_modal: bool = False
    edit_field_name: str = ""
    edit_field_value: str = ""
    edit_score: float = 0.0

    @rx.event
    def set_show_edit_modal(self, show: bool):
        self.show_edit_modal = show

    @rx.var
    def ttl_display(self) -> str:
        if self.ttl == -1:
            return "No Expiry"
        if self.ttl == -2:
            return "Expired"
        hours = self.ttl // 3600
        minutes = self.ttl % 3600 // 60
        seconds = self.ttl % 60
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    @rx.event(background=True)
    async def fetch_key_details(self, key: str):
        async with self:
            self.is_loading = True
            self.key_name = key
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
            if not config or not key:
                self.is_loading = False
                return
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"] if config["password"] else None,
                db=config["db"],
                decode_responses=True,
            )
            k_type = r.type(key)
            ttl = r.ttl(key)
            s_val, l_val, set_val, h_val, z_val = ("", [], [], {}, [])
            if k_type == "string":
                s_val = r.get(key) or ""
            elif k_type == "list":
                l_val = r.lrange(key, 0, -1)
            elif k_type == "set":
                set_val = list(r.smembers(key))
                set_val.sort()
            elif k_type == "hash":
                h_val = r.hgetall(key)
            elif k_type == "zset":
                z_val = r.zrange(key, 0, -1, withscores=True)
            async with self:
                self.key_type = k_type
                self.ttl = ttl
                self.string_value = s_val
                self.list_value = l_val
                self.set_value = set_val
                self.hash_value = h_val
                self.zset_value = z_val
        except Exception as e:
            logging.exception(f"Error fetching key details: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def delete_key(self):
        async with self:
            key = self.key_name
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"],
                db=config["db"],
            )
            r.delete(key)
            async with self:
                self.key_name = ""
                from redis_browser.states.key_browser_state import KeyBrowserState

                yield KeyBrowserState.scan_keys
                yield rx.toast(f"Key '{key}' deleted")
        except Exception as e:
            logging.exception(f"Error deleting key: {e}")
            yield rx.toast(f"Delete failed: {str(e)}")

    @rx.event(background=True)
    async def update_string_value(self, form_data: dict):
        async with self:
            new_val = form_data.get("value", "")
            key = self.key_name
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"],
                db=config["db"],
                decode_responses=True,
            )
            r.set(key, new_val)
            async with self:
                self.show_edit_modal = False
                yield KeyDetailsState.fetch_key_details(key)
        except Exception as e:
            logging.exception(f"Error updating string value: {e}")
            yield rx.toast(f"Update failed: {str(e)}")

    @rx.event
    def open_edit_modal(self, field: str = "", value: str = "", score: float = 0.0):
        self.edit_field_name = field
        self.edit_field_value = value
        self.edit_score = score
        self.show_edit_modal = True

    @rx.event(background=True)
    async def set_hash_field(self, form_data: dict):
        async with self:
            field = form_data.get("field", self.edit_field_name)
            value = form_data.get("value", "")
            key = self.key_name
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"],
                db=config["db"],
                decode_responses=True,
            )
            r.hset(key, field, value)
            async with self:
                self.show_edit_modal = False
                yield KeyDetailsState.fetch_key_details(key)
        except Exception as e:
            logging.exception(f"Error setting hash field: {e}")
            yield rx.toast(f"Hash update failed: {str(e)}")

    @rx.event(background=True)
    async def delete_hash_field(self, field: str):
        async with self:
            key = self.key_name
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"],
                db=config["db"],
                decode_responses=True,
            )
            r.hdel(key, field)
            yield KeyDetailsState.fetch_key_details(key)
        except Exception as e:
            logging.exception(f"Error deleting hash field: {e}")
            yield rx.toast(f"Field delete failed: {str(e)}")