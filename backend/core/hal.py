from typing import Type, Dict, Any, Optional
import os

from core.config import get_settings


class HALFactory:
    """
    Hardware Abstraction Layer Factory.
    Automatically loads real or mock implementations based on HAL_MODE.
    """
    
    _instances: Dict[str, Any] = {}
    _initialized = False
    
    @classmethod
    def get_module(cls, module_name: str) -> Any:
        """
        Get a module instance (real or mock) based on HAL mode.
        
        Args:
            module_name: Name of the module (e.g., 'audio', 'bluetooth', 'wifi')
            
        Returns:
            Module instance (real implementation on Pi, mock on macOS)
        """
        settings = get_settings()
        hal_mode = settings.hal_mode
        
        if module_name in cls._instances:
            return cls._instances[module_name]
        
        module = cls._load_module(module_name, hal_mode)
        cls._instances[module_name] = module
        return module
    
    @classmethod
    def _load_module(cls, module_name: str, hal_mode: str) -> Any:
        """Load the appropriate module implementation"""
        try:
            if hal_mode == "real":
                if module_name == "audio":
                    from modules import audio as audio_module
                    real_module = getattr(audio_module, "RealAudioModule", None)
                    if real_module:
                        return real_module()
                        
                if module_name == "media":
                    from modules.media import RealMediaModule
                    return RealMediaModule()
            else:
                # Mock mode (development on macOS)
                if module_name == "audio":
                    from modules import audio as audio_module
                    mock_module = getattr(audio_module, "MockAudioModule", None)
                    if mock_module:
                        return mock_module()
                        
                # Also check media
                if module_name == "media":
                    from modules.media import RealMediaModule
                    return RealMediaModule()
                    
                # Also check bluetooth, wifi, etc.
                if module_name == "bluetooth":
                    from modules import bluetooth
                    mock = getattr(bluetooth, "MockBluetoothModule", None)
                    if mock:
                        return mock()
                elif module_name == "wifi":
                    from modules import wifi
                    mock = getattr(wifi, "MockWiFiModule", None)
                    if mock:
                        return mock()
                elif module_name == "obd":
                    from modules.obd import placeholder
                    return placeholder.OBDPlaceholder()
                elif module_name == "airplay":
                    from modules.airplay import placeholder
                    return placeholder.AirPlayPlaceholder()
                elif module_name == "map":
                    from modules.map import placeholder
                    return placeholder.MapPlaceholder()
                        
        except ImportError as e:
            print(f"Warning: Could not load module '{module_name}': {e}")
            return None
        
        return None
    
    @classmethod
    def initialize_all(cls) -> Dict[str, bool]:
        """
        Initialize all registered modules.
        
        Returns:
            Dictionary mapping module names to initialization success status
        """
        results = {}
        for name in ["audio", "bluetooth", "wifi", "obd", "airplay", "map", "media"]:
            try:
                module = cls.get_module(name)
                if module:
                    results[name] = module.initialize()
                else:
                    results[name] = False
            except Exception as e:
                print(f"Error initializing module '{name}': {e}")
                results[name] = False
        cls._initialized = True
        return results
    
    @classmethod
    def shutdown_all(cls) -> None:
        """Shutdown all modules gracefully"""
        for module in cls._instances.values():
            if module and hasattr(module, "shutdown"):
                try:
                    module.shutdown()
                except Exception as e:
                    print(f"Error shutting down module: {e}")
        cls._instances.clear()
        cls._initialized = False


def get_module(module_name: str) -> Any:
    """Convenience function to get a module"""
    return HALFactory.get_module(module_name)