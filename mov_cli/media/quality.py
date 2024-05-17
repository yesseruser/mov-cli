from enum import Enum

__all__ = ("Quality", )

class Quality(Enum):
    SD = 480
    HD = 720
    FHD = 1080
    UHD = 2160

    def apply_p(self) -> str:
        """Returns that enum but with an ending p."""
        return f"{self.value}p"
    
    @classmethod
    def exists(enum, name: str) -> bool:
        """Checks if enum exists. Returns bool"""
        return name in enum.__members__