import logging
from typing import Any

import requests

class HaManager:

    logger = logging.getLogger(__package__)

    last_light_id: str|None = None

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        normalized = url.strip().rstrip("/")
        if not normalized.endswith("/api"):
            normalized = f"{normalized}/api"
        return normalized

    def __init__(self, url, token):
        self.base_url = self._normalize_base_url(url)
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None):
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            if not response.content:
                return None
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"HA request failed for {method} {url}: {e}")
            return None

    def get_lights(self):
        states = self._request("GET", "/states")
        if not isinstance(states, list):
            return []

        lights: list[str] = []
        for state in states:
            if isinstance(state, dict):
                entity_id = state.get("entity_id")
                if isinstance(entity_id, str) and entity_id.startswith("light."):
                    lights.append(entity_id)
        return lights

    def _domain_from_entity(self, entity_id: str) -> str | None:
        if not entity_id or "." not in entity_id:
            self.logger.warning(f"Invalid entity id: {entity_id}")
            return None
        return entity_id.split(".", 1)[0]

    def _call_entity_service(self, entity_id: str, service: str, **kwargs):
        domain_name = self._domain_from_entity(entity_id)
        if domain_name is None:
            return

        payload = {"entity_id": entity_id, **kwargs}
        self._request("POST", f"/services/{domain_name}/{service}", payload)

    def call_service(self, service_name: str, data: dict | None = None):
        if not service_name or "." not in service_name:
            self.logger.error(f"Invalid service name '{service_name}'. Expected format 'domain.service'")
            return

        domain_name, service = service_name.split(".", 1)
        if not domain_name or not service:
            self.logger.error(f"Invalid service name '{service_name}'. Expected format 'domain.service'")
            return

        self._request("POST", f"/services/{domain_name}/{service}", data or {})

    def toggle_light(self, entity_id: str):
        self.toggle_entity(entity_id)

    def toggle_entity(self, entity_id: str):
        self._call_entity_service(entity_id, "toggle")
        self.last_light_id = entity_id

    def turn_on_entity(self, entity_id: str):
        self._call_entity_service(entity_id, "turn_on")
        self.last_light_id = entity_id

    def turn_off_entity(self, entity_id: str):
        self._call_entity_service(entity_id, "turn_off")
        self.last_light_id = entity_id

    def _turn_on(self, entity_id: str | None = None, **kwargs):
        if entity_id is not None:
            self.last_light_id = entity_id

        if self.last_light_id is None:
            self.logger.warning("Tried to change brightness without setting light first")
            return

        self._call_entity_service(self.last_light_id, "turn_on", **kwargs)

    def increase_brightness(self, entity_id: str | None = None):
        self._turn_on(entity_id=entity_id, brightness_step_pct=10)

    def decrease_brightness(self, entity_id: str | None = None):
        self._turn_on(entity_id=entity_id, brightness_step_pct=-10)