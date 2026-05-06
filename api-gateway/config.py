from pydantic import BaseModel

class EndpointConfig(BaseModel):
    # Movie Core endpoints
    movieCoreUrl: str = "http://movie-core:5000"
    # Recommendation Service endpoints
    recommendationUrl: str = "http://recommendation-svc:5000"
    # Enrichment Service endpoint
    enrichmentUrl: str = "http://enrichment-svc:5000"


def get_endpoint_config() -> EndpointConfig:
    return EndpointConfig()


