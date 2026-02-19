import asyncio
import logging

import httpx
from homeassistant_api import Client, Domain

class HaManager:

    logger = logging.getLogger(__package__)

    light_domain: Domain|None = None
    last_light_id: str|None = None

    def __init__(self, url, token):
        normalized_url = url.rstrip("/")
        if not normalized_url.endswith("/api"):
            normalized_url = f"{normalized_url}/api"
        self.api_url = normalized_url
        self.token = token
        self.client = Client(normalized_url, token)

    def _call_service(self, domain: str, service: str, data: dict):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.api_url}/services/{domain}/{service}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=data, headers=headers)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            self.logger.error("HA service call failed: %s", exc)

    def get_lights(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.api_url}/states"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            self.logger.error("HA get_lights failed: %s", exc)
            return []

        states = resp.json()
        lights = [state for state in states if state.get("entity_id", "").startswith("light.")]

        simplified = []
        for light in lights:
            entity_id = light.get("entity_id")
            state = light.get("state")
            attributes = light.get("attributes") or {}
            name = attributes.get("friendly_name") or entity_id
            simplified.append({
                "entity_id": entity_id,
                "state": state,
                "name": name,
            })

        return simplified

    def toggle_light(self, entity_id: str):
        self._call_service("light", "toggle", {"entity_id": entity_id})
        self.last_light_id = entity_id

    def _turn_on(self, **kwargs):
        if self.last_light_id is None:
            self.logger.warning("Tried to change brightness without setting light first")
            return
        # Refer to https://www.home-assistant.io/integrations/light/#action-lightturn_on
        data = {"entity_id": self.last_light_id, **kwargs}
        self._call_service("light", "turn_on", data)

    def increase_brightness(self):
        self._turn_on(brightness_step_pct=10)

    def decrease_brightness(self):
        self._turn_on(brightness_step_pct=-10)