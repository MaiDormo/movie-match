import requests
import json
from typing import Dict, Any

def get_docs_from_service(port: int, service_name: str) -> Dict[Any, Any]:
    """Fetch OpenAPI docs from a service"""
    try:
        response = requests.get(f"http://localhost:{port}/openapi.json", timeout=5)
        if response.status_code == 200:
            docs = response.json()
            return docs
        return None
    except requests.RequestException:
        print(f"Could not connect to service on port {port}")
        return None

def merge_openapi_docs():
    """Collect and merge OpenAPI documentation from all services"""
    
    # Define services with their categories and descriptions
    services = {
        # External API Adapters
        'omdb': {'port': 5001, 'category': 'Adapter', 'description': 'OMDB API Integration Service'},
        'streaming_availability': {'port': 5002, 'category': 'Adapter', 'description': 'Streaming Availability API Integration Service'},
        'tmdb': {'port': 5003, 'category': 'Adapter', 'description': 'TMDB API Integration Service'},
        'spotify': {'port': 5004, 'category': 'Adapter', 'description': 'Spotify API Integration Service'},
        'groq': {'port': 5007, 'category': 'Adapter', 'description': 'GROQ API Integration Service'},
        'youtube': {'port': 5009, 'category': 'Adapter', 'description': 'YouTube API Integration Service'},
        
        # Database Adapters
        'user_db': {'port': 5010, 'category': 'Adapter', 'description': 'User Database Operations Service'},
        'genres_db': {'port': 5015, 'category': 'Adapter', 'description': 'Genre Database Operations Service'},
        
        # Email Services
        'email_check': {'port': 5011, 'category': 'Adapter', 'description': 'Email Validation Service'},
        
        # Business Logic Services
        'movie_details': {'port': 5005, 'category': 'Business Logic', 'description': 'Movie Details Processing Service'},
        'movie_search': {'port': 5016, 'category': 'Business Logic', 'description': 'Movie Search Processing Service'},
        'valid_email': {'port': 5012, 'category': 'Business Logic', 'description': 'Email Validation Processing Service'},
        
        # Process Centric Services
        'user_registration': {'port': 5013, 'category': 'Process Centric', 'description': 'User Registration Orchestration Service'},
        'user_login': {'port': 5014, 'category': 'Process Centric', 'description': 'User Login Orchestration Service'},
        'movie_match': {'port': 5017, 'category': 'Process Centric', 'description': 'Movie Matching Orchestration Service'}
    }

    # Base OpenAPI specification
    merged_docs = {
        "openapi": "3.0.0",
        "info": {
            "title": "MovieMatch API Documentation",
            "description": "Combined API documentation for all MovieMatch services",
            "version": "1.0.0"
        },
        "paths": {},
        "components": {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "examples": {},
            "requestBodies": {},
            "headers": {},
            "securitySchemes": {},
            "links": {},
            "callbacks": {}
        },
        "tags": []
    }

    # Define architectural layers
    layers = {
        "Adapter": "Services that interact with external APIs",
        "Business Logic": "Core business logic services",
        "Process Centric": "High-level process orchestration services"
    }

    # Add layer tags first
    for layer_name, layer_desc in layers.items():
        merged_docs['tags'].append({
            "name": layer_name,
            "description": layer_desc
        })

    # Add service tags with layer references
    for service_name, service_info in services.items():
        merged_docs['tags'].append({
            "name": service_name,
            "description": service_info['description'],
            "x-layer": service_info['category']
        })

    # Add tag grouping metadata
    merged_docs["x-tagGroups"] = [
        {
            "name": "Adapter",
            "tags": [
                *[name for name, info in services.items() if info['category'] == 'Adapter']
            ]
        },
        {
            "name": "Business Logic",
            "tags": [
                *[name for name, info in services.items() if info['category'] == 'Business Logic']
            ]
        },
        {
            "name": "Process Centric",
            "tags": [
                *[name for name, info in services.items() if info['category'] == 'Process Centric']
            ]
        }
    ]

    # Collect docs from each service
    for service_name, service_info in services.items():
        service_docs = get_docs_from_service(service_info['port'], service_name)
        if service_docs:
            print(f"Retrieved docs from {service_name}")
            
            # Add both layer and service tags to each operation
            for path in service_docs.get('paths', {}).values():
                for operation in path.values():
                    # Tag with both layer and service
                    operation['tags'] = [service_info['category'], service_name]
                    if 'operationId' in operation:
                        operation['operationId'] = f"{service_name}_{operation['operationId']}"

            # Merge paths with service prefix
            for path, operations in service_docs.get('paths', {}).items():
                new_path = f"/{service_name}{path}"
                merged_docs['paths'][new_path] = operations

            # Merge components
            for component_type in merged_docs['components']:
                if component_type in service_docs.get('components', {}):
                    merged_docs['components'][component_type].update(
                        service_docs['components'][component_type]
                    )

    # Write merged documentation to file
    with open('combined_api_docs.json', 'w') as f:
        json.dump(merged_docs, f, indent=2)

    print("\nAPI documentation has been merged and saved to 'combined_api_docs.json'")

if __name__ == "__main__":
    merge_openapi_docs()