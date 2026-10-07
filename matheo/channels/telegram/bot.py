"""Adaptation du SDK Telegram au contrat de communication de M.A.T.H.E.O."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from telegram import Bot
from telegram.constants import MessageLimit
from telegram.error import TelegramError

from matheo.channels.base import ChannelError


class TelegramChannel:
    """Canal asynchrone à utiliser dans une même boucle asyncio.

    Connecter avant les envois et déconnecter après leur achèvement.
    connect_bot() gère automatiquement ce cycle de vie.
    """

    def __init__(self, token: str) -> None:
        self._token = token.strip()
        if not self._token or any(char.isspace() for char in self._token):
            raise ValueError("Le token Telegram est vide ou contient des espaces.")
        try:
            self._bot = Bot(token=self._token)
        except TelegramError as error:
            raise self._error("Configuration", error) from None
        self._connected = False

    def _error(self, operation: str, error: TelegramError) -> ChannelError:
        description = str(error).replace(self._token, "[token masqué]")
        return ChannelError(f"{operation} Telegram : {description}")

    async def connect(self) -> None:
        """Initialise le SDK et vérifie le token avec getMe."""
        if self._connected:
            return
        try:
            # Le gestionnaire du SDK nettoie aussi une initialisation échouée.
            await self._bot.__aenter__()
        except TelegramError as error:
            raise self._error("Connexion", error) from None
        self._connected = True

    async def disconnect(self) -> None:
        """Ferme les connexions HTTP après les envois en cours."""
        if not self._connected:
            return
        try:
            await self._bot.shutdown()
        except TelegramError as error:
            raise self._error("Déconnexion", error) from None
        self._connected = False

    async def send_message(self, recipient: str | int, text: str) -> str:
        """Envoie du texte brut à un chat_id ou @canal et renvoie son ID."""
        if not self._connected:
            raise ChannelError("Connectez le canal Telegram avant d'envoyer un message.")
        if not isinstance(recipient, (str, int)) or not str(recipient).strip():
            raise ValueError("Le destinataire Telegram est obligatoire.")
        if not text.strip() or len(text) > MessageLimit.MAX_TEXT_LENGTH:
            raise ValueError("Le message doit contenir entre 1 et 4096 caractères.")
        try:
            message = await self._bot.send_message(chat_id=recipient, text=text)
        except TelegramError as error:
            raise self._error("Envoi", error) from None
        return str(message.message_id)


@asynccontextmanager
async def connect_bot(token: str | None = None) -> AsyncIterator[TelegramChannel]:
    """Connecte le bot et ferme ses ressources à la sortie du bloc async with.

    Lit TELEGRAM_BOT_TOKEN si aucun token n'est passé explicitement.
    """
    if token is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token.strip():
        raise ValueError("Définissez TELEGRAM_BOT_TOKEN ou passez token à connect_bot().")
    channel = TelegramChannel(token)
    await channel.connect()
    try:
        yield channel
    finally:
        await channel.disconnect()
