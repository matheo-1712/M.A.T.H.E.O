"""Vérifie l'adaptateur avec le vrai SDK et un transport sans réseau."""

import json
import os
import unittest
from unittest.mock import patch

from telegram import Bot
from telegram.request import BaseRequest

from matheo.channels import Channel, ChannelError
from matheo.channels.telegram import TelegramChannel, connect_bot

TOKEN = "123456:test-token"


class FakeRequest(BaseRequest):
    def __init__(self):
        self.opened = False
        self.calls = []
        self.failures = {}

    @property
    def read_timeout(self):
        return 5

    async def initialize(self):
        self.opened = True

    async def shutdown(self):
        self.opened = False

    async def do_request(self, url, method, request_data=None, **kwargs):
        endpoint = url.rsplit("/", 1)[-1]
        parameters = request_data.parameters if request_data else {}
        self.calls.append((endpoint, parameters))
        if endpoint in self.failures:
            code, description = self.failures[endpoint]
            return code, json.dumps({
                "ok": False, "error_code": code, "description": description
            }).encode()
        if endpoint == "getMe":
            result = {"id": 123456, "is_bot": True, "first_name": "Matheo"}
        elif endpoint == "sendMessage":
            result = {
                "message_id": 42, "date": 0,
                "chat": {"id": 789, "type": "private"},
                "text": parameters["text"],
            }
        else:
            raise AssertionError(f"Requête inattendue : {endpoint}")
        return 200, json.dumps({"ok": True, "result": result}).encode()


class TelegramChannelTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.request = FakeRequest()
        self.updates_request = FakeRequest()
        sdk_bot = Bot(TOKEN, request=self.request, get_updates_request=self.updates_request)
        factory = patch("matheo.channels.telegram.bot.Bot", return_value=sdk_bot)
        self.factory = factory.start()
        self.addCleanup(factory.stop)

    def assert_closed(self):
        self.assertFalse(self.request.opened)
        self.assertFalse(self.updates_request.opened)

    async def test_connect_send_and_close_through_common_interface(self):
        async with connect_bot(TOKEN) as telegram:
            channel: Channel = telegram
            self.assertTrue(self.request.opened)
            self.assertEqual(await channel.send_message("789", "Bonjour é 👋"), "42")
        self.assert_closed()
        self.assertEqual(self.request.calls[0][0], "getMe")
        self.assertEqual(self.request.calls[1], (
            "sendMessage", {"chat_id": "789", "text": "Bonjour é 👋"}
        ))

    async def test_resources_closed_when_application_fails(self):
        with self.assertRaisesRegex(RuntimeError, "erreur métier"):
            async with connect_bot(TOKEN):
                raise RuntimeError("erreur métier")
        self.assert_closed()

    async def test_rejected_token_is_hidden_and_resources_are_closed(self):
        self.request.failures["getMe"] = (401, "Unauthorized")
        with self.assertRaises(ChannelError) as caught:
            async with connect_bot(TOKEN):
                self.fail("La connexion aurait dû échouer.")
        self.assertNotIn(TOKEN, str(caught.exception))
        self.assertIn("[token masqué]", str(caught.exception))
        self.assert_closed()

    async def test_send_failure_is_translated_without_retry(self):
        self.request.failures["sendMessage"] = (403, "Forbidden: bot was blocked")
        with self.assertRaisesRegex(ChannelError, "blocked"):
            async with connect_bot(TOKEN) as channel:
                await channel.send_message("789", "Bonjour")
        self.assertEqual([call[0] for call in self.request.calls], ["getMe", "sendMessage"])
        self.assert_closed()

    async def test_invalid_input_does_not_send(self):
        channel = TelegramChannel(TOKEN)
        with self.assertRaises(ChannelError):
            await channel.send_message("789", "Bonjour")
        async with connect_bot(TOKEN) as channel:
            for recipient, text in (("", "Bonjour"), ("789", ""), ("789", "x" * 4097)):
                with self.subTest(recipient=recipient, length=len(text)):
                    with self.assertRaises(ValueError):
                        await channel.send_message(recipient, text)
        self.assertEqual([call[0] for call in self.request.calls], ["getMe"])

    async def test_token_from_environment_and_missing_configuration(self):
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": TOKEN}, clear=True):
            async with connect_bot():
                pass
        self.factory.assert_called_with(token=TOKEN)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "TELEGRAM_BOT_TOKEN"):
                async with connect_bot():
                    self.fail("Une configuration est requise.")


if __name__ == "__main__":
    unittest.main()
