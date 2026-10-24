import json
import logging
from typing import Callable, Awaitable

logger = logging.getLogger("pos_sync")


class POSSessionHub:
    """
    In-memory async session hub managing laptop POS and mobile scanner WebSocket channels.
    Allows real-time duplex communication without external message broker (e.g. Redis).
    """

    def __init__(self):
        # Maps session_id -> set of send functions for laptop sockets
        self._laptops: dict[str, set[Callable[[dict], Awaitable[None]]]] = {}
        # Maps session_id -> set of send functions for mobile sockets
        self._mobiles: dict[str, set[Callable[[dict], Awaitable[None]]]] = {}
        # Maps session_id -> set of processed event_ids for in-memory fast deduplication
        self._processed_events: dict[str, set[str]] = {}
        # Maps session_id -> mobile device information
        self._mobile_info: dict[str, str] = {}

    def is_mobile_connected(self, session_id: str) -> bool:
        return bool(self._mobiles.get(session_id))

    def is_laptop_connected(self, session_id: str) -> bool:
        return bool(self._laptops.get(session_id))

    def get_mobile_info(self, session_id: str) -> str:
        return self._mobile_info.get(session_id, "")

    async def register_laptop(self, session_id: str, send_fn: Callable[[dict], Awaitable[None]]):
        if session_id not in self._laptops:
            self._laptops[session_id] = set()
        self._laptops[session_id].add(send_fn)

        # Notify this laptop of current mobile connection status
        has_mobile = self.is_mobile_connected(session_id)
        await send_fn({
            "type": "connection_established",
            "role": "laptop",
            "session_id": session_id,
            "mobile_connected": has_mobile,
            "mobile_device_info": self.get_mobile_info(session_id) if has_mobile else None,
        })

        # Immediately notify mobile phone that laptop POS is active and ready
        await self.broadcast_to_mobile(session_id, {
            "type": "laptop_status",
            "status": "connected",
        })

    async def unregister_laptop(self, session_id: str, send_fn: Callable[[dict], Awaitable[None]]):
        if session_id in self._laptops:
            self._laptops[session_id].discard(send_fn)
            if not self._laptops[session_id]:
                del self._laptops[session_id]
                # Notify mobile that laptop is disconnected
                await self.broadcast_to_mobile(session_id, {
                    "type": "laptop_status",
                    "status": "disconnected",
                })

    async def register_mobile(
        self, session_id: str, send_fn: Callable[[dict], Awaitable[None]], device_info: str = ""
    ):
        if session_id not in self._mobiles:
            self._mobiles[session_id] = set()
        self._mobiles[session_id].add(send_fn)
        if device_info:
            self._mobile_info[session_id] = device_info

        # Notify mobile
        await send_fn({
            "type": "connection_established",
            "role": "mobile",
            "session_id": session_id,
            "laptop_connected": self.is_laptop_connected(session_id),
        })

        # Notify all connected laptop sockets for this session
        await self.broadcast_to_laptop(session_id, {
            "type": "mobile_status",
            "status": "connected",
            "device_info": device_info,
        })

    async def unregister_mobile(self, session_id: str, send_fn: Callable[[dict], Awaitable[None]]):
        if session_id in self._mobiles:
            self._mobiles[session_id].discard(send_fn)
            if not self._mobiles[session_id]:
                del self._mobiles[session_id]
                self._mobile_info.pop(session_id, None)
                # Notify laptop that mobile disconnected
                await self.broadcast_to_laptop(session_id, {
                    "type": "mobile_status",
                    "status": "disconnected",
                })

    async def broadcast_to_laptop(self, session_id: str, message: dict):
        receivers = list(self._laptops.get(session_id, []))
        for send_fn in receivers:
            try:
                await send_fn(message)
            except Exception as e:
                logger.warning(f"Failed to send to laptop socket: {e}")
                self._laptops[session_id].discard(send_fn)

    async def broadcast_to_mobile(self, session_id: str, message: dict):
        receivers = list(self._mobiles.get(session_id, []))
        for send_fn in receivers:
            try:
                await send_fn(message)
            except Exception as e:
                logger.warning(f"Failed to send to mobile socket: {e}")
                self._mobiles[session_id].discard(send_fn)

    def is_duplicate_event(self, session_id: str, event_id: str) -> bool:
        if session_id not in self._processed_events:
            self._processed_events[session_id] = set()
        if event_id in self._processed_events[session_id]:
            return True
        self._processed_events[session_id].add(event_id)
        # Cap set size to prevent memory leak
        if len(self._processed_events[session_id]) > 500:
            self._processed_events[session_id].pop()
        return False

    async def revoke_session(self, session_id: str):
        # Notify mobile
        await self.broadcast_to_mobile(session_id, {
            "type": "session_revoked",
            "message": "POS operator revoked pairing session.",
        })
        self._laptops.pop(session_id, None)
        self._mobiles.pop(session_id, None)
        self._mobile_info.pop(session_id, None)
        self._processed_events.pop(session_id, None)


# Singleton hub instance
hub = POSSessionHub()
