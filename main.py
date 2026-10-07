"""Point d'entrée pour vérifier le bot ou envoyer un message."""

import argparse
import asyncio
import os
import sys

from matheo.channels import ChannelError
from matheo.channels.telegram import connect_bot
from matheo.config import load_environment


async def run(message: str | None, recipient: str | None) -> None:
    async with connect_bot() as channel:
        print("Bot connecté.")
        if message is not None:
            if recipient is None:
                raise ValueError("Le destinataire est obligatoire pour envoyer un message.")
            message_id = await channel.send_message(recipient, message)
            print(f"Message envoyé (id : {message_id}).")


def main() -> int:
    load_environment()
    parser = argparse.ArgumentParser(description="Connexion et envoi via Telegram.")
    parser.add_argument("message", nargs="?", help="Texte à envoyer (facultatif).")
    parser.add_argument("--chat-id", default=os.getenv("TELEGRAM_CHAT_ID"))
    args = parser.parse_args()
    if args.message is not None and not args.chat_id:
        parser.error("Indiquez --chat-id ou la variable TELEGRAM_CHAT_ID.")

    try:
        asyncio.run(run(args.message, args.chat_id))
    except (ValueError, ChannelError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
