import asyncio
from typing import Any, Callable, Dict, Awaitable, List
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache
from aiogram.fsm.context import FSMContext


class UserTopicContext:
    def __init__(self):
        self.album: List[Message] = []


class AlbumsMiddleware(BaseMiddleware):
    def __init__(self, wait_time_seconds: int):
        super().__init__()
        self.wait_time_seconds = wait_time_seconds
        self.albums_cache = TTLCache(
            ttl=float(wait_time_seconds) + 20.0,
            maxsize=1000
        )
        self.lock = asyncio.Lock()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            print(f"{self.__class__.__name__} used not for Message, but for {type(event)}")
            return await handler(event, data)

        event: Message

        # If there is no media_group
        # just pass update further
        if event.media_group_id is None:
            return await handler(event, data)

        album_id: str = event.media_group_id

        async with self.lock:
            self.albums_cache.setdefault(album_id, [])
            self.albums_cache[album_id].append(event)

        # Wait for some time until other updates are collected
        await asyncio.sleep(self.wait_time_seconds)

        # Find the smallest message_id in batch, this will be our only update
        # which will pass to handlers
        my_message_id = smallest_message_id = event.message_id

        async with self.lock:
            if album_id in self.albums_cache:
                for item in self.albums_cache[album_id]:
                    smallest_message_id = min(smallest_message_id, item.message_id)

                # If current message_id is not the smallest, drop the update;
                # it's already saved in self.albums_cache
                if my_message_id != smallest_message_id:
                    return

                # If current message_id is the smallest,
                # add all other messages to data and pass to handler
                context: UserTopicContext = UserTopicContext()
                context.album = self.albums_cache.pop(album_id, [])

                # Save the context to FSMContext
                state: FSMContext = data.get('state')
                await state.update_data(context=context)

        return await handler(event, data)
