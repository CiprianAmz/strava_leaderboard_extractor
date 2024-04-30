from abc import abstractmethod

from discord import Client


class AthletePet(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    async def on_ready(self):
        pass

    @abstractmethod
    async def on_message(self, message):
        pass
