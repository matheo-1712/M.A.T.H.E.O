mod config;

fn main() -> anyhow::Result<()> {
    let config = config::Config::from_env()?;
    println!("Configuration chargée, chat_id = {}", config.chat_id);
    Ok(())
}
