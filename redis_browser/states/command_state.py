import reflex as rx
import redis
import logging
import datetime
import shlex
from typing import Any, Optional, TypedDict
from redis_browser.states.connection_state import ConnectionState


class LogEntry(TypedDict):
    timestamp: str
    command: str
    output: str
    status: str


class CommandState(rx.State):
    command_input: str = ""
    logs: list[LogEntry] = []
    is_executing: bool = False
    command_history: list[str] = []
    history_index: int = -1

    @rx.event
    def set_command_input(self, value: str):
        self.command_input = value

    @rx.event
    def clear_logs(self):
        self.logs = []

    @rx.event(background=True)
    async def execute_command(self, form_data: dict[str, Any]):
        async with self:
            cmd_str = form_data.get("command", "").strip()
            if not cmd_str:
                return
            self.is_executing = True
            if not self.command_history or self.command_history[-1] != cmd_str:
                self.command_history.append(cmd_str)
            self.history_index = -1
            connection_state = await self.get_state(ConnectionState)
            config = connection_state.active_config
            if not config or not connection_state.is_connected:
                self.logs.insert(
                    0,
                    {
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "command": cmd_str,
                        "output": "Error: No active connection.",
                        "status": "error",
                    },
                )
                self.command_input = ""
                self.is_executing = False
                return
        try:
            parts = shlex.split(cmd_str)
            if not parts:
                async with self:
                    self.is_executing = False
                return
            command_name = parts[0]
            args = parts[1:]
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=config["password"] if config["password"] else None,
                db=config["db"],
                socket_timeout=5,
                decode_responses=True,
            )
            result = r.execute_command(command_name, *args)
            formatted_output = str(result)
            if result is None:
                formatted_output = "(nil)"
            elif isinstance(result, list):
                pass
            async with self:
                self.logs.insert(
                    0,
                    {
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "command": cmd_str,
                        "output": formatted_output,
                        "status": "success",
                    },
                )
                read_only = [
                    "get",
                    "hget",
                    "lrange",
                    "smembers",
                    "zrange",
                    "ttl",
                    "type",
                    "info",
                    "ping",
                    "scan",
                    "keys",
                ]
                if command_name.lower() not in read_only:
                    from redis_browser.states.key_browser_state import KeyBrowserState

                    yield KeyBrowserState.scan_keys
                    from redis_browser.states.key_details_state import KeyDetailsState

                    selected_key = await self.get_state(KeyBrowserState)
                    if selected_key.selected_key:
                        yield KeyDetailsState.fetch_key_details(
                            selected_key.selected_key
                        )
        except Exception as e:
            logging.exception(f"Error executing Redis command: {e}")
            async with self:
                self.logs.insert(
                    0,
                    {
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "command": cmd_str,
                        "output": f"Error: {str(e)}",
                        "status": "error",
                    },
                )
        finally:
            async with self:
                self.command_input = ""
                self.is_executing = False