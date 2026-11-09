//! Les tâches qui se lancent toutes seules, à heure fixe.

use chrono_tz::Europe::Paris;
use matheo_telegram::MessageManager;
use tokio_cron_scheduler::{Job, JobScheduler};

/// Crée le planificateur, y ajoute les tâches quotidiennes et le démarre.
pub async fn start(message_manager: MessageManager) -> anyhow::Result<JobScheduler> {
    let scheduler = JobScheduler::new().await?;

    // Format : seconde minute heure jour-du-mois mois jour-de-la-semaine
    // "0 0 8 * * *" = tous les jours à 08:00:00 (heure de Paris).
    let good_morning = Job::new_async_tz("0 0 8 * * *", Paris, move |_id, _scheduler| {
        let message_manager = message_manager.clone();
        Box::pin(async move {
            let text = "☀️ Bonjour ! Une nouvelle journée commence.";
            if let Err(error) = message_manager.send(text).await {
                log::error!("Message du matin non envoyé : {error}");
            }
        })
    })?;

    scheduler.add(good_morning).await?;
    scheduler.start().await?;
    Ok(scheduler)
}