mod config;

use matheo_telegram::MessageManager;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Affiche les logs de niveau "info" et plus graves dans le terminal.
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let config = config::Config::from_env()?;
    let message_manager = MessageManager::new(config.telegram_token, config.chat_id);

    let message = format!(
        "M.A.T.H.E.O est en ligne !\nVersion : {}",
        env!("CARGO_PKG_VERSION"),
    );

    message_manager.send(&message).await?;
    log::info!("{}", &message);
    matheo_api::start(config.api_addr, message_manager.clone(), config.api_key).await?;
    message_manager.listen_for_commands().await;

    Ok(())
}
