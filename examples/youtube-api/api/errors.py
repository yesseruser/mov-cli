from pydantic import BaseModel

__all__ = ("NoMetadata", "NoVideoToScrape", )

class NoMetadata(BaseModel):
    error: str
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "NoMetadata",
                    "message": "mov-cli-youtube didn't return any metadata"
                }
            ]
        }
    }

class NoVideoToScrape(BaseModel):
    error: str
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "NoVideoToScrape",
                    "message": "mov-cli-youtube didn't find any video with that ID to scrape."
                }
            ]
        }
    }