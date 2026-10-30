from abc import ABC, abstractmethod

class BaseMusicSource(ABC):
    @property
    @abstractmethod
    def source_id(self) -> str:
        """Уникальный ID источника (site1, site2)"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Название для кнопки"""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 36) -> list[dict]:
        pass

    @abstractmethod
    async def download_audio(self, url: str) -> tuple[bytes, str] | None:
        """Скачивает аудио. Возвращает (байты, имя_файла)."""
        pass

    @abstractmethod
    async def download_cover(self, cover_url: str) -> bytes | None:
        """Скачивает обложку. Возвращает байты или None."""
        pass