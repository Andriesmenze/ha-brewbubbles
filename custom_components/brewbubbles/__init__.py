from __future__ import annotations
from .const import DOMAIN

async def async_setup_entry(hass, entry):
    # We'll add coordinator + platforms next
    return True

async def async_unload_entry(hass, entry):
    return True
