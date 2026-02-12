import reflex as rx
import redis
import logging
from typing import TypedDict, Optional


class RedisConfig(TypedDict):
    id: str
    name: str
    host: str
    port: int
    password: str
    db: int


class ConnectionState(rx.State):
    configs: list[RedisConfig] = [
        {
            "id": "default",
            "name": "Local Redis",
            "host": "localhost",
            "port": 6379,
            "password": "",
            "db": 0,
        }
    ]
    form_name: str = ""
    form_host: str = "localhost"
    form_port: int = 6379
    form_password: str = ""
    form_db: int = 0
    selected_id: str = ""
    is_connected: bool = False
    is_connecting: bool = False
    error_message: str = ""
    show_config_modal: bool = False
    editing_id: str = ""

    @rx.var
    def active_config(self) -> Optional[RedisConfig]:
        for config in self.configs:
            if config["id"] == self.selected_id:
                return config
        return None

    @rx.event
    def toggle_modal(self):
        self.show_config_modal = not self.show_config_modal
        if not self.show_config_modal:
            self.editing_id = ""
            self.reset_form()

    @rx.event
    def reset_form(self):
        self.form_name = ""
        self.form_host = "localhost"
        self.form_port = 6379
        self.form_password = ""
        self.form_db = 0

    @rx.event
    def select_connection(self, config_id: str):
        if self.is_connected:
            self.is_connected = False
        self.selected_id = config_id
        self.error_message = ""

    @rx.event
    def edit_config(self, config_id: str):
        self.editing_id = config_id
        for config in self.configs:
            if config["id"] == config_id:
                self.form_name = config["name"]
                self.form_host = config["host"]
                self.form_port = config["port"]
                self.form_password = config["password"]
                self.form_db = config["db"]
                self.show_config_modal = True
                break

    @rx.event
    def delete_config(self, config_id: str):
        self.configs = [c for c in self.configs if c["id"] != config_id]
        if self.selected_id == config_id:
            self.selected_id = ""
            self.is_connected = False

    @rx.event
    def save_config(self, form_data: dict):
        import uuid

        new_config: RedisConfig = {
            "id": self.editing_id if self.editing_id else str(uuid.uuid4()),
            "name": form_data.get("name", "Unnamed"),
            "host": form_data.get("host", "localhost"),
            "port": int(form_data.get("port", 6379)),
            "password": form_data.get("password", ""),
            "db": int(form_data.get("db", 0)),
        }
        if self.editing_id:
            self.configs = [
                new_config if c["id"] == self.editing_id else c for c in self.configs
            ]
        else:
            self.configs.append(new_config)
        self.show_config_modal = False
        self.editing_id = ""
        self.reset_form()

    @rx.event(background=True)
    async def connect_redis(self):
        async with self:
            if not self.selected_id:
                yield rx.toast("Please select a connection first")
                return
            self.is_connecting = True
            self.error_message = ""
            config = self.active_config
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"] if config["password"] else None,
                db=config["db"],
                socket_timeout=5,
                decode_responses=True,
            )
            r.ping()
            async with self:
                self.is_connected = True
                yield rx.toast(
                    f"Successfully connected to {config['name']}", position="top-right"
                )
                from redis_browser.states.key_browser_state import KeyBrowserState

                yield KeyBrowserState.scan_keys
        except Exception as e:
            logging.exception(f"Redis connection failed: {e}")
            async with self:
                self.is_connected = False
                self.error_message = str(e)
                yield rx.toast(f"Connection failed: {str(e)}", position="top-right")
        finally:
            async with self:
                self.is_connecting = False

    @rx.event
    def disconnect_redis(self):
        self.is_connected = False
        from redis_browser.states.key_details_state import KeyDetailsState

        yield KeyDetailsState.stop_watching
        yield rx.toast("Disconnected from Redis server")