import os
import hashlib
import subprocess
from typing import Any, Dict, List
from tinytag import TinyTag

from .base import BaseMediaModule

LIBRARY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "library")

class RealMediaModule(BaseMediaModule):
    """Real implementation of media module to scan local files"""
    
    def __init__(self):
        super().__init__()
        # Create library folder if it doesn't exist
        if not os.path.exists(LIBRARY_PATH):
            os.makedirs(LIBRARY_PATH)
            
    def initialize(self) -> bool:
        self.update_state(status="ready", enabled=True)
        return True
        
    def shutdown(self) -> bool:
        return True
        
    def get_status(self) -> Dict[str, Any]:
        return self.state.model_dump()
        
    async def get_all_songs(self) -> List[Dict[str, Any]]:
        """Iterate over library directory and extract ID3 info using tinytag"""
        songs = []
        valid_extensions = (".mp3", ".m4a", ".flac")
        
        if not os.path.exists(LIBRARY_PATH):
            return songs
            
        for filename in os.listdir(LIBRARY_PATH):
            if filename.lower().endswith(valid_extensions):
                filepath = os.path.join(LIBRARY_PATH, filename)
                try:
                    tag = TinyTag.get(filepath)
                    
                    # Generate a simple ID based on filename hash
                    file_id = hashlib.md5(filename.encode()).hexdigest()[:8]
                    
                    title = tag.title if tag.title else os.path.splitext(filename)[0]
                    artist = tag.artist if tag.artist else "Unknown Artist"
                    duration = int(tag.duration) if tag.duration else 0
                    
                    songs.append({
                        "id": file_id,
                        "title": title,
                        "artist": artist,
                        "duration": duration,
                        "filename": filename,
                        "coverUrl": ""  # Placeholder for now
                    })
                except Exception as e:
                    print(f"Error reading tag for {filename}: {e}")
                    
        return songs
        
    def _get_filename_by_id(self, song_id: str) -> str | None:
        """Helper to find a filename from its ID hash"""
        if not os.path.exists(LIBRARY_PATH):
            return None
        valid_extensions = (".mp3", ".m4a", ".flac")
        for filename in os.listdir(LIBRARY_PATH):
            if filename.lower().endswith(valid_extensions):
                if hashlib.md5(filename.encode()).hexdigest()[:8] == song_id:
                    return filename
        return None
        
    async def delete_song(self, song_id: str) -> bool:
        """Delete a song by ID"""
        filename = self._get_filename_by_id(song_id)
        if not filename:
            return False
            
        filepath = os.path.join(LIBRARY_PATH, filename)
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            return False
            
    async def rename_song(self, song_id: str, new_name: str) -> bool:
        """Rename a song file by ID"""
        filename = self._get_filename_by_id(song_id)
        if not filename:
            return False
            
        ext = os.path.splitext(filename)[1]
        # Make sure the new name has the extension
        if not new_name.lower().endswith(ext.lower()):
            new_name += ext
            
        old_filepath = os.path.join(LIBRARY_PATH, filename)
        new_filepath = os.path.join(LIBRARY_PATH, new_name)
        
        try:
            os.rename(old_filepath, new_filepath)
            return True
        except Exception as e:
            print(f"Error renaming {filename} to {new_name}: {e}")
            return False
            
    async def trim_song(self, song_id: str, start_time: int, end_time: int) -> bool:
        """Trim a song using ffmpeg"""
        filename = self._get_filename_by_id(song_id)
        if not filename:
            return False
            
        filepath = os.path.join(LIBRARY_PATH, filename)
        name, ext = os.path.splitext(filename)
        temp_filepath = os.path.join(LIBRARY_PATH, f"{name}_trimmed{ext}")
        
        duration = end_time - start_time
        if duration <= 0:
            return False
            
        try:
            # Use ffmpeg to trim
            cmd = [
                "ffmpeg", "-y", "-i", filepath,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",
                temp_filepath
            ]
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode == 0:
                os.replace(temp_filepath, filepath)
                return True
            else:
                print(f"FFmpeg error: {process.stderr.decode()}")
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                return False
        except Exception as e:
            print(f"Error trimming {filename}: {e}")
            return False
