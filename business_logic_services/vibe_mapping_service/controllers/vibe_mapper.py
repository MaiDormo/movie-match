import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_PATH = Path(__file__).parent.parent / "config" / "vibe_mappings.yaml"

def load_config() -> Dict[str, Any]:
    """Load vibe mappings from YAML config file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
def get_vibe(vibe_name: str) -> Optional[Dict[str, Any]]:
    """
    Get vibe mapping by name.
    
    Args:
        vibe_name: Name of the vibe (e.g., "exciting", "romantic")
    
    Returns:
        Dict with vibe data or None if not found
    """
    config = load_config()
    return config.get("vibes", {}).get(vibe_name.lower())
def get_genres(vibe_name: str) -> Optional[List[int]]:
    """
    Get genre IDs for a given vibe.
    
    Args:
        vibe_name: Name of the vibe
    
    Returns:
        List of TMDB genre IDs or None if vibe not found
    """
    vibe = get_vibe(vibe_name)
    return vibe.get("genres") if vibe else None
def list_vibes() -> List[Dict[str, Any]]:
    """
    List all available vibes.
    
    Returns:
        List of vibe objects with name, description, genres
    """
    config = load_config()
    vibes = config.get("vibes", {})
    return [
        {
            "name": name,
            "description": data.get("description"),
            "genres": data.get("genres")
        }
        for name, data in vibes.items()
    ]
def is_valid_vibe(vibe_name: str) -> bool:
    """
    Check if a vibe name is valid.
    
    Args:
        vibe_name: Name of the vibe
    
    Returns:
        True if vibe exists, False otherwise
    """
    return get_vibe(vibe_name) is not None
