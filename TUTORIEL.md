# Construire M.A.T.H.E.O en Rust — tutoriel pas à pas

Objectif : un **assistant du quotidien** qui :

1. te **parle sur Telegram** et répond à des commandes (`/ping`, `/aide`…) ;
2. expose **une API** (une route HTTP `POST /notify`) pour que d'autres programmes lui envoient des infos, qu'il te transfère sur Telegram ;
3. lance des **tâches quotidiennes** (ex. : un message chaque matin à 8 h).

Le projet est organisé en **workspace Cargo** : chaque grande fonctionnalité vit dans sa propre **crate**. On part de zéro en Rust. Chaque étape ajoute **une fonctionnalité**, et le programme marche à la fin de chaque étape. Ne saute pas d'étape : chacune explique les notions Rust dont la suivante a besoin.

> Le code final de ce tutoriel a été compilé et testé avec Rust 1.99 et les versions de bibliothèques indiquées à l'étape 3.

---

## Sommaire

- [Étape 0 — Les outils](#étape-0--les-outils)
- [Étape 1 — Rust en 15 minutes](#étape-1--rust-en-15-minutes)
- [Étape 2 — Créer le bot sur Telegram](#étape-2--créer-le-bot-sur-telegram)
- [Étape 3 — Comprendre et préparer le workspace](#étape-3--comprendre-et-préparer-le-workspace)
- [Étape 4 — Lire la configuration (crate `matheo`)](#étape-4--lire-la-configuration-crate-matheo)
- [Étape 5 — Crate `matheo-telegram` : envoyer un premier message](#étape-5--crate-matheo-telegram--envoyer-un-premier-message)
- [Étape 6 — Répondre aux commandes](#étape-6--répondre-aux-commandes)
- [Étape 7 — Crate `matheo-api` : la route `POST /notify`](#étape-7--crate-matheo-api--la-route-post-notify)
- [Étape 8 — Crate `matheo-scheduler` : les tâches quotidiennes](#étape-8--crate-matheo-scheduler--les-tâches-quotidiennes)
- [Étape 9 — Tester une crate](#étape-9--tester-une-crate)
- [Étape 10 — Récapitulatif et bonnes pratiques](#étape-10--récapitulatif-et-bonnes-pratiques)
- [Aller plus loin](#aller-plus-loin)
- [Problèmes fréquents](#problèmes-fréquents)

---

## Étape 0 — Les outils

Rust est déjà installé sur ta machine. Vérifie dans un terminal (dans RustRover : onglet **Terminal** en bas) :

```bash
cargo --version
```

Tu dois voir `cargo 1.99.0` ou plus. Si ce n'est pas le cas, installe Rust depuis https://rustup.rs.

**Les deux outils à connaître :**

| Outil | Rôle |
|---|---|
| `rustc` | Le compilateur. Tu ne l'appelleras presque jamais directement. |
| `cargo` | Le chef d'orchestre : crée les crates, télécharge les bibliothèques, compile, lance, teste. |

**Les commandes cargo dont tu auras besoin :**

| Commande | Effet |
|---|---|
| `cargo run` | Compile puis lance le programme. |
| `cargo build` | Compile seulement. |
| `cargo check` | Vérifie le code sans produire d'exécutable (très rapide). |
| `cargo test` | Lance les tests. |
| `cargo new <chemin>` | Crée une nouvelle crate. |
| `cargo add <nom> -p <crate>` | Ajoute une bibliothèque à une crate du workspace. |
| `cargo fmt` | Remet le code en forme proprement. |

Dans un workspace, `-p <crate>` (pour *package*) dit à cargo **sur quelle crate** travailler : `cargo test -p matheo-api` ne teste que l'API.

**Le projet tel qu'il est maintenant :**

```text
M.A.T.H.E.O/
├── Cargo.toml           ← le fichier du WORKSPACE (pas d'une crate)
├── Cargo.lock           ← versions exactes utilisées (généré, à commiter)
├── .env.example         ← modèle de configuration
├── .gitignore
└── crates/
    └── matheo/          ← la crate du programme principal
        ├── Cargo.toml
        └── src/
            └── main.rs
```

Lance-le depuis la racine :

```bash
cargo run
```

Tu vois `Hello, world!`. Cargo a compilé la crate `matheo` dans le dossier `target/` (à la racine) puis l'a exécutée.

---

## Étape 1 — Rust en 15 minutes

Lis cette partie une fois, sans chercher à tout retenir. Tu y reviendras quand tu croiseras ces notions dans le code.

### 1.1 La fonction `main`

```rust
fn main() {
    println!("Hello, world!");
}
```

- `fn` déclare une **fonction**. `main` est celle que le programme exécute au démarrage.
- `println!` affiche du texte. Le `!` indique que c'est une **macro** (une sorte de fonction spéciale qui génère du code). Tu en verras d'autres : `format!`, `vec!`…
- Chaque instruction finit par `;`.

### 1.2 Variables

```rust
let nom = "Matheo";        // une variable : NON modifiable par défaut
let mut compteur = 0;      // `mut` = modifiable
compteur = compteur + 1;

let age: u32 = 25;         // on peut préciser le type, mais Rust le devine souvent
```

Types courants : `i32`/`i64` (entiers, positifs ou négatifs), `u16`/`u32` (entiers positifs), `f64` (nombres à virgule), `bool`, `String` (texte), `&str` (texte « emprunté », voir 1.8).

Insérer une variable dans du texte :

```rust
let texte = format!("Bonjour {nom}, tu as {age} ans");
```

### 1.3 Fonctions

```rust
fn additionner(a: i32, b: i32) -> i32 {
    a + b      // pas de `;` → c'est la valeur renvoyée
}
```

- Les paramètres ont toujours un type.
- `-> i32` = le type renvoyé.
- La dernière expression **sans `;`** est la valeur de retour (on peut aussi écrire `return a + b;`).

### 1.4 `struct` : regrouper des données

```rust
struct Personne {
    nom: String,
    age: u32,
}

let p = Personne { nom: "Matheo".to_string(), age: 25 };
println!("{}", p.nom);
```

On ajoute des fonctions à une struct avec `impl` :

```rust
impl Personne {
    fn presenter(&self) -> String {
        format!("Je m'appelle {}", self.nom)
    }
}
```

`&self` = « la struct sur laquelle on appelle la méthode » (comme `this` ou `self` dans d'autres langages).

### 1.5 `enum` et `match` : un choix parmi plusieurs

```rust
enum Commande {
    Ping,
    Aide,
}

let reponse = match commande {
    Commande::Ping => "Pong",
    Commande::Aide => "Voici l'aide",
};
```

`match` oblige à traiter **tous** les cas. Si tu ajoutes une variante à l'enum et que tu l'oublies dans un `match`, le programme ne compile pas : c'est voulu, ça évite les oublis.

### 1.6 `Option` : une valeur qui peut être absente

Rust n'a pas de `null`. Une valeur facultative est une `Option` :

```rust
let titre: Option<String> = Some("Alerte".to_string());   // il y a une valeur
let rien: Option<String> = None;                          // pas de valeur

match titre {
    Some(t) => println!("Titre : {t}"),
    None => println!("Pas de titre"),
}
```

### 1.7 `Result` et `?` : gérer les erreurs

Une opération qui peut échouer renvoie un `Result` : soit `Ok(valeur)`, soit `Err(erreur)`.

```rust
let nombre = "42".parse::<i64>();    // Ok(42)
let rate = "abc".parse::<i64>();     // Err(...)
```

Le point d'interrogation `?` est le raccourci le plus utile du langage :

```rust
fn lire_nombre(texte: &str) -> anyhow::Result<i64> {
    let n = texte.parse::<i64>()?;   // si erreur → la fonction s'arrête et renvoie l'erreur
    Ok(n * 2)                        // sinon on continue avec la valeur
}
```

Il ne s'utilise que dans une fonction qui renvoie elle-même un `Result`. On utilisera la bibliothèque `anyhow`, dont le type `anyhow::Result<T>` accepte n'importe quelle erreur.

### 1.8 Propriété (ownership), emprunt et `clone`

C'est **la** notion propre à Rust. Règle : chaque valeur a **un seul propriétaire**.

```rust
let a = String::from("salut");
let b = a;           // la valeur est DÉPLACÉE de a vers b
// println!("{a}");  // ❌ erreur : a ne possède plus rien
```

Deux façons de partager :

- **Emprunter** avec `&` : on prête la valeur sans la donner.
  ```rust
  fn afficher(texte: &str) { println!("{texte}"); }
  afficher(&b);       // b reste utilisable après
  ```
- **Cloner** avec `.clone()` : on fabrique une copie.
  ```rust
  let c = b.clone();  // b et c existent tous les deux
  ```

Dans ce projet, on fera souvent `messager.clone()` : l'objet qui envoie les messages Telegram doit être utilisé à trois endroits (commandes, API, tâches). Le cloner ne coûte presque rien : on copie juste une « poignée » vers la même connexion.

### 1.9 Modules : découper une crate en fichiers

À l'intérieur d'une crate, chaque fichier `src/xxx.rs` est un **module**. On le déclare dans `main.rs` (ou `lib.rs`) :

```rust
mod config;            // charge src/config.rs
```

Puis on utilise ce qu'il contient avec `config::Config`. Seuls les éléments marqués `pub` (public) sont visibles depuis l'extérieur du module.

`use` sert à raccourcir les noms :

```rust
use std::env;          // ensuite on écrit env::var(...) au lieu de std::env::var(...)
```

### 1.10 Crates et workspace

- Une **crate** est un projet Rust avec son propre `Cargo.toml`. Il en existe deux sortes :
  - **binaire** : elle a un `src/main.rs` et produit un programme qu'on lance ;
  - **bibliothèque** (*library*) : elle a un `src/lib.rs` et fournit du code à d'autres crates.
- Les bibliothèques publiques se trouvent sur https://crates.io (`tokio`, `axum`…).
- Un **workspace** regroupe plusieurs crates dans un même dossier. Elles partagent le même `Cargo.lock`, le même dossier `target/` et les mêmes versions de dépendances.

Dans M.A.T.H.E.O : une crate binaire `matheo` qui **assemble** trois crates bibliothèques, `matheo-telegram`, `matheo-api` et `matheo-scheduler`.

### 1.11 `async` / `await` : faire plusieurs choses à la fois

Notre assistant doit en même temps écouter Telegram, répondre à l'API et surveiller l'heure. On écrit donc du code **asynchrone** :

```rust
async fn envoyer() { /* ... */ }

envoyer().await;     // "lance et attends le résultat, sans bloquer les autres tâches"
```

- Une fonction `async` ne s'exécute pas toute seule : il faut l'**attendre** avec `.await`.
- Il faut un **moteur** pour faire tourner tout ça : c'est **Tokio**. On l'active avec `#[tokio::main]` au-dessus de `main`.
- `tokio::spawn(...)` lance une tâche **en parallèle** et continue tout de suite.

### 1.12 Les closures (fonctions anonymes)

```rust
let doubler = |x: i32| x * 2;
doubler(4);   // 8
```

`move |x| ...` signifie que la closure **prend possession** des variables qu'elle utilise. On s'en servira pour les tâches planifiées.

### 1.13 Les attributs `#[...]`

Ce sont des annotations au-dessus du code :

- `#[derive(Clone)]` : « génère automatiquement le code pour pouvoir cloner cette struct ».
- `#[derive(Deserialize)]` : « génère le code pour lire cette struct depuis du JSON ».
- `#[tokio::main]` : « transforme `main` pour qu'elle tourne avec Tokio ».
- `#[test]` : « cette fonction est un test ».

C'est tout ce qu'il faut pour suivre. On attaque.

---

## Étape 2 — Créer le bot sur Telegram

### 2.1 Obtenir le token

1. Sur Telegram, cherche **@BotFather** (le compte officiel, avec le badge bleu).
2. Envoie `/newbot`.
3. Donne un nom (ex. `M.A.T.H.E.O`) puis un identifiant qui finit par `bot` (ex. `matheo_assistant_bot`).
4. BotFather te répond avec un **token** du genre `123456789:ABCdef...`. C'est le mot de passe de ton bot : ne le partage jamais.

### 2.2 Obtenir ton `chat_id`

Le bot a besoin de savoir **à qui** envoyer les messages spontanés (API, tâches du matin).

1. Ouvre la conversation avec ton bot et envoie-lui un message, n'importe lequel (ex. `salut`).
2. Dans ton navigateur, ouvre l'adresse suivante en remplaçant `<TOKEN>` par ton token :
   ```text
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. Dans le JSON affiché, cherche `"chat":{"id":123456789,...}`. Ce nombre est ton `chat_id`.

> Si la liste est vide (`"result":[]`), renvoie un message au bot et recharge la page.

### 2.3 Créer le fichier `.env`

Copie `.env.example` en `.env` (à la racine, à côté du `Cargo.toml` du workspace), puis remplis-le :

```text
TELEGRAM_BOT_TOKEN=le_token_de_botfather
TELEGRAM_CHAT_ID=ton_chat_id
API_ADDR=127.0.0.1:3000
API_KEY=invente-un-long-mot-de-passe
```

`.env` est listé dans `.gitignore` : il ne partira jamais sur Git. C'est là que vivent les secrets.

---

## Étape 3 — Comprendre et préparer le workspace

### 3.1 Le `Cargo.toml` de la racine

Ouvre `Cargo.toml` à la racine :

```toml
[workspace]
resolver = "3"
members = ["crates/*"]

# Valeurs partagées par toutes les crates du workspace.
[workspace.package]
version = "0.1.0"
edition = "2024"

# Les versions des dépendances, déclarées une seule fois pour tout le workspace.
[workspace.dependencies]
```

Ligne par ligne :

- `[workspace]` : ce fichier décrit un **workspace**, pas une crate. Il n'a pas de `[package]` ni de `src/`. On appelle ça un *workspace virtuel*.
- `members = ["crates/*"]` : **chaque dossier dans `crates/` est une crate du workspace**. Grâce à l'étoile, une nouvelle crate créée dans `crates/` est prise en compte automatiquement.
- `resolver = "3"` : la façon dont Cargo choisit les versions des dépendances. `"3"` est la plus récente : mets-la toujours.
- `[workspace.package]` : des réglages communs. Chaque crate peut en hériter au lieu de les répéter.
- `[workspace.dependencies]` : la liste **centrale** des dépendances et de leurs versions. On la remplit juste après.

### 3.2 Le `Cargo.toml` d'une crate membre

Ouvre `crates/matheo/Cargo.toml` :

```toml
[package]
name = "matheo"
version.workspace = true
edition.workspace = true

[dependencies]
```

`version.workspace = true` veut dire « prends la version définie dans `[workspace.package]` ». `cargo new` écrit ces lignes tout seul quand on crée une crate dans un workspace.

### 3.3 Déclarer les dépendances une seule fois

**Bonne pratique :** les versions des bibliothèques sont écrites **à un seul endroit**, le `Cargo.toml` de la racine. Les crates disent seulement « j'utilise celle du workspace ». Comme ça, toutes les crates utilisent forcément la même version, et une mise à jour se fait en changeant une seule ligne.

Remplace la section `[workspace.dependencies]` du `Cargo.toml` **racine** par :

```toml
[workspace.dependencies]
# --- Bibliothèques externes ---
anyhow = "1.0.104"
axum = "0.8.9"
chrono-tz = "0.10.4"
dotenvy = "0.15.7"
env_logger = "0.11.11"
log = "0.4.35"
serde = { version = "1.0.229", features = ["derive"] }
teloxide = { version = "0.17.0", features = ["macros"] }
tokio = { version = "1.54.1", features = ["full"] }
tokio-cron-scheduler = "0.15.1"
tower = { version = "0.5.3", features = ["util"] }
```

À quoi sert chaque crate :

| Crate | Rôle |
|---|---|
| `anyhow` | Simplifie la gestion des erreurs. |
| `axum` | Crée le serveur web de notre API. |
| `chrono-tz` | Les fuseaux horaires (pour dire « 8 h heure de Paris »). |
| `dotenvy` | Lit le fichier `.env`. |
| `log` + `env_logger` | Affichent des messages de suivi dans le terminal. |
| `serde` | Convertit du JSON en structs Rust. `derive` active `#[derive(Deserialize)]`. |
| `teloxide` | Parle à l'API Telegram. `macros` permet de déclarer les commandes facilement. |
| `tokio` | Le moteur asynchrone (étape 1.11). `full` active toutes ses fonctions. |
| `tokio-cron-scheduler` | Lance des tâches à heure fixe. |
| `tower` | Outils pour serveurs web ; on s'en sert seulement pour les tests de l'API. |

> Des versions plus récentes existent peut-être quand tu lis ceci. Pour connaître la dernière version d'une crate : `cargo search <nom>`, ou sa page sur https://crates.io.

Déclarer une dépendance ici **ne l'ajoute à aucune crate**. Pour qu'une crate l'utilise, on lancera par exemple :

```bash
cargo add anyhow -p matheo
```

Cargo voit qu'`anyhow` est déjà déclarée dans le workspace et écrit dans `crates/matheo/Cargo.toml` :

```toml
anyhow.workspace = true
```

### 3.4 Le plan du workspace

Voici les crates qu'on va créer, et qui dépend de qui :

```text
          matheo  (binaire : lit la config et assemble tout)
         /    |     \
        ▼     ▼      ▼
matheo-api  matheo-scheduler   (bibliothèques)
        \     |
         ▼    ▼
      matheo-telegram          (bibliothèque : le seul à connaître Telegram)
```

- Une flèche veut dire « dépend de ». Le binaire `matheo` dépend des trois bibliothèques, et l'API comme le planificateur dépendent de `matheo-telegram` pour envoyer des messages.
- **Cargo interdit les cycles** : `matheo-telegram` ne pourra jamais dépendre de `matheo-api`. Ça force une architecture propre.
- **Bonne pratique :** les bibliothèques ne lisent ni le `.env` ni la configuration. Elles reçoivent ce dont elles ont besoin en paramètre. Seul le binaire connaît la configuration et branche les morceaux ensemble.

Vérifie que tout va bien :

```bash
cargo build
```

---

## Étape 4 — Lire la configuration (crate `matheo`)

**Fonctionnalité :** lire le `.env` et ranger les valeurs dans une struct `Config`.

La configuration est propre au programme : elle vit donc dans la crate binaire `matheo`. Ajoute-lui ses premières dépendances :

```bash
cargo add anyhow dotenvy -p matheo
```

Crée le fichier `crates/matheo/src/config.rs` :

```rust
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

        let telegram_token =
            env::var("TELEGRAM_BOT_TOKEN").context("TELEGRAM_BOT_TOKEN manque dans .env")?;

        let chat_id = env::var("TELEGRAM_CHAT_ID")
            .context("TELEGRAM_CHAT_ID manque dans .env")?
            .parse()
            .context("TELEGRAM_CHAT_ID doit être un nombre")?;

        let api_addr = env::var("API_ADDR")
            .unwrap_or_else(|_| "127.0.0.1:3000".to_string())
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
```

**Ce qu'il faut comprendre :**

- `pub struct Config` : la struct est publique, et chaque champ aussi (`pub`), pour que `main.rs` puisse les lire.
- `/// ...` : un commentaire de **documentation**. RustRover l'affiche au survol.
- `env::var("NOM")` renvoie un `Result` : `Ok(valeur)` si la variable existe, `Err` sinon.
- `.context("...")` (fourni par `anyhow::Context`) remplace le message d'erreur par défaut par un message clair.
- `?` : en cas d'erreur, on arrête tout et on renvoie l'erreur (étape 1.7).
- `.parse()` convertit le texte en nombre (`i64`) ou en adresse (`SocketAddr`). Rust devine **vers quel type** convertir grâce aux types des champs de `Config`.
- `.unwrap_or_else(|_| "127.0.0.1:3000".to_string())` : si `API_ADDR` est absent, on prend une valeur par défaut. La closure `|_| ...` (étape 1.12) n'est appelée qu'en cas d'absence : la chaîne par défaut n'est donc pas créée pour rien quand la variable existe.
- `Ok(Config { telegram_token, chat_id, ... })` : écrire `chat_id` tout seul revient à écrire `chat_id: chat_id`.
- `dotenvy::dotenv()` cherche le `.env` dans le dossier courant **puis dans les dossiers parents** : il trouve donc celui de la racine du workspace.

Remplace **tout** le contenu de `crates/matheo/src/main.rs` par :

```rust
mod config;

fn main() -> anyhow::Result<()> {
    let config = config::Config::from_env()?;
    println!("Configuration chargée, chat_id = {}", config.chat_id);
    Ok(())
}
```

- `mod config;` charge le fichier `src/config.rs` de la même crate.
- `main` renvoie maintenant un `Result` : on peut y utiliser `?`. Si la config est invalide, le programme s'arrête et affiche l'erreur.
- `()` (prononcé « unit ») veut dire « rien ». `Ok(())` = « tout s'est bien passé, rien à renvoyer ».

Lance, toujours depuis la racine :

```bash
cargo run
```

✅ Tu dois voir `Configuration chargée, chat_id = ...`.

🧪 Teste l'erreur : renomme temporairement `.env` en `.env.bak` et relance. Tu obtiens `Error: TELEGRAM_BOT_TOKEN manque dans .env`. Remets le nom d'origine.

> RustRover peut afficher des avertissements `field is never read` : c'est normal, on n'utilise pas encore tous les champs. Ils disparaîtront plus tard.

---

## Étape 5 — Crate `matheo-telegram` : envoyer un premier message

**Fonctionnalité :** au démarrage, le bot t'envoie « M.A.T.H.E.O est en ligne ! ».

On crée notre première **bibliothèque**. Elle contiendra tout ce qui touche à Telegram.

### 5.1 Créer la crate

```bash
cargo new crates/matheo-telegram --lib --vcs none
```

- `--lib` : une bibliothèque (`src/lib.rs`), pas un programme.
- `--vcs none` : ne pas créer de dépôt Git à l'intérieur. Le projet est déjà un dépôt Git, il n'en faut pas un deuxième dedans.

Cargo a créé `crates/matheo-telegram/` avec un `Cargo.toml` et un `src/lib.rs` d'exemple. Grâce à `members = ["crates/*"]`, elle fait déjà partie du workspace.

### 5.2 Déclarer la crate dans le workspace

Pour que les autres crates puissent l'utiliser, ajoute-la dans `[workspace.dependencies]` du `Cargo.toml` **racine**, au-dessus des bibliothèques externes :

```toml
[workspace.dependencies]
# --- Nos propres crates ---
matheo-telegram = { path = "crates/matheo-telegram" }

# --- Bibliothèques externes ---
anyhow = "1.0.104"
# ... (le reste ne change pas)
```

`path = "..."` : « cette dépendance n'est pas sur crates.io, elle est dans ce dossier ».

Puis branche les dépendances :

```bash
cargo add teloxide anyhow -p matheo-telegram
```

```bash
cargo add matheo-telegram tokio env_logger log -p matheo
```

La première commande donne à `matheo-telegram` ce dont il a besoin. La seconde fait dépendre le programme `matheo` de notre nouvelle crate (et ajoute Tokio et les logs au programme).

### 5.3 Le code de la bibliothèque

Remplace **tout** le contenu de `crates/matheo-telegram/src/lib.rs` par :

```rust
//! Tout ce qui concerne Telegram : envoyer des messages et répondre aux commandes.

use teloxide::prelude::*;

/// Envoie des messages au propriétaire de l'assistant (toi).
///
/// C'est le seul type que les autres crates utilisent : elles n'ont pas
/// besoin de savoir que Telegram existe.
#[derive(Clone)]
pub struct Messager {
    bot: Bot,
    chat_id: ChatId,
}

impl Messager {
    /// Crée un `Messager` à partir du token du bot et de ton chat_id.
    pub fn new(token: String, chat_id: i64) -> Messager {
        Messager {
            bot: Bot::new(token),
            chat_id: ChatId(chat_id),
        }
    }

    /// Envoie un message texte sur ta conversation Telegram.
    pub async fn envoyer(&self, texte: &str) -> anyhow::Result<()> {
        self.bot.send_message(self.chat_id, texte).await?;
        Ok(())
    }
}
```

**Ce qu'il faut comprendre :**

- `//! ...` (avec un `!`) documente **la crate entière**, alors que `///` documente l'élément juste en dessous.
- `use teloxide::prelude::*;` importe d'un coup les éléments les plus utilisés de teloxide (`Bot`, `ChatId`, `Message`…). Le `*` veut dire « tout ».
- `pub struct Messager` est public, mais **ses champs `bot` et `chat_id` ne le sont pas** (pas de `pub` devant). Les autres crates peuvent créer un `Messager` avec `Messager::new` et appeler `envoyer`, mais ne voient jamais le `Bot` de teloxide. C'est l'**encapsulation** : on expose le minimum. Si un jour tu remplaces Telegram par autre chose, seule cette crate change.
- `#[derive(Clone)]` : on pourra faire `messager.clone()` (étape 1.8).
- `ChatId(chat_id)` : teloxide n'accepte pas un simple nombre. Il veut un `ChatId`, une petite struct qui « emballe » le nombre. Ça empêche de confondre un identifiant de conversation avec un autre nombre.
- `self.bot.send_message(...).await?` : on prépare le message, on **attend** que Telegram réponde (`.await`) et on remonte l'erreur s'il y en a une (`?`).
- `envoyer` prend un `&str` (un texte emprunté) : on peut lui passer `"du texte"` directement, ou `&une_string`.

### 5.4 L'utiliser depuis le programme

Remplace `crates/matheo/src/main.rs` par :

```rust
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
```

- `use matheo_telegram::Messager;` : la crate s'appelle `matheo-telegram` dans les `Cargo.toml`, mais **dans le code Rust les tirets deviennent des underscores** : `matheo_telegram`.
- `#[tokio::main]` + `async fn main` : `main` devient asynchrone et tourne avec Tokio.
- Le token est **déplacé** dans le `Messager` (étape 1.8) : on n'en a plus besoin ailleurs.
- `log::info!` affiche une ligne de suivi, avec la date, dans le terminal.

```bash
cargo run
```

⏳ **Cette compilation prend plusieurs minutes** : Cargo télécharge et compile teloxide, Tokio et leurs dépendances. Les suivantes ne prendront que quelques secondes.

✅ Ton téléphone vibre : le bot t'a écrit.

---

## Étape 6 — Répondre aux commandes

**Fonctionnalité :** le bot reste allumé et répond à `/start`, `/aide`, `/ping` et `/id`.

Ça concerne Telegram, donc ça va dans la crate `matheo-telegram`, dans un **module privé** `commandes`.

Ajoute `log` à la crate :

```bash
cargo add log -p matheo-telegram
```

Crée `crates/matheo-telegram/src/commandes.rs` :

```rust
use teloxide::{prelude::*, utils::command::BotCommands};

/// Voici ce que je sais faire :
#[derive(BotCommands, Clone)]
#[command(rename_rule = "lowercase")]
pub enum Command {
    /// Dire bonjour.
    Start,
    /// Afficher cette aide.
    Aide,
    /// Vérifier que je suis réveillé.
    Ping,
    /// Afficher l'identifiant de cette conversation.
    Id,
}

/// Appelée automatiquement à chaque commande reçue sur Telegram.
pub async fn repondre(bot: Bot, msg: Message, cmd: Command) -> ResponseResult<()> {
    let texte = match cmd {
        Command::Start => "Salut ! Je suis M.A.T.H.E.O, ton assistant. Tape /aide.".to_string(),
        Command::Aide => Command::descriptions().to_string(),
        Command::Ping => "Pong ! 🏓".to_string(),
        Command::Id => format!("Ton chat_id est : {}", msg.chat.id),
    };

    bot.send_message(msg.chat.id, texte).await?;
    Ok(())
}
```

Dans `crates/matheo-telegram/src/lib.rs`, ajoute la ligne `mod commandes;` juste sous le commentaire `//!`, puis ajoute cette méthode **dans** le bloc `impl Messager`, après `envoyer` :

```rust
    /// Écoute les commandes Telegram et y répond. Ne s'arrête qu'avec Ctrl+C.
    pub async fn ecouter_commandes(self) {
        log::info!("En attente de messages Telegram…");
        commandes::Command::repl(self.bot, commandes::repondre).await;
    }
```

**Ce qu'il faut comprendre :**

- `mod commandes;` **sans `pub`** : le module est privé. `Command` et `repondre` sont `pub` à l'intérieur de la crate, mais invisibles pour `matheo`, `matheo-api`… Le reste du workspace ne connaît que `Messager::ecouter_commandes()`.
- `enum Command` liste les commandes possibles (étape 1.5).
- `#[derive(BotCommands)]` est la magie de teloxide : il génère le code qui transforme le texte `/ping` en `Command::Ping`.
- `rename_rule = "lowercase"` : la variante `Ping` correspond à la commande `/ping` (en minuscules).
- Les commentaires `///` deviennent le texte d'aide : `Command::descriptions()` les rassemble pour la commande `/aide`.
- `repondre` reçoit 3 choses, fournies automatiquement par teloxide : le `bot`, le `msg` reçu (qui contient notamment `msg.chat.id`, la conversation d'origine) et la `cmd` déjà décodée.
- Toutes les branches du `match` doivent renvoyer le **même type** : ici `String`, d'où les `.to_string()` (qui transforment un `&str` en `String`).
- `ecouter_commandes(self)` prend `self` **sans `&`** : la méthode consomme le `Messager` (elle lui prend son `bot`). Après l'avoir appelée, on ne peut plus utiliser ce `Messager`-là, d'où les `.clone()` qu'on fera avant.
- `repl` (pour *Read-Eval-Print Loop*) est une boucle infinie : elle demande sans arrêt à Telegram « y a-t-il de nouveaux messages ? » et, pour chaque commande, appelle `repondre`. Elle ne s'arrête qu'avec **Ctrl+C**.

Dans `crates/matheo/src/main.rs`, remplace la ligne `log::info!("Message de démarrage envoyé");` par :

```rust
    messager.ecouter_commandes().await;
```

```bash
cargo run
```

✅ Sur Telegram, envoie `/ping` → `Pong ! 🏓`. Envoie `/aide` → la liste des commandes.

> 💡 Pour que Telegram propose les commandes quand tu tapes `/`, envoie `/setcommands` à @BotFather, choisis ton bot, puis colle :
> ```text
> aide - Afficher l'aide
> ping - Vérifier que je suis réveillé
> id - Afficher l'identifiant de la conversation
> ```

**Ajouter une commande** : ajoute une variante dans l'enum (avec son `///`), puis compile. Rust te signale que le `match` ne gère pas ce cas (étape 1.5) : ajoute la branche correspondante. C'est le compilateur qui te guide.

---

## Étape 7 — Crate `matheo-api` : la route `POST /notify`

**Fonctionnalité :** n'importe quel programme (un script, ta domotique, un raccourci iPhone, un autre serveur…) peut envoyer ce JSON :

```json
{ "titre": "Machine à laver", "message": "Le cycle est terminé" }
```

…à l'adresse `http://127.0.0.1:3000/notify`, et tu le reçois sur Telegram. La requête doit contenir l'en-tête `x-api-key` avec ta clé secrète, sinon elle est refusée.

### 7.1 Créer et brancher la crate

Tu connais maintenant la marche à suivre pour ajouter une crate au workspace :

**1. La créer :**

```bash
cargo new crates/matheo-api --lib --vcs none
```

**2. La déclarer** dans `[workspace.dependencies]` du `Cargo.toml` racine :

```toml
matheo-api = { path = "crates/matheo-api" }
```

**3. Lui donner ses dépendances**, puis la faire utiliser par le programme :

```bash
cargo add axum serde log anyhow tokio matheo-telegram -p matheo-api
```

```bash
cargo add matheo-api -p matheo
```

Note que `matheo-api` dépend de `matheo-telegram` (pour `Messager`), mais **pas** de `teloxide` : elle n'a pas besoin de savoir comment Telegram fonctionne.

### 7.2 Le code

Remplace **tout** le contenu de `crates/matheo-api/src/lib.rs` par :

```rust
//! L'API HTTP : une seule route, `POST /notify`.

use axum::{
    Json, Router,
    extract::State,
    http::{HeaderMap, StatusCode},
    routing::post,
};
use matheo_telegram::Messager;
use serde::Deserialize;
use std::net::SocketAddr;

/// Ce dont la route a besoin pour travailler. Partagé entre toutes les requêtes.
#[derive(Clone)]
struct AppState {
    messager: Messager,
    api_key: String,
}

/// Le JSON attendu dans le corps de la requête.
#[derive(Deserialize)]
struct Notification {
    titre: Option<String>,
    message: String,
}

/// Réserve le port, puis lance le serveur en arrière-plan.
pub async fn demarrer(addr: SocketAddr, messager: Messager, api_key: String) -> anyhow::Result<()> {
    let listener = tokio::net::TcpListener::bind(addr).await?;
    let app = router(messager, api_key);
    log::info!("API en écoute sur http://{addr}");

    tokio::spawn(async move {
        if let Err(erreur) = axum::serve(listener, app).await {
            log::error!("L'API s'est arrêtée : {erreur}");
        }
    });
    Ok(())
}

/// Construit le routeur : une seule route, POST /notify.
fn router(messager: Messager, api_key: String) -> Router {
    Router::new()
        .route("/notify", post(notify))
        .with_state(AppState { messager, api_key })
}

/// Reçoit une notification et la transfère sur Telegram.
async fn notify(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(notif): Json<Notification>,
) -> StatusCode {
    // 1. Vérifier la clé secrète envoyée dans l'en-tête "x-api-key".
    let cle_recue = headers.get("x-api-key").and_then(|v| v.to_str().ok());
    if cle_recue != Some(state.api_key.as_str()) {
        return StatusCode::UNAUTHORIZED; // 401
    }

    // 2. Construire le texte.
    let texte = match notif.titre {
        Some(titre) => format!("📬 {titre}\n\n{}", notif.message),
        None => format!("📬 {}", notif.message),
    };

    // 3. L'envoyer sur Telegram.
    match state.messager.envoyer(&texte).await {
        Ok(()) => StatusCode::OK, // 200
        Err(erreur) => {
            log::error!("Envoi Telegram impossible : {erreur}");
            StatusCode::BAD_GATEWAY // 502
        }
    }
}
```

### 7.3 Ce qu'il faut comprendre

**Ce qui est public.** Une seule fonction est `pub` : `demarrer`. Tout le reste (`AppState`, `Notification`, `router`, `notify`) est privé à la crate. Le programme principal n'a besoin que de « démarre l'API à cette adresse, avec ce messager et cette clé ».

**`demarrer`.** `TcpListener::bind(addr)` réserve le port. Si le port est déjà pris, le `?` renvoie l'erreur tout de suite, et le programme s'arrête avec un message clair. Ensuite `tokio::spawn(async move { ... })` lance le serveur **en parallèle** (étape 1.11) et la fonction se termine aussitôt. Sans ça, `axum::serve` tournerait à l'infini et `main` n'atteindrait jamais l'écoute des commandes Telegram. `move` donne au bloc la propriété de `listener` et `app`.

**`if let Err(erreur) = ... { }`** : « si le résultat est une erreur, exécute ce bloc ». C'est un `match` abrégé quand un seul cas nous intéresse.

**Le routeur.** `Router::new().route("/notify", post(notify))` signifie : « quand une requête `POST` arrive sur `/notify`, appelle la fonction `notify` ». Une API = une route, donc une seule ligne `.route(...)`.

**L'état partagé (`AppState`).** `notify` a besoin du messager et de la clé. On les range dans une struct qu'on donne au routeur avec `.with_state(...)`. axum la passe ensuite à chaque requête. Elle doit être `Clone` car chaque requête en reçoit une copie.

**Les extracteurs.** Les paramètres de `notify` ne sont pas des valeurs qu'on passe nous-mêmes. axum lit la requête HTTP et **remplit chaque paramètre selon son type** :

| Paramètre | Ce qu'axum y met |
|---|---|
| `State(state): State<AppState>` | L'état partagé. |
| `headers: HeaderMap` | Tous les en-têtes HTTP. |
| `Json(notif): Json<Notification>` | Le corps de la requête, converti en struct `Notification`. |

`State(state)` est un **déstructurage** : on « ouvre l'emballage » `State(...)` pour récupérer directement `state`. Même chose pour `Json(notif)`.

⚠️ Le paramètre `Json` doit toujours être **le dernier** : il consomme le corps de la requête.

**serde et `Option`.** `#[derive(Deserialize)]` génère la conversion JSON → struct. Comme `titre` est une `Option<String>`, il est **facultatif** : `{"message": "coucou"}` est accepté. `message` est obligatoire : s'il manque, axum répond tout seul `422 Unprocessable Entity`, sans même appeler ta fonction.

**La vérification de la clé.**
- `headers.get("x-api-key")` renvoie une `Option` (l'en-tête peut être absent).
- `.and_then(|v| v.to_str().ok())` : « s'il y a une valeur, essaie de la lire comme du texte ». On obtient une `Option<&str>`.
- On la compare à `Some(state.api_key.as_str())`. Si c'est différent (clé absente ou fausse), on répond `401 Unauthorized`.

**La réponse.** La fonction renvoie un `StatusCode` : c'est le code HTTP que recevra l'appelant (200 = OK, 401 = refusé, 502 = Telegram n'a pas répondu).

### 7.4 Lancer l'API depuis le programme

Dans `crates/matheo/src/main.rs`, ajoute cette ligne **juste avant** `messager.ecouter_commandes().await;` :

```rust
    matheo_api::demarrer(config.api_addr, messager.clone(), config.api_key).await?;
```

`messager.clone()` : l'API reçoit sa propre copie, car l'original sert juste après à `ecouter_commandes`.

### 7.5 Tester

Lance `cargo run`, puis **dans un second terminal** (le `+` de l'onglet Terminal de RustRover), en PowerShell :

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:3000/notify -Headers @{ "x-api-key" = "ta-cle-du-.env" } -ContentType "application/json; charset=utf-8" -Body '{"titre": "Test", "message": "Tout fonctionne !"}'
```

Ou avec curl :

```bash
curl -X POST http://127.0.0.1:3000/notify -H "x-api-key: ta-cle-du-.env" -H "Content-Type: application/json" -d "{\"message\": \"Salut depuis curl\"}"
```

✅ Le message arrive sur Telegram.

🧪 Essaie avec une mauvaise clé : tu obtiens une erreur `401`. Essaie sans le champ `message` : erreur `422`.

> `127.0.0.1` signifie « seulement depuis cet ordinateur ». Pour que d'autres appareils de ton réseau puissent appeler l'API, mets `API_ADDR=0.0.0.0:3000` dans `.env` (Windows te demandera d'autoriser le programme dans le pare-feu).

---

## Étape 8 — Crate `matheo-scheduler` : les tâches quotidiennes

**Fonctionnalité :** tous les jours à 8 h (heure de Paris), le bot t'envoie un message.

### 8.1 Créer et brancher la crate

Même marche à suivre qu'à l'étape 7.1 :

```bash
cargo new crates/matheo-scheduler --lib --vcs none
```

Dans `[workspace.dependencies]` du `Cargo.toml` racine :

```toml
matheo-scheduler = { path = "crates/matheo-scheduler" }
```

```bash
cargo add tokio-cron-scheduler chrono-tz anyhow log matheo-telegram -p matheo-scheduler
```

```bash
cargo add matheo-scheduler -p matheo
```

### 8.2 Le code

Remplace **tout** le contenu de `crates/matheo-scheduler/src/lib.rs` par :

```rust
//! Les tâches qui se lancent toutes seules, à heure fixe.

use chrono_tz::Europe::Paris;
use matheo_telegram::Messager;
use tokio_cron_scheduler::{Job, JobScheduler};

/// Crée le planificateur, y ajoute les tâches quotidiennes et le démarre.
pub async fn demarrer(messager: Messager) -> anyhow::Result<JobScheduler> {
    let planificateur = JobScheduler::new().await?;

    // Format : seconde minute heure jour-du-mois mois jour-de-la-semaine
    // "0 0 8 * * *" = tous les jours à 08:00:00 (heure de Paris).
    let bonjour = Job::new_async_tz("0 0 8 * * *", Paris, move |_id, _planificateur| {
        let messager = messager.clone();
        Box::pin(async move {
            let texte = "☀️ Bonjour ! Une nouvelle journée commence.";
            if let Err(erreur) = messager.envoyer(texte).await {
                log::error!("Message du matin non envoyé : {erreur}");
            }
        })
    })?;

    planificateur.add(bonjour).await?;
    planificateur.start().await?;
    Ok(planificateur)
}
```

### 8.3 L'expression « cron »

C'est un format standard pour décrire « quand » lancer une tâche. Ici il a **6 champs** :

```text
┌───────── seconde       (0-59)
│ ┌─────── minute        (0-59)
│ │ ┌───── heure         (0-23)
│ │ │ ┌─── jour du mois  (1-31)
│ │ │ │ ┌─ mois          (1-12)
│ │ │ │ │ ┌ jour semaine (Sun-Sat)
0 0 8 * * *
```

`*` = « n'importe lequel ». Exemples :

| Expression | Signification |
|---|---|
| `0 0 8 * * *` | Tous les jours à 8 h 00 |
| `0 30 22 * * *` | Tous les jours à 22 h 30 |
| `0 0 9 * * Mon-Fri` | Du lundi au vendredi à 9 h |
| `0 0 18 * * Sun` | Le dimanche à 18 h |
| `*/20 * * * * *` | Toutes les 20 secondes (pratique pour tester !) |

### 8.4 Ce qu'il faut comprendre

- `JobScheduler::new()` crée le planificateur. `.add(...)` lui donne une tâche, `.start()` le démarre **en arrière-plan**.
- `Job::new_async_tz(expression, fuseau, closure)` : à chaque déclenchement, la bibliothèque appelle la **closure** (étape 1.12). Elle reçoit deux paramètres dont on ne se sert pas : le `_` devant leur nom dit à Rust « je sais, je ne les utilise pas ».
- **Pourquoi `move` et `messager.clone()` ?** La closure doit vivre aussi longtemps que le planificateur, donc elle prend possession du `messager` (`move`). Mais elle s'exécute **chaque jour** : à chaque fois, on donne une copie à la tâche du jour (`let messager = messager.clone();`), et l'original reste dans la closure pour le lendemain.
- **Pourquoi `Box::pin(async move { ... })` ?** La bibliothèque attend une tâche asynchrone « emballée » sous une forme précise. Retiens-le comme une formule : *une tâche planifiée = `Box::pin(async move { ton code })`*.
- On utilise `if let Err` plutôt que `?` : si un envoi rate un matin, on note l'erreur mais le planificateur continue pour les jours suivants.
- La fonction renvoie le planificateur : `main` va le garder en vie.

### 8.5 Brancher dans `main.rs`

Dans `crates/matheo/src/main.rs`, juste **après** la ligne qui envoie le message de démarrage, ajoute :

```rust
    let _planificateur = matheo_scheduler::demarrer(messager.clone()).await?;
```

Le `_` devant `_planificateur` indique qu'on garde la variable sans s'en servir : elle existe jusqu'à la fin de `main`, donc le planificateur reste actif tant que le programme tourne.

### 8.6 Tester

Remplace temporairement `"0 0 8 * * *"` par `"*/20 * * * * *"`, lance `cargo run` : un message arrive toutes les 20 secondes. Remets `"0 0 8 * * *"` ensuite.

### 8.7 Ajouter une autre tâche

Copie le bloc `let bonjour = ...;` + `planificateur.add(bonjour).await?;`, change le nom, l'heure et le texte. Attention : comme `messager` a été déplacé dans la première closure, crée un clone **avant** chaque nouvelle tâche :

```rust
    let messager_soir = messager.clone();   // ← à placer AVANT `let bonjour = ...`
    // ...
    let bonsoir = Job::new_async_tz("0 0 22 * * *", Paris, move |_id, _planificateur| {
        let messager = messager_soir.clone();
        Box::pin(async move {
            if let Err(erreur) = messager.envoyer("🌙 Bonne nuit !").await {
                log::error!("Message du soir non envoyé : {erreur}");
            }
        })
    })?;
    planificateur.add(bonsoir).await?;
```

Si tu oublies, le compilateur te dira `use of moved value: messager` : c'est la règle de la propriété (étape 1.8) qui se manifeste.

---

## Étape 9 — Tester une crate

**Fonctionnalité :** vérifier automatiquement que l'API refuse les mauvaises requêtes, sans lancer Telegram.

Un des avantages des crates séparées : on teste chacune **seule**. Ici on teste `matheo-api`.

### 9.1 Une dépendance réservée aux tests

```bash
cargo add tower -p matheo-api --dev
```

`--dev` l'ajoute dans une section `[dev-dependencies]` : elle ne sert **que** pour les tests et n'est pas incluse dans le programme final.

### 9.2 Écrire les tests

Ajoute à la **fin** de `crates/matheo-api/src/lib.rs` :

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::Request;
    use tower::ServiceExt;

    /// Fabrique une requête POST /notify avec la clé et le JSON donnés.
    fn requete(cle: &str, json: &str) -> Request<Body> {
        Request::post("/notify")
            .header("x-api-key", cle)
            .header("content-type", "application/json")
            .body(Body::from(json.to_string()))
            .unwrap()
    }

    /// Un routeur de test, avec un faux token Telegram.
    fn app() -> Router {
        router(Messager::new("123:faux".to_string(), 1), "secret".to_string())
    }

    #[tokio::test]
    async fn refuse_une_mauvaise_cle() {
        let reponse = app().oneshot(requete("mauvaise", r#"{"message":"hi"}"#)).await.unwrap();
        assert_eq!(reponse.status(), StatusCode::UNAUTHORIZED);
    }

    #[tokio::test]
    async fn refuse_un_json_sans_message() {
        let reponse = app().oneshot(requete("secret", r#"{"titre":"hi"}"#)).await.unwrap();
        assert_eq!(reponse.status(), StatusCode::UNPROCESSABLE_ENTITY);
    }
}
```

**Ce qu'il faut comprendre :**

- `#[cfg(test)]` : ce module n'est compilé **que** pendant `cargo test`. Il n'alourdit pas le programme.
- `use super::*;` : importe tout ce qui est dans le module parent, y compris les éléments **privés** comme `router`. Un test placé dans la crate peut donc tester son fonctionnement interne.
- `#[tokio::test]` : comme `#[test]`, mais pour un test `async`.
- `.oneshot(requete)` (fourni par `tower`) envoie une requête au routeur **sans ouvrir de vrai port réseau**.
- `assert_eq!(a, b)` : le test échoue si `a` et `b` sont différents.
- `.unwrap()` : « je suis sûr qu'il n'y a pas d'erreur ; s'il y en a une, arrête tout ». Acceptable dans un test, à éviter dans le vrai code.
- `r#"..."#` : une chaîne « brute », dans laquelle on peut mettre des `"` sans les échapper. Pratique pour le JSON.
- Le faux token `"123:faux"` ne pose pas de problème : ces deux tests sont refusés **avant** tout envoi vers Telegram.

### 9.3 Lancer les tests

Seulement ceux de l'API :

```bash
cargo test -p matheo-api
```

Ceux de tout le workspace :

```bash
cargo test
```

✅ Tu dois voir `test result: ok. 2 passed`.

---

## Étape 10 — Récapitulatif et bonnes pratiques

### 10.1 `crates/matheo/src/main.rs` complet

```rust
mod config;

use matheo_telegram::Messager;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Affiche les logs de niveau "info" et plus graves dans le terminal.
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    // 1. Configuration
    let config = config::Config::from_env()?;
    let messager = Messager::new(config.telegram_token, config.chat_id);

    // 2. Message de démarrage
    messager.envoyer("🤖 M.A.T.H.E.O est en ligne !").await?;

    // 3. Tâches quotidiennes
    let _planificateur = matheo_scheduler::demarrer(messager.clone()).await?;

    // 4. API, en arrière-plan
    matheo_api::demarrer(config.api_addr, messager.clone(), config.api_key).await?;

    // 5. Commandes Telegram (bloque jusqu'à Ctrl+C)
    messager.ecouter_commandes().await;

    Ok(())
}
```

Remarque : `main` est court et ne contient **aucune logique**. Il lit la config et branche les crates entre elles. C'est exactement le rôle d'un binaire dans un workspace.

### 10.2 Organisation finale

```text
M.A.T.H.E.O/
├── Cargo.toml                    ← workspace : membres + versions des dépendances
├── Cargo.lock                    ← un seul pour tout le workspace
├── .env
└── crates/
    ├── matheo/                   ← BINAIRE : config + assemblage
    │   └── src/
    │       ├── main.rs
    │       └── config.rs
    ├── matheo-telegram/          ← LIB : Messager + commandes
    │   └── src/
    │       ├── lib.rs
    │       └── commandes.rs      (module privé)
    ├── matheo-api/               ← LIB : POST /notify + tests
    │   └── src/lib.rs
    └── matheo-scheduler/         ← LIB : tâches quotidiennes
        └── src/lib.rs
```

### 10.3 Comment tout tourne en même temps

```text
                         ┌────────────────────────── processus matheo ──────────────────────────┐
                         │                                                                      │
 Toi sur Telegram ──────►│  matheo-telegram : ecouter_commandes → répond aux commandes          │
                         │                                                                      │
 Script / domotique ────►│  matheo-api : POST /notify ─────────────┐                            │
   (HTTP + x-api-key)    │      (tâche lancée par tokio::spawn)    │                            │
                         │                                         ├─► Messager ─► Telegram ───►│──► ton téléphone
                         │  matheo-scheduler : chaque jour à 8 h ──┘                            │
                         │      (en arrière-plan)                                               │
                         └──────────────────────────────────────────────────────────────────────┘
```

Les trois parties partagent le même `Messager` (cloné), et Tokio les fait avancer en parallèle dans **un seul programme**.

### 10.4 Les bonnes pratiques d'un workspace

1. **Un `Cargo.toml` racine « virtuel »** (`[workspace]` sans `[package]`) et toutes les crates dans `crates/`.
2. **Les versions dans `[workspace.dependencies]`**, et `nom.workspace = true` dans les crates. Une version = une ligne à changer.
3. **Les réglages communs dans `[workspace.package]`** (`version`, `edition`…), hérités avec `xxx.workspace = true`.
4. **Un préfixe commun** pour les noms (`matheo-…`) : on voit tout de suite ce qui vient du projet.
5. **Le binaire assemble, les bibliothèques font le travail.** Seul le binaire lit la configuration ; les bibliothèques reçoivent tout en paramètre. Elles restent faciles à tester et à réutiliser.
6. **Exposer le minimum** : peu d'éléments `pub` par crate (`Messager`, `demarrer`). Le reste est privé et peut changer librement.
7. **Pas de cycles** : les dépendances vont toujours dans le même sens (Cargo te l'impose de toute façon).
8. **Chaque crate a ses tests** et se teste seule avec `cargo test -p <crate>`.
9. **On commite `Cargo.lock`** pour un projet qui produit un programme : tout le monde compile alors avec exactement les mêmes versions.

### 10.5 Aide-mémoire des commandes

| Je veux… | Commande |
|---|---|
| Lancer le programme | `cargo run` |
| Créer une bibliothèque | `cargo new crates/matheo-xxx --lib --vcs none` |
| Ajouter une dépendance à une crate | `cargo add <nom> -p <crate>` (après l'avoir déclarée dans le `Cargo.toml` racine) |
| Ajouter une dépendance de test | `cargo add <nom> -p <crate> --dev` |
| Vérifier une seule crate | `cargo check -p <crate>` |
| Tester une seule crate | `cargo test -p <crate>` |
| Tout tester | `cargo test` |
| Voir l'arbre des dépendances | `cargo tree -p <crate> --depth 1` |

---

## Aller plus loin

Idées, de la plus simple à la plus ambitieuse :

1. **Réserver le bot à toi seul.** Pour l'instant, n'importe qui trouvant ton bot peut lui envoyer `/ping`. Dans `repondre`, compare `msg.chat.id` à ton `chat_id` et ignore les autres. (Indice : il faudra faire passer le `chat_id` du `Messager` jusqu'à `repondre`.)
2. **Une commande avec argument**, ex. `/rappel acheter du pain`. Dans l'enum : `Rappel(String)`. teloxide met le texte après la commande dans le `String`.
3. **Une crate `matheo-meteo`** : appeler une API météo (crate `reqwest`) et envoyer la prévision dans la tâche de 8 h. Bon exercice pour refaire seul toute la marche à suivre d'une nouvelle crate.
4. **Une crate `matheo-core`** pour la logique métier (liste de courses, rappels…), **sans aucune dépendance à Telegram ni à HTTP**. Les autres crates l'utilisent, et elle se teste très facilement.
5. **Garder des données** dans un fichier JSON avec `serde_json`, ou dans une base SQLite avec `sqlx`.
6. **Un deuxième binaire**, par exemple un outil en ligne de commande `matheo-cli` qui réutilise les mêmes crates. Il faudra alors préciser lequel lancer : `cargo run -p matheo`.
7. **Le faire tourner en permanence** : sur un Raspberry Pi ou un petit serveur Linux. `cargo build --release` produit un exécutable optimisé dans `target/release/`. Sous Linux, il faudra installer `libssl-dev` (utilisé par teloxide) avant de compiler.

Pour apprendre Rust plus en profondeur : **« The Rust Programming Language »** (gratuit, en ligne : https://doc.rust-lang.org/book/). Les chapitres 3 à 9 couvrent les bases, et le chapitre 14 parle des workspaces.

---

## Problèmes fréquents

| Symptôme | Cause probable / solution |
|---|---|
| `Error: TELEGRAM_BOT_TOKEN manque dans .env` | Le fichier `.env` est absent ou n'est pas à la racine du workspace (à côté du `Cargo.toml` racine). |
| `Error: ... Unauthorized` au démarrage | Token Telegram incorrect. Recopie-le depuis @BotFather. |
| `Error: ... chat not found` | `TELEGRAM_CHAT_ID` incorrect, ou tu n'as jamais écrit au bot. Envoie-lui un message puis refais l'étape 2.2. |
| `Error: ... Address already in use` / `os error 10048` | Le port 3000 est pris (souvent par une autre instance du bot encore ouverte). Ferme-la ou change `API_ADDR`. |
| `TerminatedByOtherGetUpdates` dans les logs | Deux instances du bot tournent en même temps. N'en garde qu'une. |
| `failed to resolve: use of unresolved module or unlinked crate 'xxx'` | La crate n'a pas cette dépendance. Fais `cargo add xxx -p <crate>`. Rappel : dans le code, les `-` deviennent des `_`. |
| Dans le `Cargo.toml` d'une crate, `cargo add` a écrit une version (`teloxide = "0.17.0"`) au lieu de `teloxide.workspace = true`. Erreurs du genre `cannot find derive macro BotCommands` | La dépendance n'était pas déclarée dans `[workspace.dependencies]` du `Cargo.toml` racine, donc Cargo l'a ajoutée **sans ses features** (`macros`, `derive`…). Supprime la ligne, déclare la dépendance à la racine, puis refais `cargo add`. |
| `cargo add matheo-xxx -p ...` : `could not find matheo-xxx in registry` | Ta crate n'est pas déclarée dans `[workspace.dependencies]` avec son `path = "crates/matheo-xxx"`. |
| `error: 'crates/xxx/' does not have a commit checked out` en faisant `git add` | `cargo new` a créé un dépôt Git dans la crate. Supprime le dossier caché `crates/xxx/.git`, et utilise `--vcs none` la prochaine fois. |
| `cyclic package dependency` | Deux crates dépendent l'une de l'autre. Sors le code commun dans une troisième crate dont elles dépendent toutes les deux. |
| `struct ... is private` / `function ... is private` | Tu utilises depuis une autre crate un élément sans `pub`. Rends-le `pub`, ou mieux : expose une fonction publique qui fait le travail. |
| `use of moved value` | Une valeur a été donnée (déplacée) puis réutilisée. Ajoute un `.clone()` avant de la donner (étape 1.8). |
| `non-exhaustive patterns` | Un `match` ne gère pas tous les cas d'un enum. Ajoute la branche manquante. |
| L'API répond `401` | L'en-tête `x-api-key` est absent ou ne correspond pas à `API_KEY` du `.env`. |
| L'API répond `422` | Le JSON est mal formé ou il manque le champ `message`. |
| La tâche de 8 h ne part pas | Le programme doit tourner à 8 h ! Teste avec `*/20 * * * * *`. |
| La compilation est très longue | Normal la première fois. Ensuite, utilise `cargo check` (ou `cargo check -p <crate>`) pour vérifier rapidement. |
