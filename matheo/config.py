"""Chargement de la configuration commune à tous les canaux."""

from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_environment() -> None:
    """Charge le .env du projet sans écraser les variables déjà définies.

    Le chemin ne dépend pas du dossier de lancement choisi par PyCharm.
    utf-8-sig accepte aussi les fichiers UTF-8 avec BOM créés sous Windows.
    """
    load_dotenv(dotenv_path=ENV_FILE, override=False, encoding="utf-8-sig")
