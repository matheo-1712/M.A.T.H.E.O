use teloxide::{prelude::*, utils::command::BotCommands};

/// Voici ce que je sais faire :
#[derive(BotCommands, Clone)]
#[command(rename_rule = "lowercase")]
pub enum Command {
    /// Dire bonjour.
    Start,
    /// Afficher cette aide.
    Help,
    /// Vérifier que je suis réveillé.
    Ping,
    /// Afficher l'identifiant de cette conversation.
    Id,
}

/// Appelée automatiquement à chaque commande reçue sur Telegram.
pub async fn reply(bot: Bot, msg: Message, cmd: Command) -> ResponseResult<()> {
    let text = match cmd {
        Command::Start => "Salut ! Je suis M.A.T.H.E.O, ton assistant. Tape /help.".to_string(),
        Command::Help => Command::descriptions().to_string(),
        Command::Ping => "Pong ! 🏓".to_string(),
        Command::Id => format!("Ton chat_id est : {}", msg.chat.id),
    };

    bot.send_message(msg.chat.id, text).await?;
    Ok(())
}