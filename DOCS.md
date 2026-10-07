# M.A.T.H.E.O — assistant personnel

Base Python 3.14+ organisée par canaux de communication. Le canal Telegram
utilise [python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/),
qui gère les appels API, les connexions HTTP et les erreurs Telegram.

## Organisation

```text
main.py                         # Point d'entrée et choix du canal
matheo/
  config.py                     # Charge le .env à la racine du projet
  channels/
    base.py                     # Contrat Channel et erreur ChannelError
    telegram/
      __init__.py               # Expose TelegramChannel et connect_bot
      bot.py                    # Connexion, envoi et fermeture via le SDK
```

`Channel` définit trois méthodes asynchrones : `connect()`,
`send_message(recipient, text)` et `disconnect()`. L'envoi renvoie un identifiant
sous forme de chaîne ; aucun objet du SDK Telegram ne sort de l'adaptateur.
La future logique de l'assistant pourra dépendre de cette interface, tandis que
chaque nouveau canal aura son propre dossier dans `matheo/channels/`.

Cette première base gère la connexion et l'envoi. La réception des messages,
le moteur de l'assistant et les actions domotiques restent à ajouter.
Leur logique métier devra rester indépendante des canaux.

## Installation

```powershell
uv sync --locked
```

La dépendance est déclarée dans `pyproject.toml`, avec les versions résolues dans
`uv.lock`. Sans uv : `python -m pip install -e .`.

## Configuration

Créer le bot avec [@BotFather](https://t.me/BotFather), récupérer le token,
puis ouvrir sa conversation et lui envoyer `/start`.

Créer un fichier `.env` à la racine du projet, à côté de `main.py` et de
`pyproject.toml`, en utilisant `.env.example` comme modèle :

```dotenv
TELEGRAM_BOT_TOKEN=votre_token
TELEGRAM_CHAT_ID=123456789
```

`main.py` charge ce fichier avec `python-dotenv`, même si PyCharm utilise un
autre dossier de lancement. `TELEGRAM_CHAT_ID` est facultatif pour simplement
vérifier la connexion. Les variables déjà définies dans l'environnement restent
prioritaires sur le fichier `.env`.

Il est également possible de définir les variables dans PowerShell ou dans la
configuration d'exécution PyCharm :

```powershell
$env:TELEGRAM_BOT_TOKEN = "votre_token"
$env:TELEGRAM_CHAT_ID = "123456789"
```

Pour retrouver le `chat_id` après `/start`, définir le token dans la session
PowerShell avec la commande ci-dessus, puis exécuter :

```powershell
$updates = Invoke-RestMethod -Uri "https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/getUpdates"
$updates.result.message.chat | Select-Object id, first_name, title -Unique
```

Choisir la conversation souhaitée. Si la liste est vide, envoyer un nouveau
message puis réessayer. Cette commande suppose qu'aucun webhook ni autre
programme ne récupère déjà les messages du bot.

Les variables PowerShell sont valables pour la session en cours. Le fichier
`.env` est ignoré par Git ; le token ne doit pas être versionné.

## Lancement

```powershell
# Vérifier les identifiants et fermer la connexion
uv run main.py

# Envoyer un message
uv run main.py "Bonjour depuis M.A.T.H.E.O !"

# Choisir une autre conversation
uv run main.py --chat-id "123456789" "Bonjour !"
```

Dans PyCharm, utiliser l'interpréteur `.venv` du projet et exécuter `main.py`.

## Utilisation depuis Python

```python
import asyncio

from matheo.channels import Channel, ChannelError
from matheo.channels.telegram import connect_bot
from matheo.config import load_environment


async def notify(channel: Channel, recipient: str, text: str) -> str:
    # Cette fonction fonctionne avec tout canal respectant le contrat Channel.
    return await channel.send_message(recipient, text)


async def main() -> None:
    load_environment()
    try:
        async with connect_bot() as channel:
            message_id = await notify(channel, "123456789", "Bonjour !")
            print(message_id)
    except (ValueError, ChannelError) as error:
        print(f"Erreur : {error}")


asyncio.run(main())
```

`connect_bot(token="...")` accepte aussi un token explicite. Le bloc `async with`
valide le token à l'entrée et ferme les connexions à la sortie, y compris si le
code du bloc échoue. Garder le bloc ouvert pour plusieurs envois. Dans une
application déjà asynchrone, utiliser directement `await` / `async with`, sans
créer une seconde boucle avec `asyncio.run()`.

Les délais réseau sont ceux du SDK. Les erreurs Telegram sont converties en
`ChannelError`, avec le token masqué dans leur texte. Le texte envoyé est brut
et limité à 4096 caractères. Aucun renvoi automatique n'est ajouté : après un
délai dépassé, vérifier la conversation avant de renvoyer le message.

## Vérification locale

```powershell
uv run python -m unittest discover -s tests -v
```

Les tests utilisent le vrai SDK avec un transport simulé, sans token réel et
sans envoyer de message sur Telegram.
