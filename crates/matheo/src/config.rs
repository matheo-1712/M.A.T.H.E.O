use anyhow::Context;
use std::env;
use std::net::SocketAddr;

/// Toute la configuration de l'assistant, lue depuis le fichier `.env`.
pub struct Config {
    pub telegram_token: String,
    pub chat_id: i64,
    pub api_addr: SocketAddr,
    pub api_key: String,
}

impl Config {
    /// Lit le fichier `.env` puis construit la configuration.
    pub fn from_env() -> anyhow::Result<Config> {
        // Charge le fichier .env dans les variables d'environnement.
        // `.ok()` = "si le fichier n'existe pas, ce n'est pas grave".
        dotenvy::dotenv().ok();


        /// =========================================
        /// Chargement des variables d'environnement
        /// =========================================
        let telegram_token =
            env::var("TELEGRAM_BOT_TOKEN").context("TELEGRAM_BOT_TOKEN manque dans .env")?;

        let chat_id = env::var("TELEGRAM_CHAT_ID")
            .context("TELEGRAM_CHAT_ID manque dans .env")?
            .parse()
            .context("TELEGRAM_CHAT_ID doit être un nombre")?;

        let api_addr = env::var("API_ADDR")
            .unwrap_or("127.0.0.1:3000".to_string())
            .parse()
            .context("API_ADDR doit ressembler à 127.0.0.1:3000")?;

        let api_key = env::var("API_KEY").context("API_KEY manque dans .env")?;

        Ok(Config {
            telegram_token,
            chat_id,
            api_addr,
            api_key,
        })
    }
}