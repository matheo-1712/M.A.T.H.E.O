mod config;

use matheo_telegram::Messager;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Affiche les logs de niveau "info" et plus graves dans le terminal.
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let config = config::Config::from_env()?;
    let messager = Messager::new(config.telegram_token, config.chat_id);

    messager.envoyer("🤖 M.A.T.H.E.O est en ligne !").await?;
    log::info!("Message de démarrage envoyé");

    Ok(())
}