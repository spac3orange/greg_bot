from aiogram.filters import BaseFilter
from aiogram.types import ContentType, Message


class CTFilter(BaseFilter):
    def __init__(self):
        self.allowed_types = [ContentType.PHOTO, ContentType.VIDEO]

    def __call__(self, message: Message):
        print(message.content_type)
        return message.content_type in self.allowed_types
