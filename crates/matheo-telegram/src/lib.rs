//! Tout ce qui concerne Telegram : envoyer des messages et répondre aux commandes.

mod commands;

use teloxide::prelude::*;

/// Envoie des messages au propriétaire de l'assistant (toi).
///
/// C'est le seul type que les autres crates utilisent : elles n'ont pas
/// besoin de savoir que Telegram existe.
#[derive(Clone)]
pub struct MessageManager {
    bot: Bot,
    chat_id: ChatId,
}

impl MessageManager {
    /// Crée un `MessageManager` à partir du token du bot et de ton chat_id.
    pub fn new(token: String, chat_id: i64) -> MessageManager {
        MessageManager {
            bot: Bot::new(token),
            chat_id: ChatId(chat_id),
        }
    }

    /// Envoie un message texte sur ta conversation Telegram.
    pub async fn send(&self, texte: &str) -> anyhow::Result<()> {
        self.bot.send_message(self.chat_id, texte).await?;
        Ok(())
    }

    /// Écoute les commandes Telegram et y répond. Ne s'arrête qu'avec Ctrl+C.
    pub async fn listen_for_commands(self) {
        log::info!("En attente de messages Telegram…");
        commands::Command::repl(self.bot, commands::reply).await;
    }
}
