"""Contrat d'envoi indépendant de Telegram et de ses objets SDK."""

from typing import Protocol


class ChannelError(RuntimeError):
    """Échec d'une opération sur un canal de communication."""


class Channel(Protocol):
    """Interface minimale à implémenter par chaque futur canal.

    Les destinataires et les identifiants de message sont propres à chaque
    canal. Le cœur de l'assistant les manipule comme des chaînes opaques.
    """

    async def connect(self) -> None:
        """Ouvre les ressources et vérifie les identifiants du canal."""
        ...

    async def send_message(self, recipient: str, text: str) -> str:
        """Envoie du texte et renvoie l'identifiant du message."""
        ...

    async def disconnect(self) -> None:
        """Libère les ressources réseau du canal."""
        ...
