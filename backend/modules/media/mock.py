from typing import Any, Dict, List
from .base import BaseMediaModule

class MockMediaModule(BaseMediaModule):
    """Mock implementation of media module with static data"""
    
    def initialize(self) -> bool:
        self.update_state(status="ready", enabled=True)
        return True
        
    def shutdown(self) -> bool:
        return True
        
    def get_status(self) -> Dict[str, Any]:
        return self.state.model_dump()
        
    async def get_all_songs(self) -> List[Dict[str, Any]]:
        """Return a static list of songs for testing"""
        return [
            {
                "id": "mock1",
                "title": "Midnight City",
                "artist": "M83",
                "duration": 244,
                "filename": "midnight.mp3",
                "coverUrl": ""
            },
            {
                "id": "mock2",
                "title": "Blinding Lights",
                "artist": "The Weeknd",
                "duration": 200,
                "filename": "blinding.mp3",
                "coverUrl": ""
            },
            {
                "id": "mock3",
                "title": "Get Lucky",
                "artist": "Daft Punk",
                "duration": 248,
                "filename": "getlucky.mp3",
                "coverUrl": ""
            }
        ]
