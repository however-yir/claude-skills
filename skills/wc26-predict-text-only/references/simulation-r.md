# simulation-r.md

Use these exact file contents when reconstructing the WC26 text-only project.

## File: `elo/simulation.R`

```r
# ============================================================
# simulation.R — Reine Simulations-Logik (Daten + Funktionen)
# ============================================================
# Diese Datei enthält den kompletten Berechnungskern der WM-Simulation.
# Sie wird von app.R gesourct (für UI/Server) UND einmalig beim Start
# jedes Future-Workers geladen. Dadurch müssen die ~49 MB an Funktionen
# und Daten NICHT mehr bei jedem future_promise-Aufruf an die Worker
# übertragen werden — das war die Ursache der RAM-Explosion unter Last.
#
# WICHTIG: Diese Datei darf KEINEN Shiny-Code enthalten und muss als
# Arbeitsverzeichnis das App-Verzeichnis haben (wegen der ../data-Pfade).
# ============================================================

library(dplyr)

`%||%` <- function(a, b) if (!is.null(a) && length(a) > 0) a else b

# ── DATA ─────────────────────────────────────────────────────

matches <- read.csv("../data/matches.csv", stringsAsFactors = FALSE)
teams_init <- read.csv("../data/teams.csv", stringsAsFactors = FALSE)

if (!"team_name_de" %in% names(teams_init)) {
  teams_init$team_name_de <- teams_init$team_name
}

##### PLAYED MATCHES (fixed results) #####
results_path <- "../data/cache/results.tsv"

load_played_results <- function() {
  if (file.exists(results_path)) {
    read.delim(results_path, sep="\t", header=TRUE, stringsAsFactors=FALSE)
  } else {
    data.frame(stage=character(), home_id=integer(), away_id=integer(),
               home_goals=integer(), away_goals=integer(),
               pens_winner_id=integer(), stringsAsFactors=FALSE)
  }
}
played_results <- load_played_results()
# Order-insensitive lookup: matches (h,a) and (a,h) the same way.
lookup_result <- function(stage_name, id_a, id_b) {
  hit <- played_results[
    played_results$stage == stage_name &
      ((played_results$home_id == id_a & played_results$away_id == id_b) |
         (played_results$home_id == id_b & played_results$away_id == id_a)), ]
  if (nrow(hit) == 0) return(NULL)
  hit[1, ]
}

##### End of check of existing results #####
# ── 中文国家名（按 FIFA 代码映射）──────────────────────────
# 仅用于 UI 展示。英文 team_name 保留给 ELO 数据匹配使用。
team_name_de_map <- c(
  MEX="墨西哥", RSA="南非", KOR="韩国", CZE="捷克",
  CAN="加拿大", BIH="波黑", QAT="卡塔尔", SUI="瑞士",
  BRA="巴西", MAR="摩洛哥", HAI="海地", SCO="苏格兰",
  USA="美国", PAR="巴拉圭", AUS="澳大利亚", TUR="土耳其",
  GER="德国", CUR="库拉索", CIV="科特迪瓦", ECU="厄瓜多尔",
  NED="荷兰", JPN="日本", SWE="瑞典", TUN="突尼斯",
  BEL="比利时", EGY="埃及", IRN="伊朗", NZL="新西兰",
  ESP="西班牙", CPV="佛得角", KSA="沙特阿拉伯", URU="乌拉圭",
  FRA="法国", SEN="塞内加尔", IRQ="伊拉克", NOR="挪威",
  ARG="阿根廷", ALG="阿尔及利亚", AUT="奥地利", JOR="约旦",
  POR="葡萄牙", COD="刚果（金）", UZB="乌兹别克斯坦", COL="哥伦比亚",
  ENG="英格兰", CRO="克罗地亚", GHA="加纳", PAN="巴拿马"
)

teams_init <- teams_init %>%
  mutate(team_name_de = ifelse(fifa_code %in% names(team_name_de_map),
                               team_name_de_map[fifa_code],
                               team_name))   # fallback: englischer Name

# ── 淘汰赛阶段中文映射（仅用于 UI）─────────────────────────
# 内部 stage 字符串保持英文，以兼容 results.tsv。
stage_de_map <- c(
  "Group"         = "小组赛",
  "Round of 32"   = "32强",
  "Round of 16"   = "16强",
  "Quarter-Final" = "1/4决赛",
  "Semi-Final"    = "半决赛",
  "Third Place"   = "季军赛",
  "Final"         = "决赛"
)

# Flag emoji lookup
flag_map <- c(MEX="🇲🇽",RSA="🇿🇦",KOR="🇰🇷",CZE="🇨🇿",CAN="🇨🇦",BIH="🇧🇦",QAT="🇶🇦",
              SUI="🇨🇭",BRA="🇧🇷",MAR="🇲🇦",HAI="🇭🇹",SCO="🏴󠁧󠁢󠁳󠁣󠁴󠁿",USA="🇺🇸",PAR="🇵🇾",
              AUS="🇦🇺",TUR="🇹🇷",GER="🇩🇪",CUR="🇨🇼",CIV="🇨🇮",ECU="🇪🇨",NED="🇳🇱",
              JPN="🇯🇵",SWE="🇸🇪",TUN="🇹🇳",BEL="🇧🇪",EGY="🇪🇬",IRN="🇮🇷",NZL="🇳🇿",
              ESP="🇪🇸",CPV="🇨🇻",KSA="🇸🇦",URU="🇺🇾",FRA="🇫🇷",SEN="🇸🇳",IRQ="🇮🇶",
              NOR="🇳🇴",ARG="🇦🇷",ALG="🇩🇿",AUT="🇦🇹",JOR="🇯🇴",POR="🇵🇹",COD="🇨🇩",
              UZB="🇺🇿",COL="🇨🇴",ENG="🏴󠁧󠁢󠁥󠁮󠁧󠁿",CRO="🇭🇷",GHA="🇬🇭",PAN="🇵🇦")

get_flag <- function(code) { ifelse(is.na(flag_map[code]), "🏳️", flag_map[code]) }


hist_score_dist <- read.csv("../data/score_dist.csv", stringsAsFactors = FALSE)

# Sample a score from historical distribution.
# p_fav  : favourite's ELO win probability (>= 0.5 always — caller must ensure this)
# outcome: "fav_win" | "draw" | "und_win"
# Returns list(fav_goals, und_goals)
sample_hist_score <- function(p_fav, sim_outcome) {
  # Find bin — p_fav is always in [0.5, 1.0]; the top bin uses include.lowest
  bin_row <- hist_score_dist %>%
    filter(outcome == sim_outcome,
           p_lo <= p_fav, p_fav < p_hi)

  # Edge case: p_fav == 1.0 → use top bin
  if (nrow(bin_row) == 0) {
    bin_row <- hist_score_dist %>%
      filter(outcome == csv_outcome, p_hi == max(p_hi))
  }

  if (nrow(bin_row) == 0) return(NULL)   # fallback signal

  idx       <- sample(nrow(bin_row), 1, prob = bin_row$prob)
  fav_goals <- bin_row$fav_goals[idx]   # "home" ≡ favourite in the CSV
  und_goals <- bin_row$und_goals[idx]
  list(fav_goals = fav_goals, und_goals = und_goals)
}

# ── SIMULATION PARAMETERS ────────────────────────────────────
# Zentraler Container für alle Tuning-Parameter der Simulation.
# Defaults = aktuelles Verhalten der App (vor Einführung der Schalter).
# Wird durch die ganze Aufrufkette gereicht, damit keine Funktion
# eine lange Argumentliste braucht.
default_params <- list(
  k                 = 60,    # ELO-Lerngeschwindigkeit
  use_historical    = FALSE, # FALSE = Poisson, TRUE = empirische Tor-Verteilung
  home_advantage    = 0,     # ELO-Bonus für USA/CAN/MEX (0 = kein Heimvorteil)
  team_boost_id     = NA,    # team$id der Mannschaft, die den Bonus erhält
  team_boost_value  = 0,     # ELO-Bonus für das gewählte Team
  team_adjustments  = NULL,  # named numeric vector (id → ELO-Offset/Differenz) aus der ELO-Rangliste
  goal_scale        = 1.0,   # Multiplikator auf Poisson-λ (1 = original)
  draw_max          = 0.3,   # max. Wahrscheinlichkeit eines Unentschieden bei p_h = 0.5 (ELO-Gleichstand); einheitlich mit UI-Default & Fallback in app.R
  upset_factor      = 1.0,   # interner Multiplikator: 1 = neutral, <1 = Außenseiter begünstigt, >1 = Favoriten begünstigt
                             # UI zeigt diesen Wert als (1 - upset_factor); Slider-Bereich -3 bis +3 entspricht intern 4 bis -2
  prediction_model        = "elo", # "elo" = bisherige ELO-Simulation, "dixon_coles" = DC-Tormatrizen
  dc_host_factor          = 1.0,   # Multiplikator auf den host-Koeffizienten des DC-Modells (1 = original, 0 = aus)
  dc_intercept_delta      = 0,     # Δ auf den Intercept (globales Torniveau, log-Skala)
  dc_attack_values        = NULL,  # named numeric (id → absoluter Slider-Wert 0–2.5, entspricht exp(attack_log))
  dc_defense_values       = NULL   # named numeric (id → absoluter Slider-Wert 0–2.5, entspricht exp(defense_log))
)

# Wendet die ELO-Modifier (Heimvorteil + Team-Boost + Per-Team-Adjustments)
# auf den Mannschaftsdataframe an. Wird einmal pro Turnier vor Anpfiff gerufen.
apply_elo_modifiers <- function(teams_df, params) {
  if (params$home_advantage != 0) {
    hosts <- c("USA", "CAN", "MEX")
    teams_df <- teams_df %>%
      mutate(elo = ifelse(fifa_code %in% hosts,
                          elo + params$home_advantage, elo))
  }
  if (!is.na(params$team_boost_id) && params$team_boost_value != 0) {
    teams_df <- teams_df %>%
      mutate(elo = ifelse(id == params$team_boost_id,
                          elo + params$team_boost_value, elo))
  }
  # Per-Team-Adjustments aus der ELO-Rangliste (additiv zu den anderen Modifiern).
  # Werte sind Differenzen (Slider-Wert minus Original-Start-ELO).
  if (!is.null(params$team_adjustments) && length(params$team_adjustments) > 0) {
    adj <- params$team_adjustments
    adj <- adj[!is.na(adj) & adj != 0]
    if (length(adj) > 0) {
      adj_df <- data.frame(id = as.integer(names(adj)),
                           .adj = as.numeric(adj),
                           stringsAsFactors = FALSE)
      teams_df <- teams_df %>%
        left_join(adj_df, by = "id") %>%
        mutate(elo = elo + ifelse(is.na(.adj), 0, .adj)) %>%
        select(-.adj)
    }
  }
  teams_df
}

# ── DIXON-COLES ENGINE ───────────────────────────────────────

dc_model_path <- "../dc/dc_model.rds"
dc_model_fit  <- NULL
dc_prob_cache <- new.env(parent = emptyenv())

# Aktives DC-Modell mit aktuell angewendeten User-Overrides.
# Wird zu Beginn jedes run_tournament-Aufrufs gesetzt (siehe dort).
# Bleibt NULL, solange keine Simulation läuft (UI nutzt dann load_dc_model()).
dc_active_model <- NULL

dc_available <- function() {
  file.exists(dc_model_path) && requireNamespace("goalmodel", quietly = TRUE)
}

load_dc_model <- function() {
  if (!dc_available()) {
    stop("Dixon-Coles-Modell nicht verfügbar. Bitte goalmodel installieren und ../dc/dc_model.rds bereitstellen.")
  }
  if (is.null(dc_model_fit)) {
    dc_model_fit <<- readRDS(dc_model_path)
  }
  dc_model_fit
}

# Wendet die User-Slider-Werte als additive Offsets (log-Skala) auf eine
# Kopie des gefitteten Modells an. Globale Parameter (hfa, rho, intercept)
# und per-Team-Parameter (attack, defense) werden separat behandelt.
# Rückgabewert: identische Struktur wie das Original; nur $parameters wird ersetzt.
apply_dc_overrides <- function(model_fit, params) {
  m <- model_fit
  p <- m$parameters
  
  if (!is.null(params$dc_host_factor) && !is.null(p$beta) && "host" %in% names(p$beta)) {
    f <- as.numeric(params$dc_host_factor)
    if (!is.na(f) && f != 1) {
      p$beta[["host"]] <- p$beta[["host"]] * f
    }
  }
  if (!is.null(params$dc_intercept_delta) && isTRUE(params$dc_intercept_delta != 0) && !is.null(p$intercept)) {
    p$intercept <- p$intercept + as.numeric(params$dc_intercept_delta)
  }
  
  # Per-Team-Slider liefern direkt die log-skalierten Modellparameter
  # (attack bzw. defense). Range −5 bis +5. Slider = Originalwert ⇒
  # Modell unverändert. Höheres attack = offensiver; höheres defense =
  # bessere Abwehr (goalmodel-Konvention, NICHT invertiert).
  apply_abs <- function(param_vec, abs_values) {
    if (is.null(abs_values) || length(abs_values) == 0) return(param_vec)
    abs_values <- abs_values[!is.na(abs_values)]
    if (length(abs_values) == 0) return(param_vec)
    nm_match <- intersect(names(abs_values), names(param_vec))
    if (length(nm_match) == 0) return(param_vec)
    for (k in nm_match) {
      param_vec[k] <- as.numeric(abs_values[[k]])
    }
    param_vec
  }
  
  if (!is.null(p$attack))  p$attack  <- apply_abs(p$attack,  params$dc_attack_values)
  if (!is.null(p$defense)) p$defense <- apply_abs(p$defense, params$dc_defense_values)
  
  m$parameters <- p
  m
}

get_dc_prob_matrix <- function(id_home, id_away) {
  if (is.null(id_home) || is.null(id_away) || is.na(id_home) || is.na(id_away)) {
    stop("Dixon-Coles benötigt gültige Team-IDs.")
  }
  
  key <- paste0(id_home, "_", id_away)
  if (exists(key, envir = dc_prob_cache, inherits = FALSE)) {
    return(get(key, envir = dc_prob_cache, inherits = FALSE))
  }
  
  # Während einer Turnier-Simulation: das (ggf. modifizierte) aktive Modell nutzen.
  # Außerhalb (z.B. wenn die DC-Funktionen für UI-Vorschauen direkt gerufen werden):
  # auf das Originalmodell zurückfallen.
  model_fit <- if (!is.null(dc_active_model)) dc_active_model else load_dc_model()
  host_ids  <- c(1L, 5L, 13L) # USA, Kanada, Mexiko
  x1 <- matrix(c(0, as.integer(id_home %in% host_ids), 0), ncol = 3)
  x2 <- matrix(c(as.integer(id_away %in% host_ids), 0), ncol = 2)
  colnames(x1) <- c("home", "host", "friendly")
  colnames(x2) <- c("host", "friendly")

  mat <- goalmodel::predict_goals(
    model_fit,
    team1 = id_home,
    team2 = id_away,
    maxgoal = 10,
    return_df = FALSE,
    x1 = x1,
    x2 = x2
  )
  if (is.list(mat)) mat <- mat[[1]]
  if (!is.matrix(mat) || any(is.na(mat))) {
    stop("Dixon-Coles konnte keine gültige Tormatrix berechnen für ", id_home, " vs ", id_away, ".")
  }
  # Extreme ρ-Werte können einzelne Zellen der Tau-Korrektur negativ werden lassen.
  # Vor der Normalisierung clampen, sonst füttert sample.int() negative
  # Wahrscheinlichkeiten und löscht den Worker.
  mat[mat < 0] <- 0
  s <- sum(mat)
  if (s <= 0) {
    stop("Dixon-Coles konnte keine gültige Tormatrix berechnen für ", id_home, " vs ", id_away, ".")
  }
  mat <- mat / s
  assign(key, mat, envir = dc_prob_cache)
  mat
}

sample_dc_score <- function(id_home, id_away) {
  mat <- get_dc_prob_matrix(id_home, id_away)
  probs <- as.vector(mat)
  idx <- sample.int(length(probs), 1, prob = probs)
  n_home <- nrow(mat)
  home_goals <- (idx - 1) %% n_home
  away_goals <- (idx - 1) %/% n_home
  list(home_goals = home_goals, away_goals = away_goals, matrix = mat)
}

simulate_match_dc <- function(id_home, id_away, elo_home, elo_away) {
  sc <- sample_dc_score(id_home, id_away)
  outcome <- if (sc$home_goals > sc$away_goals) "home"
  else if (sc$home_goals < sc$away_goals) "away"
  else "draw"

  mat <- sc$matrix
  home_win_prob <- sum(mat[row(mat) > col(mat)])

  list(home_goals    = sc$home_goals,
       away_goals    = sc$away_goals,
       outcome       = outcome,
       new_elo_home  = elo_home,
       new_elo_away  = elo_away,
       pen_home_prob = home_win_prob)
}

dc_home_win_probability <- function(id_home, id_away) {
  mat <- get_dc_prob_matrix(id_home, id_away)
  sum(mat[row(mat) > col(mat)])
}

# ── ELO ENGINE ───────────────────────────────────────────────

elo_expected <- function(ea, eb) 1 / (1 + 10^((eb - ea) / 400))

simulate_match_elo <- function(elo_home, elo_away,
                               params = default_params,
                               force_gh = NULL, force_ga = NULL) {

  # ── Fixed result (real, already-played match): bypass simulation ──
  # ELO is NOT updated here — update_elo.R already reflects this match
  # in the cache, so updating again would double-count.
  if (!is.null(force_gh) && !is.null(force_ga)) {
    outcome <- if (force_gh > force_ga) "home"
    else if (force_gh < force_ga) "away"
    else "draw"
    return(list(home_goals    = force_gh,
                away_goals    = force_ga,
                outcome       = outcome,
                new_elo_home  = elo_home,
                new_elo_away  = elo_away))
  }

  # Raw win probability (für ELO-Update später unverändert nötig)
  p_raw <- elo_expected(elo_home, elo_away)

  # ── Underdog-Faktor: skaliert die Abweichung von 50/50 ──
  # 1.0 = original, 0 = alle Spiele 50/50, 2 = doppelt so deutliche Favoriten
  p_h <- 0.5 + (p_raw - 0.5) * params$upset_factor
  p_h <- min(max(p_h, 0.001), 0.999)

  # ── Unentschieden-Häufigkeit ──
  # Glockenkurve um p_h = 0.5 (ELO-Gleichstand). params$draw_max ist die
  # maximale Wahrscheinlichkeit für ein Unentschieden bei p_h = 0.5; mit
  # zunehmender Abweichung (eindeutigerer Favorit) fällt die Draw-WK gauss-
  # förmig gegen 0. Sigma steuert die Breite der Glocke und bleibt fix.
  sigma  <- .3#0.236875
  draw_p <- params$draw_max * exp(-((p_h - 0.5)^2) / (2 * sigma^2))
  ph <- p_h * (1 - draw_p)
  pa <- (1 - p_h) * (1 - draw_p)

  outcome <- sample(c("home", "draw", "away"), 1, prob = c(ph, draw_p, pa))

  # ── Neutral-ground symmetry: work in favourite / underdog space ──
  # p_h >= 0.5  =>  home team is the favourite; otherwise away is.
  home_is_fav <- (p_h >= 0.5)
  p_fav       <- if (home_is_fav) p_h else (1 - p_h)

  # Translate raw outcome to favourite-space label used by the CSV lookup
  sim_outcome <- if (outcome == "draw") {
    "draw"
  } else if ((outcome == "home") == home_is_fav) {
    "fav_win"
  } else {
    "und_win"
  }

  used_historical <- FALSE
  if (params$use_historical) {
    sc <- sample_hist_score(p_fav, sim_outcome)
    if (!is.null(sc)) {
      # Map favourite/underdog goals back to the actual home/away teams
      gh <- if (home_is_fav) sc$fav_goals else sc$und_goals
      ga <- if (home_is_fav) sc$und_goals else sc$fav_goals
      used_historical <- TRUE
    }
  }

  if (!used_historical) {
    # ── Poisson score sampling (original / fallback) ───────
    # Torreichtum: Multiplikator auf Lambda (1 = original WM-Niveau)
    lh <- (1.99419 * p_h + 0.24629) * params$goal_scale
    la <- (1.99419 * (1-p_h) + 0.24629) * params$goal_scale
    repeat {
      gh <- rpois(1, lh); ga <- rpois(1, la)
      if (outcome == "home" && gh > ga) break
      if (outcome == "away" && ga > gh) break
      if (outcome == "draw" && gh == ga) break
    }
  }

  act_h    <- ifelse(outcome == "home", 1, ifelse(outcome == "draw", 0.5, 0))
  exp_h    <- p_raw                                # ELO-Update mit Roh-Probability
  goal_diff <- abs(gh - ga)
  k_mult   <- if (goal_diff <= 1) 1
  else if (goal_diff == 2) 1.5
  else if (goal_diff == 3) 1.75
  else 1.75 + (goal_diff - 3) / 8
  k_adj <- params$k * k_mult

  list(home_goals    = gh,
       away_goals    = ga,
       outcome       = outcome,
       new_elo_home  = elo_home + k_adj * (act_h - exp_h),
       new_elo_away  = elo_away + k_adj * ((1 - act_h) - (1 - exp_h)))
}

simulate_match <- function(elo_home, elo_away,
                           params = default_params,
                           force_gh = NULL, force_ga = NULL,
                           id_home = NULL, id_away = NULL) {

  # Bereits gespielte Partien bleiben modellunabhängig fix.
  if (!is.null(force_gh) && !is.null(force_ga)) {
    return(simulate_match_elo(elo_home, elo_away, params = params,
                              force_gh = force_gh, force_ga = force_ga))
  }

  if (identical(params$prediction_model, "dixon_coles")) {
    return(simulate_match_dc(id_home, id_away, elo_home, elo_away))
  }

  simulate_match_elo(elo_home, elo_away, params = params)
}

# ── FIFA TIEBREAKER ──────────────────────────────────────────
# FIFA group-stage tiebreakers in order:
#   1. Points (overall)
#   2. Goal difference (overall)
#   3. Goals scored (overall)
#   4. Points in matches between tied teams (head-to-head)
#   5. Goal difference in head-to-head matches
#   6. Goals scored in head-to-head matches
# Final fallback (substitute for FIFA's "fair play" / "drawing
# of lots", which we cannot simulate): ELO.
rank_group_fifa <- function(standing, raw_matches) {
  standing <- standing %>%
    arrange(desc(pts), desc(gd), desc(gf)) %>%
    mutate(tie_key = paste(pts, gd, gf, sep = "_"))

  resolved <- lapply(unique(standing$tie_key), function(tk) {
    sub <- standing %>% filter(tie_key == tk)
    if (nrow(sub) == 1) return(sub)

    tied_ids <- sub$id
    h2h <- raw_matches %>%
      filter(home_id %in% tied_ids, away_id %in% tied_ids)

    h2h_pts <- h2h_gf <- h2h_ga <-
      setNames(rep(0, length(tied_ids)), as.character(tied_ids))

    for (i in seq_len(nrow(h2h))) {
      h  <- as.character(h2h$home_id[i])
      a  <- as.character(h2h$away_id[i])
      gh <- h2h$home_goals[i]
      ga_ <- h2h$away_goals[i]
      h2h_gf[h] <- h2h_gf[h] + gh
      h2h_ga[h] <- h2h_ga[h] + ga_
      h2h_gf[a] <- h2h_gf[a] + ga_
      h2h_ga[a] <- h2h_ga[a] + gh
      if      (gh >  ga_) h2h_pts[h] <- h2h_pts[h] + 3
      else if (gh <  ga_) h2h_pts[a] <- h2h_pts[a] + 3
      else { h2h_pts[h] <- h2h_pts[h] + 1; h2h_pts[a] <- h2h_pts[a] + 1 }
    }

    sub %>%
      mutate(h2h_pts = as.numeric(h2h_pts[as.character(id)]),
             h2h_gd  = as.numeric(h2h_gf[as.character(id)] -
                                    h2h_ga[as.character(id)]),
             h2h_gf  = as.numeric(h2h_gf[as.character(id)])) %>%
      arrange(desc(h2h_pts), desc(h2h_gd), desc(h2h_gf), desc(elo)) %>%
      select(-h2h_pts, -h2h_gd, -h2h_gf)
  })

  bind_rows(resolved) %>%
    select(-tie_key) %>%
    mutate(rank = row_number())
}

# ── GROUP STAGE ──────────────────────────────────────────────

run_group_stage <- function(teams_df, params = default_params) {
  elo_start <- setNames(teams_df$elo, teams_df$id)
  elo_live  <- elo_start

  all_matches   <- data.frame()
  all_standings <- data.frame()

  for (grp in sort(unique(teams_df$group_letter))) {
    ids   <- teams_df %>% filter(group_letter == grp) %>% pull(id)
    pairs <- combn(ids, 2, simplify = FALSE)
    pts <- gf <- ga <- setNames(rep(0, 4), ids)
    raw_grp_matches <- data.frame(home_id    = integer(),
                                  away_id    = integer(),
                                  home_goals = integer(),
                                  away_goals = integer())

    for (pair in pairs) {
      h <- pair[1]; a <- pair[2]

      elo_h <- elo_live[as.character(h)]
      elo_a <- elo_live[as.character(a)]

      # Already played? Use the real result instead of simulating.
      fixed <- lookup_result("Group", h, a)
      if (!is.null(fixed)) {
        if (fixed$home_id == h) {
          fgh <- fixed$home_goals; fga <- fixed$away_goals
        } else {
          fgh <- fixed$away_goals; fga <- fixed$home_goals
        }
        res <- simulate_match(elo_h, elo_a, params = params,
                              force_gh = fgh, force_ga = fga,
                              id_home = h, id_away = a)
      } else {
        res <- simulate_match(elo_h, elo_a, params = params,
                              id_home = h, id_away = a)
      }
      elo_live[as.character(h)] <- res$new_elo_home
      elo_live[as.character(a)] <- res$new_elo_away

      gf[as.character(h)] <- gf[as.character(h)] + res$home_goals
      ga[as.character(h)] <- ga[as.character(h)] + res$away_goals
      gf[as.character(a)] <- gf[as.character(a)] + res$away_goals
      ga[as.character(a)] <- ga[as.character(a)] + res$home_goals

      if      (res$outcome == "home") pts[as.character(h)] <- pts[as.character(h)] + 3
      else if (res$outcome == "away") pts[as.character(a)] <- pts[as.character(a)] + 3
      else {
        pts[as.character(h)] <- pts[as.character(h)] + 1
        pts[as.character(a)] <- pts[as.character(a)] + 1
      }

      raw_grp_matches <- rbind(raw_grp_matches, data.frame(
        home_id = h, away_id = a,
        home_goals = res$home_goals, away_goals = res$away_goals))

      ht <- teams_df %>% filter(id == h)
      at <- teams_df %>% filter(id == a)
      all_matches <- rbind(all_matches, data.frame(
        stage  = "Group", group = grp,
        home   = paste(get_flag(ht$fifa_code), ht$team_name_de),
        away   = paste(get_flag(at$fifa_code), at$team_name_de),
        score  = paste0(res$home_goals, "-", res$away_goals),
        result = res$outcome, stringsAsFactors = FALSE))
    }

    standing <- data.frame(id = ids, pts = as.numeric(pts),
                           gf = as.numeric(gf), ga = as.numeric(ga)) %>%
      mutate(gd = gf - ga, elo = elo_live[as.character(ids)]) %>%
      arrange(desc(pts), desc(gd), desc(gf), desc(elo)) %>%
      mutate(rank = 1:4, group = grp) %>%
      left_join(teams_df %>% select(id, team_name_de, fifa_code), by = "id")
    all_standings <- rbind(all_standings, standing)
  }
  list(standings = all_standings, matches = all_matches, elo_live = elo_live)
}

# ── KNOCKOUT ─────────────────────────────────────────────────

sim_ko_match <- function(id_a, id_b, elo_live, teams_df,
                         round_name, params = default_params) {
  elo_h <- elo_live[as.character(id_a)]
  elo_a <- elo_live[as.character(id_b)]

  # Already played? Use the real result instead of simulating.
  fixed <- lookup_result(round_name, id_a, id_b)
  if (!is.null(fixed)) {
    if (fixed$home_id == id_a) {
      fgh <- fixed$home_goals; fga <- fixed$away_goals
    } else {
      fgh <- fixed$away_goals; fga <- fixed$home_goals
    }
    res <- simulate_match(elo_h, elo_a, params = params,
                          force_gh = fgh, force_ga = fga,
                          id_home = id_a, id_away = id_b)
  } else {
    res <- simulate_match(elo_h, elo_a, params = params,
                          id_home = id_a, id_away = id_b)
  }

  pens <- ""
  if (res$outcome == "draw") {
    pens <- " (i. E.)"
    if (!is.null(fixed) && !is.na(fixed$pens_winner_id)) {
      winner <- fixed$pens_winner_id
    } else {
      pa <- if (identical(params$prediction_model, "dixon_coles")) {
        res$pen_home_prob %||% dc_home_win_probability(id_a, id_b)
      } else {
        elo_expected(elo_h, elo_a)
      }
      winner <- ifelse(runif(1) < pa, id_a, id_b)
    }
  } else {
    winner <- ifelse(res$outcome == "home", id_a, id_b)
  }



  loser <- ifelse(winner == id_a, id_b, id_a)

  elo_live[as.character(id_a)] <- res$new_elo_home
  elo_live[as.character(id_b)] <- res$new_elo_away

  ta <- teams_df %>% filter(id == id_a)
  tb <- teams_df %>% filter(id == id_b)
  tw <- teams_df %>% filter(id == winner)
  list(winner = winner, loser = loser, elo_live = elo_live,
       row = data.frame(stage  = round_name, group = "",
                        home   = paste(get_flag(ta$fifa_code), ta$team_name_de),
                        away   = paste(get_flag(tb$fifa_code), tb$team_name_de),
                        score  = paste0(res$home_goals, "-", res$away_goals, pens),
                        result = paste("→", get_flag(tw$fifa_code), tw$team_name_de),
                        stringsAsFactors = FALSE))
}

run_knockout <- function(pairs, elo_live, teams_df,
                         round_name, params = default_params) {
  winners <- c(); losers <- c(); rows <- data.frame()
  for (pair in pairs) {
    res      <- sim_ko_match(pair[1], pair[2], elo_live, teams_df,
                             round_name, params = params)
    elo_live <- res$elo_live
    winners  <- c(winners, res$winner)
    losers   <- c(losers,  res$loser)
    rows     <- rbind(rows, res$row)
  }
  list(winners = winners, losers = losers, elo_live = elo_live, matches = rows)
}

# ── TOURNAMENT ───────────────────────────────────────────────

run_tournament <- function(seed = NULL, params = default_params) {
  if (!is.null(seed)) set.seed(seed)
  played_results <<- load_played_results()  # refresh from disk

  # Heimvorteil + Team-Boost + Per-Team-Adjustments VOR Turnierstart aufschlagen
  teams_df <- apply_elo_modifiers(teams_init, params)
  
  # Dixon-Coles: User-Overrides auf das gefittete Modell anwenden und Cache leeren.
  # Außerhalb des DC-Modus bleibt dc_active_model NULL und das Original wird benutzt.
  rm(list = ls(dc_prob_cache, all.names = TRUE), envir = dc_prob_cache)
  dc_active_model <<- if (identical(params$prediction_model, "dixon_coles") && dc_available()) {
    apply_dc_overrides(load_dc_model(), params)
  } else {
    NULL
  }
  
  gs       <- run_group_stage(teams_df, params = params)
  elo_live <- gs$elo_live
  std      <- gs$standings

  thirds <- std %>% filter(rank == 3) %>%
    arrange(desc(pts), desc(gd), desc(gf), desc(elo)) %>% slice(1:8)

  get_t <- function(grp, rnk) std %>% filter(group == grp, rank == rnk) %>% pull(id)

  # ── FIFA WM-2026 Annex C: Zuordnung der Gruppendritten im Sechzehntelfinale ──
  # Welcher Gruppensieger gegen den Dritten WELCHER Gruppe spielt, haengt NICHT
  # vom Rang der Dritten ab, sondern von der KOMBINATION der acht Gruppen, aus
  # denen ein qualifizierter Dritter stammt (C(12,8) = 495 Faelle, Annex C des
  # offiziellen FIFA-Reglements). Schluessel = sortierte 8-Buchstaben-Kombination
  # dieser Gruppen. Wert = 8 Zeichen = Quell-Gruppe des jeweiligen Dritten fuer
  # die Gruppensieger 1A,1B,1D,1E,1G,1I,1K,1L (genau in dieser Reihenfolge).
  # Schliesst ein Wiedersehen aus derselben Gruppe konstruktiv aus.
  annexC <- c(
    "ABCDEFGH"="HGBCAFDE", "ABCDEFGI"="CGBDAFEI", "ABCDEFGJ"="CGBDAFEJ", "ABCDEFGK"="CGBDAFEK", "ABCDEFGL"="CGBDAFLE",
    "ABCDEFHI"="HEBCAFDI", "ABCDEFHJ"="HJBCAFDE", "ABCDEFHK"="HEBCAFDK", "ABCDEFHL"="HFBCADLE", "ABCDEFIJ"="CJBDAFEI",
    "ABCDEFIK"="CEBDAFIK", "ABCDEFIL"="CEBDAFLI", "ABCDEFJK"="CJBDAFEK", "ABCDEFJL"="CJBDAFLE", "ABCDEFKL"="CEBDAFLK",
    "ABCDEGHI"="HGBCADEI", "ABCDEGHJ"="HGBCADEJ", "ABCDEGHK"="HGBCADEK", "ABCDEGHL"="HGBCADLE", "ABCDEGIJ"="EGBCADIJ",
    "ABCDEGIK"="EGBCADIK", "ABCDEGIL"="EGBCADLI", "ABCDEGJK"="EGBCADJK", "ABCDEGJL"="EGBCADLJ", "ABCDEGKL"="EGBCADLK",
    "ABCDEHIJ"="HJBCADEI", "ABCDEHIK"="HEBCADIK", "ABCDEHIL"="HEBCADLI", "ABCDEHJK"="HJBCADEK", "ABCDEHJL"="HJBCADLE",
    "ABCDEHKL"="HEBCADLK", "ABCDEIJK"="EJBCADIK", "ABCDEIJL"="EJBCADLI", "ABCDEIKL"="EIBCADLK", "ABCDEJKL"="EJBCADLK",
    "ABCDFGHI"="HGBCAFDI", "ABCDFGHJ"="HGBCAFDJ", "ABCDFGHK"="HGBCAFDK", "ABCDFGHL"="CGBDAFLH", "ABCDFGIJ"="CGBDAFIJ",
    "ABCDFGIK"="CGBDAFIK", "ABCDFGIL"="CGBDAFLI", "ABCDFGJK"="CGBDAFJK", "ABCDFGJL"="CGBDAFLJ", "ABCDFGKL"="CGBDAFLK",
    "ABCDFHIJ"="HJBCAFDI", "ABCDFHIK"="HFBCADIK", "ABCDFHIL"="HFBCADLI", "ABCDFHJK"="HJBCAFDK", "ABCDFHJL"="CJBDAFLH",
    "ABCDFHKL"="HFBCADLK", "ABCDFIJK"="CJBDAFIK", "ABCDFIJL"="CJBDAFLI", "ABCDFIKL"="CIBDAFLK", "ABCDFJKL"="CJBDAFLK",
    "ABCDGHIJ"="HGBCADIJ", "ABCDGHIK"="HGBCADIK", "ABCDGHIL"="HGBCADLI", "ABCDGHJK"="HGBCADJK", "ABCDGHJL"="HGBCADLJ",
    "ABCDGHKL"="HGBCADLK", "ABCDGIJK"="CJBDAGIK", "ABCDGIJL"="CJBDAGLI", "ABCDGIKL"="IGBCADLK", "ABCDGJKL"="CJBDAGLK",
    "ABCDHIJK"="HJBCADIK", "ABCDHIJL"="HJBCADLI", "ABCDHIKL"="HIBCADLK", "ABCDHJKL"="HJBCADLK", "ABCDIJKL"="IJBCADLK",
    "ABCEFGHI"="HGBCAFEI", "ABCEFGHJ"="HGBCAFEJ", "ABCEFGHK"="HGBCAFEK", "ABCEFGHL"="HGBCAFLE", "ABCEFGIJ"="EGBCAFIJ",
    "ABCEFGIK"="EGBCAFIK", "ABCEFGIL"="EGBCAFLI", "ABCEFGJK"="EGBCAFJK", "ABCEFGJL"="EGBCAFLJ", "ABCEFGKL"="EGBCAFLK",
    "ABCEFHIJ"="HJBCAFEI", "ABCEFHIK"="HEBCAFIK", "ABCEFHIL"="HEBCAFLI", "ABCEFHJK"="HJBCAFEK", "ABCEFHJL"="HJBCAFLE",
    "ABCEFHKL"="HEBCAFLK", "ABCEFIJK"="EJBCAFIK", "ABCEFIJL"="EJBCAFLI", "ABCEFIKL"="EIBCAFLK", "ABCEFJKL"="EJBCAFLK",
    "ABCEGHIJ"="HJBCAGEI", "ABCEGHIK"="EGBCAHIK", "ABCEGHIL"="EGBCAHLI", "ABCEGHJK"="HJBCAGEK", "ABCEGHJL"="HJBCAGLE",
    "ABCEGHKL"="EGBCAHLK", "ABCEGIJK"="EJBCAGIK", "ABCEGIJL"="EJBCAGLI", "ABCEGIKL"="EGBAICLK", "ABCEGJKL"="EJBCAGLK",
    "ABCEHIJK"="EJBCAHIK", "ABCEHIJL"="EJBCAHLI", "ABCEHIKL"="EIBCAHLK", "ABCEHJKL"="EJBCAHLK", "ABCEIJKL"="EJBAICLK",
    "ABCFGHIJ"="HGBCAFIJ", "ABCFGHIK"="HGBCAFIK", "ABCFGHIL"="HGBCAFLI", "ABCFGHJK"="HGBCAFJK", "ABCFGHJL"="HGBCAFLJ",
    "ABCFGHKL"="HGBCAFLK", "ABCFGIJK"="CJBFAGIK", "ABCFGIJL"="CJBFAGLI", "ABCFGIKL"="IGBCAFLK", "ABCFGJKL"="CJBFAGLK",
    "ABCFHIJK"="HJBCAFIK", "ABCFHIJL"="HJBCAFLI", "ABCFHIKL"="HIBCAFLK", "ABCFHJKL"="HJBCAFLK", "ABCFIJKL"="IJBCAFLK",
    "ABCGHIJK"="HJBCAGIK", "ABCGHIJL"="HJBCAGLI", "ABCGHIKL"="IGBCAHLK", "ABCGHJKL"="HJBCAGLK", "ABCGIJKL"="IJBCAGLK",
    "ABCHIJKL"="IJBCAHLK", "ABDEFGHI"="HGBDAFEI", "ABDEFGHJ"="HGBDAFEJ", "ABDEFGHK"="HGBDAFEK", "ABDEFGHL"="HGBDAFLE",
    "ABDEFGIJ"="EGBDAFIJ", "ABDEFGIK"="EGBDAFIK", "ABDEFGIL"="EGBDAFLI", "ABDEFGJK"="EGBDAFJK", "ABDEFGJL"="EGBDAFLJ",
    "ABDEFGKL"="EGBDAFLK", "ABDEFHIJ"="HJBDAFEI", "ABDEFHIK"="HEBDAFIK", "ABDEFHIL"="HEBDAFLI", "ABDEFHJK"="HJBDAFEK",
    "ABDEFHJL"="HJBDAFLE", "ABDEFHKL"="HEBDAFLK", "ABDEFIJK"="EJBDAFIK", "ABDEFIJL"="EJBDAFLI", "ABDEFIKL"="EIBDAFLK",
    "ABDEFJKL"="EJBDAFLK", "ABDEGHIJ"="HJBDAGEI", "ABDEGHIK"="EGBDAHIK", "ABDEGHIL"="EGBDAHLI", "ABDEGHJK"="HJBDAGEK",
    "ABDEGHJL"="HJBDAGLE", "ABDEGHKL"="EGBDAHLK", "ABDEGIJK"="EJBDAGIK", "ABDEGIJL"="EJBDAGLI", "ABDEGIKL"="EGBAIDLK",
    "ABDEGJKL"="EJBDAGLK", "ABDEHIJK"="EJBDAHIK", "ABDEHIJL"="EJBDAHLI", "ABDEHIKL"="EIBDAHLK", "ABDEHJKL"="EJBDAHLK",
    "ABDEIJKL"="EJBAIDLK", "ABDFGHIJ"="HGBDAFIJ", "ABDFGHIK"="HGBDAFIK", "ABDFGHIL"="HGBDAFLI", "ABDFGHJK"="HGBDAFJK",
    "ABDFGHJL"="HGBDAFLJ", "ABDFGHKL"="HGBDAFLK", "ABDFGIJK"="FJBDAGIK", "ABDFGIJL"="FJBDAGLI", "ABDFGIKL"="IGBDAFLK",
    "ABDFGJKL"="FJBDAGLK", "ABDFHIJK"="HJBDAFIK", "ABDFHIJL"="HJBDAFLI", "ABDFHIKL"="HIBDAFLK", "ABDFHJKL"="HJBDAFLK",
    "ABDFIJKL"="IJBDAFLK", "ABDGHIJK"="HJBDAGIK", "ABDGHIJL"="HJBDAGLI", "ABDGHIKL"="IGBDAHLK", "ABDGHJKL"="HJBDAGLK",
    "ABDGIJKL"="IJBDAGLK", "ABDHIJKL"="IJBDAHLK", "ABEFGHIJ"="HJBFAGEI", "ABEFGHIK"="EGBFAHIK", "ABEFGHIL"="EGBFAHLI",
    "ABEFGHJK"="HJBFAGEK", "ABEFGHJL"="HJBFAGLE", "ABEFGHKL"="EGBFAHLK", "ABEFGIJK"="EJBFAGIK", "ABEFGIJL"="EJBFAGLI",
    "ABEFGIKL"="EGBAIFLK", "ABEFGJKL"="EJBFAGLK", "ABEFHIJK"="EJBFAHIK", "ABEFHIJL"="EJBFAHLI", "ABEFHIKL"="EIBFAHLK",
    "ABEFHJKL"="EJBFAHLK", "ABEFIJKL"="EJBAIFLK", "ABEGHIJK"="EJBAHGIK", "ABEGHIJL"="EJBAHGLI", "ABEGHIKL"="EGBAIHLK",
    "ABEGHJKL"="EJBAHGLK", "ABEGIJKL"="EJBAIGLK", "ABEHIJKL"="EJBAIHLK", "ABFGHIJK"="HJBFAGIK", "ABFGHIJL"="HJBFAGLI",
    "ABFGHIKL"="HGBAIFLK", "ABFGHJKL"="HJBFAGLK", "ABFGIJKL"="IJBFAGLK", "ABFHIJKL"="HJBAIFLK", "ABGHIJKL"="HJBAIGLK",
    "ACDEFGHI"="HGECAFDI", "ACDEFGHJ"="HGJCAFDE", "ACDEFGHK"="HGECAFDK", "ACDEFGHL"="HGFCADLE", "ACDEFGIJ"="CGJDAFEI",
    "ACDEFGIK"="CGEDAFIK", "ACDEFGIL"="CGEDAFLI", "ACDEFGJK"="CGJDAFEK", "ACDEFGJL"="CGJDAFLE", "ACDEFGKL"="CGEDAFLK",
    "ACDEFHIJ"="HJECAFDI", "ACDEFHIK"="HEFCADIK", "ACDEFHIL"="HEFCADLI", "ACDEFHJK"="HJECAFDK", "ACDEFHJL"="HJFCADLE",
    "ACDEFHKL"="HEFCADLK", "ACDEFIJK"="CJEDAFIK", "ACDEFIJL"="CJEDAFLI", "ACDEFIKL"="CEIDAFLK", "ACDEFJKL"="CJEDAFLK",
    "ACDEGHIJ"="HGJCADEI", "ACDEGHIK"="HGECADIK", "ACDEGHIL"="HGECADLI", "ACDEGHJK"="HGJCADEK", "ACDEGHJL"="HGJCADLE",
    "ACDEGHKL"="HGECADLK", "ACDEGIJK"="EGJCADIK", "ACDEGIJL"="EGJCADLI", "ACDEGIKL"="EGICADLK", "ACDEGJKL"="EGJCADLK",
    "ACDEHIJK"="HJECADIK", "ACDEHIJL"="HJECADLI", "ACDEHIKL"="HEICADLK", "ACDEHJKL"="HJECADLK", "ACDEIJKL"="EJICADLK",
    "ACDFGHIJ"="HGJCAFDI", "ACDFGHIK"="HGFCADIK", "ACDFGHIL"="HGFCADLI", "ACDFGHJK"="HGJCAFDK", "ACDFGHJL"="CGJDAFLH",
    "ACDFGHKL"="HGFCADLK", "ACDFGIJK"="CGJDAFIK", "ACDFGIJL"="CGJDAFLI", "ACDFGIKL"="CGIDAFLK", "ACDFGJKL"="CGJDAFLK",
    "ACDFHIJK"="HJFCADIK", "ACDFHIJL"="HJFCADLI", "ACDFHIKL"="HFICADLK", "ACDFHJKL"="HJFCADLK", "ACDFIJKL"="CJIDAFLK",
    "ACDGHIJK"="HGJCADIK", "ACDGHIJL"="HGJCADLI", "ACDGHIKL"="HGICADLK", "ACDGHJKL"="HGJCADLK", "ACDGIJKL"="IGJCADLK",
    "ACDHIJKL"="HJICADLK", "ACEFGHIJ"="HGJCAFEI", "ACEFGHIK"="HGECAFIK", "ACEFGHIL"="HGECAFLI", "ACEFGHJK"="HGJCAFEK",
    "ACEFGHJL"="HGJCAFLE", "ACEFGHKL"="HGECAFLK", "ACEFGIJK"="EGJCAFIK", "ACEFGIJL"="EGJCAFLI", "ACEFGIKL"="EGICAFLK",
    "ACEFGJKL"="EGJCAFLK", "ACEFHIJK"="HJECAFIK", "ACEFHIJL"="HJECAFLI", "ACEFHIKL"="HEICAFLK", "ACEFHJKL"="HJECAFLK",
    "ACEFIJKL"="EJICAFLK", "ACEGHIJK"="EGJCAHIK", "ACEGHIJL"="EGJCAHLI", "ACEGHIKL"="EGICAHLK", "ACEGHJKL"="EGJCAHLK",
    "ACEGIJKL"="EJICAGLK", "ACEHIJKL"="EJICAHLK", "ACFGHIJK"="HGJCAFIK", "ACFGHIJL"="HGJCAFLI", "ACFGHIKL"="HGICAFLK",
    "ACFGHJKL"="HGJCAFLK", "ACFGIJKL"="IGJCAFLK", "ACFHIJKL"="HJICAFLK", "ACGHIJKL"="HJICAGLK", "ADEFGHIJ"="HGJDAFEI",
    "ADEFGHIK"="HGEDAFIK", "ADEFGHIL"="HGEDAFLI", "ADEFGHJK"="HGJDAFEK", "ADEFGHJL"="HGJDAFLE", "ADEFGHKL"="HGEDAFLK",
    "ADEFGIJK"="EGJDAFIK", "ADEFGIJL"="EGJDAFLI", "ADEFGIKL"="EGIDAFLK", "ADEFGJKL"="EGJDAFLK", "ADEFHIJK"="HJEDAFIK",
    "ADEFHIJL"="HJEDAFLI", "ADEFHIKL"="HEIDAFLK", "ADEFHJKL"="HJEDAFLK", "ADEFIJKL"="EJIDAFLK", "ADEGHIJK"="EGJDAHIK",
    "ADEGHIJL"="EGJDAHLI", "ADEGHIKL"="EGIDAHLK", "ADEGHJKL"="EGJDAHLK", "ADEGIJKL"="EJIDAGLK", "ADEHIJKL"="EJIDAHLK",
    "ADFGHIJK"="HGJDAFIK", "ADFGHIJL"="HGJDAFLI", "ADFGHIKL"="HGIDAFLK", "ADFGHJKL"="HGJDAFLK", "ADFGIJKL"="IGJDAFLK",
    "ADFHIJKL"="HJIDAFLK", "ADGHIJKL"="HJIDAGLK", "AEFGHIJK"="EGJFAHIK", "AEFGHIJL"="EGJFAHLI", "AEFGHIKL"="EGIFAHLK",
    "AEFGHJKL"="EGJFAHLK", "AEFGIJKL"="EJIFAGLK", "AEFHIJKL"="EJIFAHLK", "AEGHIJKL"="EJIAHGLK", "AFGHIJKL"="HJIFAGLK",
    "BCDEFGHI"="CGBDHFEI", "BCDEFGHJ"="HGBCJFDE", "BCDEFGHK"="CGBDHFEK", "BCDEFGHL"="CGBDHFLE", "BCDEFGIJ"="CGBDJFEI",
    "BCDEFGIK"="CGBDEFIK", "BCDEFGIL"="CGBDEFLI", "BCDEFGJK"="CGBDJFEK", "BCDEFGJL"="CGBDJFLE", "BCDEFGKL"="CGBDEFLK",
    "BCDEFHIJ"="CJBDHFEI", "BCDEFHIK"="CEBDHFIK", "BCDEFHIL"="CEBDHFLI", "BCDEFHJK"="CJBDHFEK", "BCDEFHJL"="CJBDHFLE",
    "BCDEFHKL"="CEBDHFLK", "BCDEFIJK"="CJBDEFIK", "BCDEFIJL"="CJBDEFLI", "BCDEFIKL"="CEBDIFLK", "BCDEFJKL"="CJBDEFLK",
    "BCDEGHIJ"="HGBCJDEI", "BCDEGHIK"="EGBCHDIK", "BCDEGHIL"="EGBCHDLI", "BCDEGHJK"="HGBCJDEK", "BCDEGHJL"="HGBCJDLE",
    "BCDEGHKL"="EGBCHDLK", "BCDEGIJK"="EGBCJDIK", "BCDEGIJL"="EGBCJDLI", "BCDEGIKL"="EGBCIDLK", "BCDEGJKL"="EGBCJDLK",
    "BCDEHIJK"="EJBCHDIK", "BCDEHIJL"="EJBCHDLI", "BCDEHIKL"="EIBCHDLK", "BCDEHJKL"="EJBCHDLK", "BCDEIJKL"="EJBCIDLK",
    "BCDFGHIJ"="HGBCJFDI", "BCDFGHIK"="CGBDHFIK", "BCDFGHIL"="CGBDHFLI", "BCDFGHJK"="HGBCJFDK", "BCDFGHJL"="CGBDHFLJ",
    "BCDFGHKL"="CGBDHFLK", "BCDFGIJK"="CGBDJFIK", "BCDFGIJL"="CGBDJFLI", "BCDFGIKL"="CGBDIFLK", "BCDFGJKL"="CGBDJFLK",
    "BCDFHIJK"="CJBDHFIK", "BCDFHIJL"="CJBDHFLI", "BCDFHIKL"="CIBDHFLK", "BCDFHJKL"="CJBDHFLK", "BCDFIJKL"="CJBDIFLK",
    "BCDGHIJK"="HGBCJDIK", "BCDGHIJL"="HGBCJDLI", "BCDGHIKL"="HGBCIDLK", "BCDGHJKL"="HGBCJDLK", "BCDGIJKL"="IGBCJDLK",
    "BCDHIJKL"="HJBCIDLK", "BCEFGHIJ"="HGBCJFEI", "BCEFGHIK"="EGBCHFIK", "BCEFGHIL"="EGBCHFLI", "BCEFGHJK"="HGBCJFEK",
    "BCEFGHJL"="HGBCJFLE", "BCEFGHKL"="EGBCHFLK", "BCEFGIJK"="EGBCJFIK", "BCEFGIJL"="EGBCJFLI", "BCEFGIKL"="EGBCIFLK",
    "BCEFGJKL"="EGBCJFLK", "BCEFHIJK"="EJBCHFIK", "BCEFHIJL"="EJBCHFLI", "BCEFHIKL"="EIBCHFLK", "BCEFHJKL"="EJBCHFLK",
    "BCEFIJKL"="EJBCIFLK", "BCEGHIJK"="EJBCHGIK", "BCEGHIJL"="EJBCHGLI", "BCEGHIKL"="EGBCIHLK", "BCEGHJKL"="EJBCHGLK",
    "BCEGIJKL"="EJBCIGLK", "BCEHIJKL"="EJBCIHLK", "BCFGHIJK"="HGBCJFIK", "BCFGHIJL"="HGBCJFLI", "BCFGHIKL"="HGBCIFLK",
    "BCFGHJKL"="HGBCJFLK", "BCFGIJKL"="IGBCJFLK", "BCFHIJKL"="HJBCIFLK", "BCGHIJKL"="HJBCIGLK", "BDEFGHIJ"="HGBDJFEI",
    "BDEFGHIK"="EGBDHFIK", "BDEFGHIL"="EGBDHFLI", "BDEFGHJK"="HGBDJFEK", "BDEFGHJL"="HGBDJFLE", "BDEFGHKL"="EGBDHFLK",
    "BDEFGIJK"="EGBDJFIK", "BDEFGIJL"="EGBDJFLI", "BDEFGIKL"="EGBDIFLK", "BDEFGJKL"="EGBDJFLK", "BDEFHIJK"="EJBDHFIK",
    "BDEFHIJL"="EJBDHFLI", "BDEFHIKL"="EIBDHFLK", "BDEFHJKL"="EJBDHFLK", "BDEFIJKL"="EJBDIFLK", "BDEGHIJK"="EJBDHGIK",
    "BDEGHIJL"="EJBDHGLI", "BDEGHIKL"="EGBDIHLK", "BDEGHJKL"="EJBDHGLK", "BDEGIJKL"="EJBDIGLK", "BDEHIJKL"="EJBDIHLK",
    "BDFGHIJK"="HGBDJFIK", "BDFGHIJL"="HGBDJFLI", "BDFGHIKL"="HGBDIFLK", "BDFGHJKL"="HGBDJFLK", "BDFGIJKL"="IGBDJFLK",
    "BDFHIJKL"="HJBDIFLK", "BDGHIJKL"="HJBDIGLK", "BEFGHIJK"="EJBFHGIK", "BEFGHIJL"="EJBFHGLI", "BEFGHIKL"="EGBFIHLK",
    "BEFGHJKL"="EJBFHGLK", "BEFGIJKL"="EJBFIGLK", "BEFHIJKL"="EJBFIHLK", "BEGHIJKL"="EJIBHGLK", "BFGHIJKL"="HJBFIGLK",
    "CDEFGHIJ"="CGJDHFEI", "CDEFGHIK"="CGEDHFIK", "CDEFGHIL"="CGEDHFLI", "CDEFGHJK"="CGJDHFEK", "CDEFGHJL"="CGJDHFLE",
    "CDEFGHKL"="CGEDHFLK", "CDEFGIJK"="CGEDJFIK", "CDEFGIJL"="CGEDJFLI", "CDEFGIKL"="CGEDIFLK", "CDEFGJKL"="CGEDJFLK",
    "CDEFHIJK"="CJEDHFIK", "CDEFHIJL"="CJEDHFLI", "CDEFHIKL"="CEIDHFLK", "CDEFHJKL"="CJEDHFLK", "CDEFIJKL"="CJEDIFLK",
    "CDEGHIJK"="EGJCHDIK", "CDEGHIJL"="EGJCHDLI", "CDEGHIKL"="EGICHDLK", "CDEGHJKL"="EGJCHDLK", "CDEGIJKL"="EGICJDLK",
    "CDEHIJKL"="EJICHDLK", "CDFGHIJK"="CGJDHFIK", "CDFGHIJL"="CGJDHFLI", "CDFGHIKL"="CGIDHFLK", "CDFGHJKL"="CGJDHFLK",
    "CDFGIJKL"="CGIDJFLK", "CDFHIJKL"="CJIDHFLK", "CDGHIJKL"="HGICJDLK", "CEFGHIJK"="EGJCHFIK", "CEFGHIJL"="EGJCHFLI",
    "CEFGHIKL"="EGICHFLK", "CEFGHJKL"="EGJCHFLK", "CEFGIJKL"="EGICJFLK", "CEFHIJKL"="EJICHFLK", "CEGHIJKL"="EJICHGLK",
    "CFGHIJKL"="HGICJFLK", "DEFGHIJK"="EGJDHFIK", "DEFGHIJL"="EGJDHFLI", "DEFGHIKL"="EGIDHFLK", "DEFGHJKL"="EGJDHFLK",
    "DEFGIJKL"="EGIDJFLK", "DEFHIJKL"="EJIDHFLK", "DEGHIJKL"="EJIDHGLK", "DFGHIJKL"="HGIDJFLK", "EFGHIJKL"="EJIFHGLK"
  )

  combo_key  <- paste(sort(thirds$group), collapse = "")
  assign_str <- annexC[[combo_key]]
  if (is.null(assign_str))
    stop("Annex-C-Kombination nicht gefunden: ", combo_key)
  third_for  <- setNames(strsplit(assign_str, "")[[1]],
                         c("A", "B", "D", "E", "G", "I", "K", "L"))

  # id des Dritten der Gruppe, die laut Annex C gegen 'winner_grp' antritt
  third_id <- function(winner_grp)
    std %>% filter(group == third_for[[winner_grp]], rank == 3) %>% pull(id)

  r32_pairs <- list(
    c(get_t("A",2), get_t("B",2)),
    c(get_t("C",1), get_t("F",2)),
    c(get_t("E",1), third_id("E")),
    c(get_t("F",1), get_t("C",2)),
    c(get_t("E",2), get_t("I",2)),
    c(get_t("I",1), third_id("I")),
    c(get_t("A",1), third_id("A")),
    c(get_t("L",1), third_id("L")),
    c(get_t("G",1), third_id("G")),
    c(get_t("D",1), third_id("D")),
    c(get_t("H",1), get_t("J",2)),
    c(get_t("K",2), get_t("L",2)),
    c(get_t("B",1), third_id("B")),
    c(get_t("D",2), get_t("G",2)),
    c(get_t("J",1), get_t("H",2)),
    c(get_t("K",1), third_id("K"))
  )

  ko_args <- list(elo_live = elo_live, teams_df = teams_df, params = params)

  r32 <- do.call(run_knockout, c(list(pairs = r32_pairs, round_name = "Round of 32"),   ko_args))
  ko_args$elo_live <- r32$elo_live
  r16_pairs <- lapply(seq(1,15,2), function(i) c(r32$winners[i], r32$winners[i+1]))
  r16 <- do.call(run_knockout, c(list(pairs = r16_pairs, round_name = "Round of 16"),   ko_args))
  ko_args$elo_live <- r16$elo_live
  qf_pairs  <- lapply(seq(1,7,2),  function(i) c(r16$winners[i], r16$winners[i+1]))
  qf  <- do.call(run_knockout, c(list(pairs = qf_pairs,  round_name = "Quarter-Final"), ko_args))
  ko_args$elo_live <- qf$elo_live
  sf_pairs  <- list(c(qf$winners[1], qf$winners[2]), c(qf$winners[3], qf$winners[4]))
  sf  <- do.call(run_knockout, c(list(pairs = sf_pairs,  round_name = "Semi-Final"),    ko_args))
  ko_args$elo_live <- sf$elo_live
  tp  <- do.call(run_knockout, c(list(pairs = list(sf$losers), round_name = "Third Place"), ko_args))
  ko_args$elo_live <- tp$elo_live
  fin <- do.call(run_knockout, c(list(pairs = list(c(sf$winners[1], sf$winners[2])),
                                      round_name = "Final"), ko_args))
  elo_live <- fin$elo_live

  champion <- teams_df %>% filter(id == fin$winners[1])
  runner   <- teams_df %>% filter(id == fin$losers[1])
  third    <- teams_df %>% filter(id == tp$winners[1])

  all_ko_matches <- bind_rows(r32$matches, r16$matches, qf$matches,
                              sf$matches, tp$matches, fin$matches)

  # final_elo: enthält neben final_elo (Endstand nach Turnier) und
  # start_elo (Wert NACH Modifiern, mit dem das Turnier tatsächlich
  # gestartet wurde) auch orig_elo (ORIGINAL aus teams_init, ohne
  # jegliche Modifier). orig_elo ist der stabile Referenzanker für
  # die ELO-Anpassungs-Slider in der Rangliste.
  final_elo <- data.frame(
    id        = as.integer(names(elo_live)),
    final_elo = as.numeric(elo_live)
  ) %>%
    left_join(teams_df   %>% select(id, team_name, team_name_de, fifa_code, elo), by = "id") %>%
    left_join(teams_init %>% select(id, orig_elo = elo), by = "id") %>%
    mutate(
      change    = round(final_elo - elo),
      final_elo = round(final_elo),
      start_elo = round(elo),
      orig_elo  = round(orig_elo),
      flag      = sapply(fifa_code, get_flag)
    ) %>%
    arrange(desc(final_elo)) %>%
    mutate(rank = row_number())

  list(standings = std, group_matches = gs$matches, ko_matches = all_ko_matches,
       champion = champion, runner_up = runner, third = third,
       final_elo = final_elo)
}

```
