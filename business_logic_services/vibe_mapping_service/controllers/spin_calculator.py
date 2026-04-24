import random
from typing import List, Tuple

def get_random_sort(config: dict) -> str:
    """
    Get a random sort option from config.
    
    Args:
        config: Full YAML config dict
    
    Returns:
        Random sort option string
    """
    sort_options = config.get("spin", {}).get("sort_options", ["popularity.desc"])
    return random.choice(sort_options)

def get_random_page(config: dict) -> int:
    """
    Get a random page number from config range.
    
    Args:
        config: Full YAML config dict
    
    Returns:
        Random page number
    """
    page_range = config.get("spin", {}).get("page_range", [1, 3])
    return random.randint(page_range[0], page_range[1])

def get_default_limit(config: dict) -> int:
    """
    Get default limit from config.
    
    Args:
        config: Full YAML config dict
    
    Returns:
        Default limit integer
    """
    return config.get("spin", {}).get("default_limit", 10)

def get_spin_params(config: dict) -> Tuple[str, int, int]:
    """
    Get all spin parameters.
    
    Args:
        config: Full YAML config dict
    
    Returns:
        Tuple of (sort_by, page, limit)
    """
    return (
        get_random_sort(config),
        get_random_page(config),
        get_default_limit(config)
    )
