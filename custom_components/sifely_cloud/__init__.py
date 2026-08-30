# __init__.py
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .token_manager import SifelyTokenManager
from .sifely import setup_sifely_coordinator
from .openapi_auth import is_sk_token, redact_secrets
from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CLIENT_ID,
    STARTUP_MESSAGE,
    SUPPORTED_PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Handle YAML setup (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle integration setup from config flow."""
    _LOGGER.info("📦 Setting up Sifely Cloud")

    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info(STARTUP_MESSAGE)

    # Extract credentials from config entry options
    email = entry.options.get(CONF_EMAIL)
    password = entry.options.get(CONF_PASSWORD)
    client_id = entry.options.get(CONF_CLIENT_ID)

    if not all([email, password, client_id]):
        _LOGGER.error("❌ Missing required credentials in config entry.")
        return False

    _LOGGER.info(
        "🔐 Initializing Sifely token manager for client_id: %s",
        redact_secrets(client_id) if is_sk_token(client_id) else client_id,
    )

    # Create and initialize token manager
    session = async_get_clientsession(hass)
    token_manager = SifelyTokenManager(
        client_id=client_id,
        email=email,
        password=password,
        session=session,
        hass=hass,
        config_entry=entry,
    )

    try:
        await token_manager.initialize()
        coordinator = await setup_sifely_coordinator(hass, token_manager, entry)
        _LOGGER.info("✅ Sifely token manager and coordinator initialized successfully.")
    except Exception as e:
        _LOGGER.exception("❌ Failed to initialize Sifely integration")
        return False

    # Store token manager and coordinator under entry ID
    hass.data[DOMAIN][entry.entry_id] = {
        "token_manager": token_manager,
        "coordinator": coordinator,
    }

    # ✅ Listen for config option updates
    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update by reloading the config entry."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_refresh_lock_list(hass: HomeAssistant):
    """Manually trigger a refresh of the lock list."""
    for entry_id, data in hass.data.get(DOMAIN, {}).items():
        coordinator = data.get("coordinator")
        if coordinator:
            await coordinator.async_fetch_lock_list()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, SUPPORTED_PLATFORMS)

    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, {})
        token_manager = data.get("token_manager")
        if token_manager:
            await token_manager.async_shutdown()

    return unload_ok
