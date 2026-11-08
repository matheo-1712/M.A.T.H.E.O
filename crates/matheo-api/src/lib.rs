//! L'API HTTP : une seule route, `POST /notify`.
//! Commande de test : `curl -X POST http://localhost:3000/notify -H "x-api-key: API_KEY" -H "Content-Type: application/json" -d '{"message": "Ceci est un test."}'`

use axum::{
    Json, Router,
    extract::State,
    http::{HeaderMap, StatusCode},
    routing::post,
};
use matheo_telegram::MessageManager;
use serde::Deserialize;
use std::net::SocketAddr;

/// Ce dont la route a besoin pour travailler. Partagé entre toutes les requêtes.
#[derive(Clone)]
struct AppState {
    message_manager: MessageManager,
    api_key: String,
}

/// Le JSON attendu dans le corps de la requête.
#[derive(Deserialize)]
struct Notification {
    title: Option<String>,
    message: String,
}

/// Réserve le port, puis lance le serveur en arrière-plan.
pub async fn start(addr: SocketAddr, message_manager: MessageManager, api_key: String) -> anyhow::Result<()> {
    let listener = tokio::net::TcpListener::bind(addr).await?;
    let app = router(message_manager, api_key);
    log::info!("API en écoute sur http://{addr}");

    tokio::spawn(async move {
        if let Err(error) = axum::serve(listener, app).await {
            log::error!("L'API s'est arrêtée : {error}");
        }
    });
    Ok(())
}

/// Construit le routeur : une seule route, POST /notify.
fn router(message_manager: MessageManager, api_key: String) -> Router {
    Router::new()
        .route("/notify", post(notify))
        .with_state(AppState { message_manager, api_key })
}

/// Reçoit une notification et la transfère sur Telegram.
async fn notify(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(notif): Json<Notification>,
) -> StatusCode {
    // 1. Vérifier la clé secrète envoyée dans l'en-tête "x-api-key".
    let received_key = headers.get("x-api-key").and_then(|v| v.to_str().ok());
    if received_key != Some(state.api_key.as_str()) {
        return StatusCode::UNAUTHORIZED; // 401
    }

    // 2. Construire le texte.
    let text = match notif.title {
        Some(title) => format!("📬 {title}\n\n{}", notif.message),
        None => format!("📬 {}", notif.message),
    };

    // 3. L'envoyer sur Telegram.
    match state.message_manager.send(&text).await {
        Ok(()) => StatusCode::OK, // 200
        Err(error) => {
            log::error!("Envoi Telegram impossible : {error}");
            StatusCode::BAD_GATEWAY // 502
        }
    }
}