# app-r.md

Use these exact file contents when reconstructing the WC26 text-only project.

## File: `elo/app.R`

```r
# ============================================================
# FIFA World Cup 2026 — ELO Simulation Shiny App
# Install: install.packages(c("shiny", "dplyr", "DT"))
# Run:     shiny::runApp("app.R")
# ============================================================

library(shiny)
library(dplyr)
library(DT)
library(future)
library(promises)

# Worker-Anzahl: Auf dem Produktions-Server (erkannt am /srv/shiny-server-Pfad)
# hardcoded 12 — systemd-Environment wird durch su --login geschluckt,
# .Renviron ist fehleranfällig im Pfad. ENV-Variable hat trotzdem Vorrang,
# falls man später ohne Code-Änderung umstellen will.
# Lokal: dynamisch (detectCores - 1), damit Entwickler-Maschinen
# nicht ihre gesamte CPU für die App verbrennen.
n_workers <- local({
  env_val <- Sys.getenv("WM2026_WORKERS", unset = "")
  if (nzchar(env_val)) {
    as.integer(env_val)
  } else if (dir.exists("/srv/shiny-server")) {
    3L   # Produktions-Server (4 App-Instanzen x 3 Worker = 12)
  } else {
    max(1L, parallel::detectCores() - 1L)   # Lokale Entwicklung
  }
})
future::plan(future::multisession, workers = n_workers)
message("future plan: multisession mit ", n_workers, " Worker(n)")

# ── Pfad zur ausgelagerten Simulations-Logik ────────────────
# simulation.R enthält alle Daten + Berechnungsfunktionen. Sie wird
#   (a) hier im Hauptprozess gesourct (für UI/Server-Code), und
#   (b) einmalig in jedem Future-Worker gesourct (siehe future_promise unten).
# Dadurch wandern pro Simulation nur noch seed+params (wenige KB) statt
# ~49 MB Funktions-/Datenballast in die Worker → kein RAM-Leak mehr.
# normalizePath, weil der Worker u.U. ein anderes Arbeitsverzeichnis hat.
sim_file <- normalizePath("simulation.R", mustWork = TRUE)


# Null-coalescing helper: gibt a zurück, wenn nicht-NULL und nicht-leer,
# sonst b. Muss VOR der ersten Verwendung definiert sein (wird sowohl
# beim UI-Aufbau als auch im Server-Code benutzt).
`%||%` <- function(a, b) if (!is.null(a) && length(a) > 0) a else b

# ── SESSION-TRACKING ─────────────────────────────────────────
# Loggt Start- und Endzeitpunkt jeder Shiny-Session als TSV-Datei.
# Aus den beiden Events (event = "start" / "end") lassen sich später
# sowohl die Gesamtzahl der Besuche als auch Concurrency-Kurven
# (gleichzeitige Nutzer:innen über die Zeit) rekonstruieren.
# Fehler beim Loggen werden abgefangen, damit die App auch bei
# fehlender Schreibberechtigung / vollem Volume normal weiterläuft.
session_log_file <- "../data/logs/sessions.tsv"
# Log-Verzeichnis idempotent anlegen (lokal nicht vorhanden, Server schon).
# Fehlschlag (z.B. read-only-FS) wird stillschweigend ignoriert.
tryCatch(
  dir.create(dirname(session_log_file), recursive = TRUE, showWarnings = FALSE),
  error = function(e) invisible(NULL)
)
tryCatch({
  if (!dir.exists(dirname(session_log_file))) {
    dir.create(dirname(session_log_file), recursive = TRUE, showWarnings = FALSE)
  }
  if (!file.exists(session_log_file)) {
    writeLines("timestamp\tevent\tsession_token", session_log_file)
  }
}, error = function(e) {
  message("Session-Log konnte nicht initialisiert werden: ", conditionMessage(e))
})

log_session_event <- function(event, token) {
  tryCatch({
    line <- paste(
      format(Sys.time(), "%Y-%m-%d %H:%M:%OS3"),
      event,
      token,
      sep = "\t"
    )
    cat(line, "\n", file = session_log_file, append = TRUE, sep = "")
  }, error = function(e) {
    message("Session-Log-Fehler: ", conditionMessage(e))
  })
}

# ── SIMULATIONS-LOGIK (Daten + Funktionen) ──────────────────
# Ausgelagert nach simulation.R. local = FALSE, damit alle Objekte
# (teams_init, default_params, run_tournament, ...) im globalen
# Environment dieses Hauptprozesses landen — exakt wie zuvor, als
# der Code inline hier stand. UI- und Server-Code finden sie dort.
source(sim_file, local = FALSE)

venues <- read.csv("../data/venues.csv", stringsAsFactors = FALSE)

format_kickoff_label <- function(x) {
  sub(
    "([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}):[0-9]{2}([+-][0-9]{2})",
    "\\1 \\2 (UTC\\3)",
    x
  )
}

parse_kickoff_utc <- function(x) {
  normalized <- sub("([+-][0-9]{2})$", "\\100", x)
  as.POSIXct(normalized, format = "%Y-%m-%d %H:%M:%S%z", tz = "UTC")
}

group_label_zh <- function(label) {
  sub("^Group ", "", label)
}

stage_label_zh_for_match <- function(stage_id, match_label) {
  if (stage_id == 1) {
    return(paste0(group_label_zh(match_label), "组"))
  }
  c(
    "32强", "16强", "1/4决赛", "半决赛", "季军赛", "决赛"
  )[stage_id - 1]
}

weather_code_zh <- function(code) {
  dplyr::case_when(
    is.na(code) ~ "天气未知",
    code == 0 ~ "晴",
    code %in% c(1, 2) ~ "多云",
    code == 3 ~ "阴",
    code %in% c(45, 48) ~ "雾",
    code %in% c(51, 53, 55, 56, 57) ~ "毛毛雨",
    code %in% c(61, 63, 65, 66, 67, 80, 81, 82) ~ "降雨",
    code %in% c(71, 73, 75, 77, 85, 86) ~ "降雪",
    code %in% c(95, 96, 99) ~ "雷暴",
    TRUE ~ "天气变化"
  )
}

roof_type_zh <- function(x) {
  dplyr::case_when(
    x == "covered" ~ "全封闭/可控环境",
    x == "retractable" ~ "可开合顶棚",
    x == "partially_covered" ~ "半覆盖看台",
    x == "semi_open" ~ "开放式球场",
    TRUE ~ "开放式球场"
  )
}

match_schedule <- local({
  team_lookup <- teams_init %>%
    select(id, fifa_code, team_name_de)

  matches %>%
    left_join(
      team_lookup %>%
        rename(home_team_id = id,
               home_fifa_code = fifa_code,
               home_team_name = team_name_de),
      by = "home_team_id"
    ) %>%
    left_join(
      team_lookup %>%
        rename(away_team_id = id,
               away_fifa_code = fifa_code,
               away_team_name = team_name_de),
      by = "away_team_id"
    ) %>%
    left_join(venues, by = "city_id") %>%
    mutate(
      kickoff_utc = as.POSIXct(
        unlist(lapply(kickoff_at, parse_kickoff_utc)),
        origin = "1970-01-01",
        tz = "UTC"
      ),
      kickoff_label_zh = vapply(kickoff_at, format_kickoff_label, character(1)),
      stage_label_zh = mapply(stage_label_zh_for_match, stage_id, match_label, USE.NAMES = FALSE),
      matchup_label_zh = dplyr::case_when(
        !is.na(home_team_name) & !is.na(away_team_name) ~ paste0(
          get_flag(home_fifa_code), " ", home_team_name,
          " vs ",
          get_flag(away_fifa_code), " ", away_team_name
        ),
        TRUE ~ match_label
      ),
      choice_label_zh = paste0(
        "M", match_number, " | ",
        stage_label_zh, " | ",
        matchup_label_zh, " | ",
        city_zh
      )
    )
})

default_context_match <- local({
  now_utc <- Sys.time()
  upcoming <- match_schedule %>%
    filter(!is.na(kickoff_utc), kickoff_utc >= now_utc - 6 * 3600) %>%
    arrange(kickoff_utc)
  if (nrow(upcoming) > 0) upcoming$match_number[[1]] else match_schedule$match_number[[1]]
})

weather_cache <- new.env(parent = emptyenv())

fetch_city_forecast <- function(match_row) {
  cache_key <- paste(match_row$city_id, format(Sys.Date(), "%Y-%m-%d"), sep = "_")
  if (exists(cache_key, envir = weather_cache, inherits = FALSE)) {
    return(get(cache_key, envir = weather_cache, inherits = FALSE))
  }

  weather_url <- paste0(
    "https://api.open-meteo.com/v1/forecast?latitude=", match_row$latitude,
    "&longitude=", match_row$longitude,
    "&hourly=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code",
    "&forecast_days=16&timezone=GMT"
  )

  forecast <- tryCatch(
    jsonlite::fromJSON(weather_url),
    error = function(e) list(error = conditionMessage(e))
  )
  assign(cache_key, forecast, envir = weather_cache)
  forecast
}

get_match_weather <- function(match_row) {
  if (is.na(match_row$kickoff_utc)) {
    return(list(status = "missing", message = "比赛开球时间解析失败，暂时无法对齐天气预报。"))
  }

  forecast <- fetch_city_forecast(match_row)
  if (!is.null(forecast$error)) {
    return(list(status = "error", message = paste("天气接口调用失败：", forecast$error)))
  }

  hourly <- forecast$hourly
  if (is.null(hourly$time) || length(hourly$time) == 0) {
    return(list(status = "missing", message = "当前没有可用的小时级天气预报。"))
  }

  hourly_times <- as.POSIXct(hourly$time, format = "%Y-%m-%dT%H:%M", tz = "GMT")
  if (all(is.na(hourly_times))) {
    return(list(status = "missing", message = "天气数据时间轴解析失败。"))
  }

  idx <- which.min(abs(as.numeric(difftime(hourly_times, match_row$kickoff_utc, units = "hours"))))
  if (length(idx) == 0 || is.na(idx)) {
    return(list(status = "missing", message = "没有找到与开球时间相邻的天气预报。"))
  }

  hour_gap <- abs(as.numeric(difftime(hourly_times[idx], match_row$kickoff_utc, units = "hours")))
  if (is.na(hour_gap) || hour_gap > 6) {
    return(list(status = "missing", message = "这场比赛超出了 Open-Meteo 当前可提供的预报窗口。"))
  }

  list(
    status = "ok",
    forecast_time = hourly_times[idx],
    temperature_2m = hourly$temperature_2m[idx],
    apparent_temperature = hourly$apparent_temperature[idx],
    relative_humidity_2m = hourly$relative_humidity_2m[idx],
    precipitation_probability = hourly$precipitation_probability[idx],
    precipitation = hourly$precipitation[idx],
    wind_speed_10m = hourly$wind_speed_10m[idx],
    weather_code = hourly$weather_code[idx]
  )
}

build_match_context_notes <- function(match_row, weather) {
  notes <- c(
    paste0("球场环境：", roof_type_zh(match_row$roof_type), "，草坪类型为", match_row$pitch_type, "。")
  )

  if (!is.na(match_row$altitude_m) && match_row$altitude_m >= 1500) {
    notes <- c(notes, paste0("海拔约 ", match_row$altitude_m, " 米，空气更稀薄，比赛节奏和体能消耗可能被放大。"))
  } else if (!is.na(match_row$altitude_m) && match_row$altitude_m >= 500) {
    notes <- c(notes, paste0("海拔约 ", match_row$altitude_m, " 米，体能与长传落点会有轻微场地效应。"))
  }

  if (!identical(weather$status, "ok")) {
    return(notes)
  }

  if (!is.na(weather$apparent_temperature) && weather$apparent_temperature >= 32) {
    notes <- c(notes, "体感温度偏高，压迫和高强度回追的消耗会更明显。")
  } else if (!is.na(weather$temperature_2m) && weather$temperature_2m <= 8) {
    notes <- c(notes, "气温偏低，开场节奏可能更紧，但肌肉负荷管理更重要。")
  }

  if (!is.na(weather$relative_humidity_2m) &&
      !is.na(weather$temperature_2m) &&
      weather$relative_humidity_2m >= 75 &&
      weather$temperature_2m >= 26) {
    notes <- c(notes, "湿热条件叠加时，比赛后段的疲劳衰减通常更快。")
  }

  if (!is.na(weather$wind_speed_10m) && weather$wind_speed_10m >= 25) {
    notes <- c(notes, "风速较高，长传、定位球和高空球的离散性会增加。")
  }

  if ((!is.na(weather$precipitation_probability) && weather$precipitation_probability >= 50) ||
      (!is.na(weather$precipitation) && weather$precipitation >= 1)) {
    notes <- c(notes, "有明显降水风险，草皮更滑，地面推进和门将处理球的不确定性会上升。")
  }

  notes
}



# ── UI ───────────────────────────────────────────────────────

# Modul-weit gecachter Default-Lauf (seed = 111, default_params).
# Erste Berechnung erfolgt lazy beim ersten Session-Start; danach
# instantaner Return für alle weiteren Sessions im selben R-Prozess.
default_result_cache <- local({
  cached <- NULL
  function() {
    if (is.null(cached)) cached <<- run_tournament(seed = 111)
    cached
  }
})

ui <- function(req) {
  
  # Reiter-Vorauswahl bereits beim Seitenaufbau (kein nachträgliches
  # Umschalten per Websocket). ?modell=dc rendert direkt Dixon-Coles.
  start_model <- if (identical(
    parseQueryString(req$QUERY_STRING)[["modell"]], "dc")) {
    "dixon_coles"
  } else {
    "elo"
  }
  
  fluidPage(
    tags$head(
    tags$meta(name="viewport", content="width=device-width, initial-scale=1.0"),
    tags$link(href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap", rel="stylesheet"),
    tags$style(HTML("
      /* ══ DARK MODE (default) ══ */
      :root {
        --fublue:  #004659;
        --fugreen: #CCFF00;
        --fublack: #000000;
        --fuwhite: #FFFFFF;
        --body:    #000000;
        --gold:    #CCFF00;
        --lime:    #CCFF00;
        --navy:    #222222;
        --red:     #C8102E;
        --dark:    #000000;
        --panel:   #111111;
        --border:  #333333;
        --text:    #FFFFFF;
        --muted:   #888888;
        --green:   #00C853;
        --blue:    #2979FF;
        --input-bg:          #111111;
        --group-card-bg:     #111111;
        --group-header-bg:   #CCFF00;
        --qualify-bg:        transparent;
        --qualify3-bg:       transparent;
        --ko-border:         rgba(255,255,255,0.08);
        --elo-bar-bg:        rgba(255,255,255,0.08);
        --rank4-bg:          transparent;
        --rank3-bg:          transparent;
      }
      /* ══ LIGHT MODE ══ */
      body.light-mode {
        --body:            #FFFFFF;
        --dark:            #FFFFFF;
        --panel:           #FFFFFF;
        --border:          #E0E0E0;
        --text:            #000000;
        --muted:           #888888;
        --gold:            #000000;
        --lime:            #000000;
        --input-bg:        #F8F8F8;
        --group-card-bg:   #FFFFFF;
        --group-header-bg: rgba(0,0,0,0.04);
        --qualify-bg:      transparent;
        --qualify3-bg:     transparent;
        --ko-border:       rgba(0,0,0,0.06);
        --elo-bar-bg:      rgba(0,0,0,0.07);
        --rank4-bg:        transparent;
        --rank3-bg:        transparent;
      }

      * { box-sizing: border-box; }
      body {
        background: var(--dark); color: var(--text);
        font-family: 'Source Sans 3', Arial, sans-serif; font-size: 14px; margin: 0; padding: 0;
        transition: background 0.3s, color 0.3s;
      }

      /* ── HEADER ── */
      .wc-header {
        background: #000000;
        border-bottom: 3px solid #CCFF00;
        padding: 20px 40px; position: relative; overflow: hidden;
      }
      body.light-mode .wc-header {
        background: #FFFFFF;
        border-bottom: 3px solid #CCFF00;
      }
      .wc-header::before {
        content: ''; position: absolute; inset: 0;
        background: repeating-linear-gradient(
          45deg, transparent, transparent 40px,
          rgba(245,197,24,0.03) 40px, rgba(245,197,24,0.03) 41px);
        pointer-events: none;
      }
      .wc-title {
        font-family: 'Source Sans 3', Arial, sans-serif; font-size: 52px; font-weight: 700;
        letter-spacing: 4px; color: var(--fuwhite); line-height: 1; margin: 0;
        text-shadow: 0 0 40px rgba(126,200,32,0.35);
      }
      .wc-subtitle {
        color: #FFFFFF; font-size: 12px; font-weight: 300;
        letter-spacing: 3px; text-transform: uppercase; margin-top: 4px;
      }
      body.light-mode .wc-title { color: #000000; text-shadow: none; }
      body.light-mode .wc-subtitle { color: #000000; }
      .header-inner {
        display: flex; align-items: center; justify-content: space-between;
        flex-wrap: wrap; gap: 16px;
      }
      .header-branding { display: flex; flex-direction: column; }
      .fustat-logo {
        height: 44px; opacity: 0.92;
        filter: drop-shadow(0 0 8px rgba(126,200,32,0.3));
        transition: opacity 0.2s, filter 0.2s;
      }
      .fustat-logo:hover { opacity: 1; filter: drop-shadow(0 0 14px rgba(126,200,32,0.55)); }

      /* ── THEME TOGGLE ── */
      .theme-toggle {
        display: flex; align-items: center; gap: 10px;
        background: #CCFF00; border: 1px solid #CCFF00;
        border-radius: 24px; padding: 6px 14px; cursor: pointer;
        transition: background 0.2s, border-color 0.2s;
        user-select: none;
      }
      body.light-mode .theme-toggle {
        display: flex; align-items: center; gap: 10px;
        background: #FFFFFF; border: 1px solid rgba(255,255,255,0.15);
        border-radius: 24px; padding: 6px 14px; cursor: pointer;
        transition: background 0.2s, border-color 0.2s;
        user-select: none;
      }
      .toggle-label {
        font-family: 'Source Sans 3', Arial, sans-serif; font-size: 14px; font-weight: 700;
        letter-spacing: 2px; color: #000000;
      }
      .toggle-track {
        position: relative; width: 42px; height: 22px;
        background: #32324A; border-radius: 11px;
        transition: background 0.3s;
        flex-shrink: 0;
      }
      body.light-mode .toggle-track { background: #CCFF00; border: 1.5px solid #CCFF00; }
      body.light-mode .toggle-track.on { background: #CCFF00; border: 1.5px solid #CCFF00; }
      .toggle-track.on { background: var(--gold); }
      .toggle-thumb {
        position: absolute; top: 3px; left: 3px;
        width: 16px; height: 16px; border-radius: 50%;
        background: #fff; transition: transform 0.3s;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      }
      body.light-mode .toggle-thumb {
        position: absolute; top: 3px; left: 3px;
        width: 16px; height: 16px; border-radius: 50%;
        background: #000000; transition: transform 0.3s;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      }
      .toggle-track.on .toggle-thumb { transform: translateX(20px); }
      .toggle-icon { font-size: 16px; }

      /* ── LAYOUT ── */
      .wc-body { padding: 24px 32px; }

      /* ── CONTROLS ── */
      .control-bar {
        display: flex; align-items: flex-end; gap: 28px; flex-wrap: wrap;
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 10px; padding: 16px 20px; margin-bottom: 24px;
        transition: background 0.3s, border-color 0.3s;
      }
      .control-group { display: flex; flex-direction: column; gap: 6px; }
      .control-label {
        color: var(--muted); font-size: 10px; letter-spacing: 1.5px;
        text-transform: uppercase; font-weight: 400;
      }
      body:not(.light-mode) .control-label { color: #FFFFFF; }
      #seed_elo, #seed_dc {
        background: var(--input-bg); border: 1px solid var(--border); color: var(--text);
        border-radius: 6px; padding: 8px 12px; width: 120px;
        font-family: monospace; font-size: 14px;
        transition: background 0.3s, border-color 0.3s, color 0.3s;
      }
      body:not(.light-mode) #seed_elo,
      body:not(.light-mode) #seed_dc { background: #000000; color: #FFFFFF; }
      body:not(.light-mode) #seed_elo::placeholder,
      body:not(.light-mode) #seed_dc::placeholder { color: #FFFFFF; }
      #run_btn {
        background: var(--gold); color: #000; border: none;
        font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 18px; letter-spacing: 2px;
        padding: 10px 28px; border-radius: 6px; cursor: pointer;
        transition: all 0.2s; box-shadow: 0 0 20px rgba(245,197,24,0.3);
      }
      #run_btn:hover { background: #FFFFFF; color: #000000; box-shadow: none; transform: translateY(-1px); }
      body.light-mode #run_btn { background: #CCFF00; color: #000000; box-shadow: none; border: none; }
      body.light-mode #run_btn:hover { background: #000000; color: #CCFF00; box-shadow: none; transform: translateY(-1px); }

      /* ── K SLIDER (Shiny) ── */
      #k_slider.js-range-slider { background: transparent; }
      .irs--shiny .irs-single { background: transparent; border: none; color: #FFFFFF; font-size: 12px; padding: 2px 4px; top: -2px; }
      .irs--shiny .irs-bar { background: #CCFF00; border: none; }
      .irs--shiny .irs-handle { background: #CCFF00; border: 2px solid #CCFF00; box-shadow: none; }
      .irs--shiny .irs-handle:hover { background: #CCFF00; }
      .irs--shiny .irs-bar--single { border-left: 1px solid var(--gold); }
      .irs--shiny .irs-line { background: var(--border); border: none; }
      body.light-mode .irs--shiny .irs-single { background: #FFFFFF; border: none; color: #000000; font-size: 12px; padding: 2px 4px; top: -2px; }
      body.light-mode .irs--shiny .irs-bar { background: #CCFF00; border: none; }
      body.light-mode .irs--shiny .irs-handle { background: #000000; border: 2px solid #000000; box-shadow: none; }
      body.light-mode .irs--shiny .irs-handle:hover { background: #000000; }
      .irs--shiny .irs-min, .irs--shiny .irs-max { background: var(--panel); color: var(--muted); font-size: 11px; }
      .irs-with-grid { margin-bottom: 0 !important; }
      .form-group { margin-bottom: 0 !important; }

      /* ── SCORE MODE RADIO (Poisson / Empirisch) ── */
      .score-mode-radio .shiny-options-group { margin-top: 2px; }
      .score-mode-radio .radio { margin: 4px 0; padding: 0; }
      .score-mode-radio .radio label {
        font-family: 'Source Sans 3', Arial, sans-serif;
        font-size: 13px; font-weight: 600; color: var(--text);
        padding-left: 24px; cursor: pointer;
      }
      .score-mode-radio input[type='radio'] {
        accent-color: var(--gold);
        margin-right: 6px;
        cursor: pointer;
      }
      body.light-mode .score-mode-radio input[type='radio'] { accent-color: #000000; }

      /* ── PODIUM ── */
      .podium { display: flex; gap: 12px; margin-bottom: 24px; }
      .podium-card {
        flex: 1; background: var(--panel); border: 2px solid var(--border);
        border-radius: 12px; padding: 20px; text-align: center;
        transition: background 0.3s, border-color 0.3s;
      }
      .podium-card.first  { border-color: #D4AF37; box-shadow: 0 0 30px rgba(245,197,24,0.15); }
      .podium-card.second { border-color: #C0C0C0; }
      .podium-card.third  { border-color: #B08D57; }
      .podium-label {
        font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 13px;
        letter-spacing: 3px; color: var(--muted); margin-bottom: 8px;
      }
      .podium-flag  { font-size: 40px; display: block; margin-bottom: 6px; }
      .podium-team  { font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 22px; letter-spacing: 1px; }
      .podium-card.first  .podium-team { color: #D4AF37; }
      .podium-card.second .podium-team { color: #C0C0C0; }
      .podium-card.third  .podium-team { color: #B08D57; }
      .trophy { font-size: 28px; }

      /* ── TABS ── */
      .nav-tabs { border-bottom: 2px solid var(--border); margin-bottom: 0; }
      .nav-tabs > li > a {
        background: transparent; border: none; color: var(--muted);
        font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 14px; letter-spacing: 1px;
        padding: 10px 20px; border-radius: 0; transition: color 0.2s; text-transform: uppercase;
      }
      .nav-tabs > li > a:hover { color: var(--text); background: transparent; border: none; }
      .nav-tabs > li.active > a,
      .nav-tabs > li.active > a:hover,
      .nav-tabs > li.active > a:focus {
        background: transparent; border: none;
        border-bottom: 3px solid var(--gold) !important;
        color: var(--gold); margin-bottom: -2px;
      }
      body.light-mode .nav-tabs > li.active > a,
      body.light-mode .nav-tabs > li.active > a:hover,
      body.light-mode .nav-tabs > li.active > a:focus {
        color: #000000;
        border-bottom: 3px solid #CCFF00 !important;
      }
      .tab-content {
        background: var(--panel); border: 1px solid var(--border);
        border-top: none; border-radius: 0 0 10px 10px; padding: 20px;
        transition: background 0.3s, border-color 0.3s;
      }
      /* Verschachtelte DC-Reiter (Angriff/Abwehr) in der Mannschafts-
         einstellung: kein eigener Rahmen/Hintergrund, damit sie sich in das
         umgebende Panel einfügen statt eine zweite Box zu erzeugen. */
      .dc-tabs-wrap .tab-content {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 12px 0 0 0;
      }

      /* ── GROUPS ── */
      .groups-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px,1fr)); gap: 16px; }
      .group-card  { background: var(--group-card-bg); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: background 0.3s; }
      body.light-mode .group-card { border: 1.5px solid #000000; }
      .group-header {
        background: var(--group-header-bg);
        border-bottom: 1px solid var(--border); padding: 10px 16px;
        font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 16px; letter-spacing: 2px; color: var(--lime);
        text-transform: uppercase;
      }
      body:not(.light-mode) .group-header { color: #000000; }
      body.light-mode .group-header { color: #000000; background: #CCFF00; border-bottom: 1px solid #000000; }
      .group-table { width: 100%; border-collapse: collapse; table-layout: auto; }
      .group-table th {
        color: var(--muted); font-size: 10px; letter-spacing: 1px; text-transform: uppercase;
        padding: 6px 12px; text-align: right; font-weight: 400;
      }
      body:not(.light-mode) .group-table th { color: #F8F8F8; }
      .group-table th:first-child { text-align: left; }
      .group-table td { padding: 8px 12px; border-top: 1px solid var(--ko-border); text-align: right; }
      .group-table td:first-child { text-align: left; }
      /* Numerische Spalten (2–6: Pkt, Tore+, Tore−, Diff, ELO) kompakter darstellen */
      .group-table th:nth-child(n+2),
      .group-table td:nth-child(n+2) {
        padding-left: 4px; padding-right: 8px;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
      }
      .group-table th:last-child,
      .group-table td:last-child { padding-right: 12px; }
      .group-table tr:first-child td { border-top: none; }
      .qualify     { background: var(--qualify-bg); }
      .qualify-3rd { background: var(--qualify3-bg); }
      .rank-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: 600; margin-right: 6px;
      }
      .rank-1 { background: #FFD700; color: #000000; }
      .rank-2 { background: #C0C0C0; color: #000000; }
      .rank-3 { background: #CD7F32; color: #000000; border: none; }
      .rank-4 { background: #222222; color: #888888; }
      body.light-mode .rank-1 { background: #FFD700; color: #000000; }
      body.light-mode .rank-2 { background: #C0C0C0; color: #000000; }
      body.light-mode .rank-3 { background: #CD7F32; color: #000000; border: none; }
      body.light-mode .rank-4 { background: #F0F0F0; color: #555555; }
      .pts-cell { font-weight: 600; color: var(--gold); }
      body.light-mode .pts-cell { color: #000000; }
      .gd-pos { color: var(--green); }
      .gd-neg { color: var(--red); }
      body.light-mode .gd-pos { color: #007a30; }

      /* ── KO ── */
      .ko-section { margin-bottom: 28px; }
      .ko-round-title {
        font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 18px; letter-spacing: 2px; color: var(--lime);
        border-left: 4px solid var(--lime); padding-left: 12px; margin-bottom: 12px; text-transform: uppercase;
      }
      body.light-mode .ko-round-title { color: #000000; border-color: #CCFF00; }
      .ko-table { width: 100%; border-collapse: collapse; }
      .ko-table th {
        color: var(--muted); font-size: 10px; letter-spacing: 1px; text-transform: uppercase;
        padding: 8px 14px; text-align: left; border-bottom: 1px solid var(--border); font-weight: 400;
      }
      .ko-table td { padding: 9px 14px; border-bottom: 1px solid var(--ko-border); }
      .ko-table tr:last-child td { border-bottom: none; }
      .ko-score  { font-family: monospace; font-size: 15px; font-weight: 600; color: var(--gold); text-align: center; }
      body.light-mode .ko-score { color: #000000; }
      .ko-winner { color: #CCFF00; font-weight: 600; }
      body.light-mode .ko-winner { color: #007a30; }

      /* ── ELO ── */
      .elo-up { color: var(--green); }
      body.light-mode .elo-up { color: #007a30; }
      .elo-dn { color: var(--red); }

      /* ── Per-Team ELO-Anpassungs-Slider in der ELO-Rangliste ── */
      /* Kompakter Shiny-Slider in jeder Tabellenzeile. */
      .elo-adj-slider {
        width: 200px;
        min-width: 180px;
        margin: 0;
      }
      .elo-adj-slider .form-group { margin: 0 !important; padding: 0 !important; }
      .elo-adj-slider .irs--shiny { margin-top: 0; margin-bottom: 0; min-height: 50px; }
      .elo-adj-slider .irs { height: 44px; top: 0; }
      .elo-adj-slider .irs-line { top: 6px; }
      .elo-adj-slider .irs-bar  { top: 6px; }
      .elo-adj-slider .irs-handle { top: -2px; }
      /* Min/Max-Labels in jeder Zeile ausblenden — Spaltentitel reicht. */
      .elo-adj-slider .irs-min,
      .elo-adj-slider .irs-max { display: none; }
      /* Aktuellen Wert UNTER den Regler legen (statt darüber), kleiner & mit Abstand. */
      .elo-adj-slider .irs-single {
        top: 26px !important;
        background: transparent !important;
        color: var(--text) !important;
        font-family: monospace;
        font-size: 10px;
        font-weight: 600;
        padding: 0 !important;
      }
      .elo-adj-slider .irs-single::before { display: none !important; }

      .elo-adj-reset-wrap {
        display: flex;
        justify-content: flex-end;
        margin: 0 0 12px 0;
      }

      /* Spalte 'ELO-Änderung': Differenz aus Slider und Start-ELO,
         rein lesend, grün/rot gefärbt mit Vorzeichen. */
      .elo-user-delta { font-family: monospace; font-weight: 600; }

      /* ── EINSTELLUNGEN-BOX (permanent ausgeklappt) ── */
      .settings-box {
        margin: 0 0 20px 0;
        border: 1px solid var(--border);
        border-radius: 10px;
        background: var(--panel);
        position: relative;
        z-index: 50;          /* über Podium, damit Dropdown nicht verdeckt wird */
      }
      /* Header zeigt Titel links, Reset-Button rechts in derselben Zeile. */
      .settings-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--text);
        border-bottom: 1px solid var(--border);
        background: var(--input-bg);
        border-radius: 10px 10px 0 0;
      }
      .settings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px 18px;
        padding: 16px;
      }
      .settings-grid-fixed {
        grid-template-columns: repeat(auto-fill, 200px);
      }
      .settings-grid .control-group { margin: 0; }
      .settings-box .tabbable + .settings-header { border-radius: 0; }
      .settings-box > .tabbable > .tab-content {
        display: none;
      }
      /* Sekundärer Reset-Button: dezent, klar als Rückgängig-Aktion erkennbar.
         Im Header kompakter, damit die Headerhöhe nicht aufgebläht wird. */
      .btn-reset {
        background: transparent;
        color: #000000;
        border: 1px solid var(--border);
        padding: 6px 14px;
        border-radius: 6px;
        font-family: 'Source Sans 3', Arial, sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        transition: background 0.15s, color 0.15s, border-color 0.15s;
      }
      .btn-reset:hover {
        background: var(--input-bg);
        color: #000000;
        border-color: #000000;
      }
      /* Hilfe-Links im Settings-Header (Desktop). Container links für Titel + Links;
         Reset-Button bleibt rechts. */
      .settings-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
        flex: 1;
        flex-wrap: wrap;
      }
      .help-link {
        font-family: 'Source Sans 3', Arial, sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--text);
        text-decoration: none;
        padding: 4px 10px;
        border: 1px solid var(--border);
        border-radius: 6px;
        transition: background 0.15s, border-color 0.15s, color 0.15s;
      }
      .help-link:hover {
        background: var(--input-bg);
        border-color: #000000;
        color: #000000;
        text-decoration: none;
      }
      /* Slot-Wrapper für die (server-seitig gerenderten) Hilfe-Links.
         display:contents => der Wrapper-DIV selbst nimmt kein Layout ein,
         die enthaltenen <a> bleiben direkte Flex-Kinder ihres Containers
         (Desktop-Header bzw. Mobile-Buttonzeile) und behalten Abstände/Breite. */
      .help-slot { display: contents; }
      /* Mobile-Hilfeknöpfe über/unter SIMULIEREN. Standardmäßig versteckt,
         im @media-Block für schmale Bildschirme aktiviert. */
      .help-link-mobile {
        display: none;
        justify-content: center;
        margin: 0 0 12px 0;
      }
      .help-link-mobile.below { margin: 0 0 24px 0; }
      /* Disclaimer am Fuß der gesamten App. */
      .disclaimer {
        margin: 40px 0 24px 0;
        padding: 20px 0 0 0;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-size: 11px;
        line-height: 1.55;
      }
      .disclaimer-title {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 0 0 8px 0;
        color: var(--text);
      }
      .disclaimer p { margin: 0 0 8px 0; }
      /* Zentraler Simulieren-Button außerhalb der Einstellungsbox */
      .run-section {
        display: flex;
        justify-content: center;
        margin: 0 0 24px 0;
      }
      .run-section .btn { min-width: 220px; }
      /* Selectize-Dropdown muss über dem Podium liegen */
      .selectize-dropdown { z-index: 9999 !important; }
      .selectize-control  { position: relative; z-index: 100; }
      /* Selectize-Felder/Dropdowns an das Theme anpassen.
         Standard-Selectize ist immer weiß — wir überschreiben mit CSS-Variablen,
         damit im Dark Mode korrekt schwarz/weiß angezeigt wird. */
      .selectize-input,
      .selectize-input input,
      .selectize-dropdown,
      .selectize-dropdown-content,
      .selectize-dropdown .option {
        background: var(--input-bg) !important;
        color: var(--text) !important;
      }
      .selectize-input,
      .selectize-dropdown {
        border: 1px solid var(--border) !important;
      }
      .selectize-dropdown .option.active,
      .selectize-dropdown .option:hover {
        background: #CCFF00 !important;
        color: #000000 !important;
      }
      /* Podium darf keinen eigenen stacking context erzeugen, der das Dropdown abschneidet */
      .podium { position: relative; z-index: 1; }

      /* ── SPINNER ── */
      .loading-overlay {
        display: none; position: fixed; inset: 0; background: rgba(10,10,15,0.85);
        z-index: 9999; align-items: center; justify-content: center; flex-direction: column; gap: 16px;
      }
      .loading-overlay.active { display: flex; }
      .spinner {
        width: 48px; height: 48px; border: 4px solid rgba(245,197,24,0.2);
        border-top-color: var(--gold); border-radius: 50%; animation: spin 0.8s linear infinite;
      }
      @keyframes spin { to { transform: rotate(360deg); } }
      .loading-text { font-family: 'Source Sans 3', Arial, sans-serif; font-weight: 700; font-size: 22px; letter-spacing: 4px; color: var(--gold); }

      /* ── MISC ── */
      select.form-control { background: var(--input-bg); border: 1px solid var(--border); color: var(--text); border-radius: 6px; }
      .shiny-output-error { color: var(--red); }

      /* ── MOBILE ── */
      @media (max-width: 600px) {
        /* Header-Hilfe-Links auf Mobile ausblenden, Mobile-Buttons stattdessen anzeigen */
        .settings-header-left .help-link { display: none; }
        .help-link-mobile { display: flex; }
        /* Mobile-Hilfe-Buttons: exakt so groß wie der SIMULIEREN-Button.
           Volle Breite, identisches Padding/Schriftgröße/letter-spacing.
           Border bleibt dünn — kennzeichnet die Buttons als sekundär. */
        .help-link-mobile .help-link {
          flex: 1;
          text-align: center;
          padding: 10px 28px;
          font-size: 18px;
          font-weight: 700;
          letter-spacing: 2px;
        }
        .wc-header { padding: 12px 16px; }
        .header-inner { flex-direction: column; align-items: flex-start; gap: 10px; }
        .wc-title { font-size: 28px; letter-spacing: 2px; }
        .wc-subtitle { font-size: 10px; }
        .fustat-logo { height: 28px; }
        .Alumni-logo { height: 28px; }
        div[style*='gap:20px'] { flex-wrap: wrap; gap: 8px !important; }
        .wc-body { padding: 12px; }
        .control-bar { flex-direction: column; align-items: stretch; gap: 14px; }
        #run_btn { width: 100%; }
        #seed_elo, #seed_dc { width: 100%; }
        .settings-grid-fixed { grid-template-columns: 1fr; }
        .podium { flex-direction: column; gap: 8px; }
        .groups-grid { grid-template-columns: 1fr; }
        .nav-tabs > li > a { font-size: 11px; padding: 8px 8px; letter-spacing: 0; }
        .group-table td, .group-table th { padding: 5px 6px; font-size: 12px; }
        .ko-table td, .ko-table th { padding: 5px 8px; font-size: 12px; }
        .tab-content { padding: 12px; }
        .settings-box > .tabbable > .tab-content { display: none; }
        .podium { flex-direction: column; gap: 8px; }
        .podium-card.first  { order: 1; }
        .podium-card.second { order: 2; }
        .podium-card.third  { order: 3; }
        /* Slider in der ELO-Rangliste auf Mobile schmaler */
        .elo-adj-slider { width: 140px; min-width: 130px; }
        /* ELO-Rangliste auf Mobile: nur Platz, Team, Slider, End-ELO zeigen.
           Spalten 3 (Start-ELO) und 5 (Δ Turnier) werden ausgeblendet,
           damit die Tabelle nicht über den Bildschirmrand hinausläuft. */
        .elo-rangliste-table th:nth-child(3),
        .elo-rangliste-table td:nth-child(3),
        .elo-rangliste-table th:nth-child(5),
        .elo-rangliste-table td:nth-child(5) { display: none; }
      }
    "))
  ),

  div(class="loading-overlay", id="loader",
      div(class="spinner"),
      div(class="loading-text", "正在模拟赛事...")
  ),

  div(class="wc-header",
      div(class="header-inner",
          div(class="header-branding",
              p(class="wc-subtitle", "ELO 与 Dixon-Coles 世界杯模拟"),
              h1(class="wc-title", "🏆 FIFA WM 2026")
          ),
          div(style="display:flex; align-items:center; gap:20px;",
              div(class="theme-toggle", id="theme_toggle", onclick="toggleTheme()",
                  span(class="toggle-icon", id="theme_icon", "🌙"),
                  div(class="toggle-track", id="toggle_track",
                      div(class="toggle-thumb")
                  ),
                  span(class="toggle-label", id="theme_label", "LIGHT MODE")
              ),
              tags$img(src="FUStatBlueOnGreen.png",    id="fustat-logo", class="fustat-logo", alt="FUSTAT",  style="height:55px;"),
              tags$img(src="WiWiss-Alumni.png",                          class="Alumni-logo", alt="Alumni",  style="height:55px;"),
              tags$img(src="StuKoLogoLight_Trans.png", id="stuko-logo",  class="fustat-logo", alt="StuKo",   style="height:55px;")
          )
      )
  ),

  div(class="wc-body",

      # ── EINSTELLUNGEN (permanent ausgeklappt) ───────────────────
      div(class="settings-box",
          tabsetPanel(
            id = "prediction_model",
            type = "tabs",
            selected = start_model,
            tabPanel("ELO", value = "elo"),
            tabPanel("Dixon-Coles", value = "dixon_coles")
        ),

        # Header mit Titel links und Zurücksetzen-Button rechts in derselben Zeile.
        div(class="settings-header",
            div(class="settings-header-left",
                span(class="settings-header-title", "⚙️ 参数设置"),
                uiOutput("help_links_desktop", class="help-slot")
            ),
            actionButton("reset_btn", "↺ 重置", class="btn-reset")
        ),

        conditionalPanel(
          condition = "input.prediction_model == 'elo'",
          div(class="settings-grid",
              # Zufallsgenerator Startwert (vormals Random Seed)
              div(class="control-group",
                  div(class="control-label", "随机种子"),
                  tags$input(id="seed_elo", type="number", value="", min="1", max="99999",
                             class="form-control", placeholder="留空则随机")
              ),

              # Turnier Elo Gewicht (vormals K-Factor / Lerngeschwindigkeit)
              div(class="control-group",
                  div(class="control-label", "赛事 ELO 系数"),
                  sliderInput("k_slider", label=NULL, min=0, max=100, value=60, step=5,
                              ticks=FALSE, width="100%")
              ),

              # Tor-Modell als Radio-Buttons (klassisch, sofort sichtbar welche Option aktiv ist)
              div(class="control-group score-mode-radio",
                  div(class="control-label", "进球模型"),
                  radioButtons("use_historical", label = NULL,
                               choices = c("Poisson" = "0",
                                           "经验分布" = "1"),
                               selected = "0",
                               inline = FALSE)
              ),

              # Außenseiter-Faktor
              div(class="control-group",
                  div(class="control-label", "冷门系数"),
                  sliderInput("upset_factor", label=NULL,
                              min=-3, max=3, value=0, step=0.1,
                              ticks=FALSE, width="100%")
              ),

              # Torreichtum
              div(class="control-group",
                  div(class="control-label", "进球丰度"),
                  sliderInput("goal_scale", label=NULL,
                              min=0.3, max=2.0, value=1.0, step=0.1,
                              ticks=FALSE, width="100%")
              ),

              # Unentschieden-Häufigkeit (max)
              # Slider-Wert ist direkt die max. Wahrscheinlichkeit eines
              # Unentschieden bei ELO-Gleichstand. Default 0.3 — einheitlich mit
              # default_params$draw_max in simulation.R (vormals dort 1/3).
              div(class="control-group",
                  div(class="control-label", "ELO 相同时的平局概率"),
                  sliderInput("draw_max", label=NULL,
                              min=0, max=1.0, value=.3, step=0.01,
                              ticks=FALSE, width="100%")
              ),

              # Team-Boost: Auswahl
              div(class="control-group",
                  div(class="control-label", "定向调整球队"),
                  selectInput("team_boost_id", label=NULL,
                              choices = setNames(
                                teams_init$id,
                                paste(sapply(teams_init$fifa_code, get_flag),
                                      teams_init$team_name_de)
                              ),
                              selected = (teams_init %>%
                                            filter(fifa_code == "GER") %>%
                                            pull(id))[1],
                              width="100%")
              ),

              # Team-Boost: ELO-Differenz
              div(class="control-group",
                  div(class="control-label", "该队 ELO 调整值"),
                  sliderInput("team_boost_value", label=NULL,
                              min=-500, max=500, value=0, step=10,
                              ticks=FALSE, width="100%")
              )
          )
        ),

        conditionalPanel(
          condition = "input.prediction_model == 'dixon_coles'",
          div(class="settings-grid",
              # Zufallsgenerator Startwert
              div(class="control-group",
                  div(class="control-label", "随机种子"),
                  tags$input(id="seed_dc", type="number", value="", min="1", max="99999",
                             class="form-control", placeholder="留空则随机")
              ),

              # Heimvorteil USA / Kanada / Mexiko: Multiplikator auf den
              # host-Koeffizienten des Modells. 1 = original, 0 = aus, > 1 = verstärkt.
              div(class="control-group",
                  div(class="control-label", "东道主优势 🇺🇸🇨🇦🇲🇽 (×)"),
                  sliderInput("dc_host_factor", label=NULL,
                              min=0, max=5, value=1, step=0.1,
                              ticks=FALSE, width="100%")
              ),

              # Torniveau / Intercept (Δ)
              div(class="control-group",
                  div(class="control-label", "总体进球强度 (Δ)"),
                  sliderInput("dc_intercept_delta", label=NULL,
                              min=-0.5, max=0.5, value=0, step=0.05,
                              ticks=FALSE, width="100%")
              ),

          )
        )
      ),

      # ── Mobile: Einstellungshilfe-Button (nur auf schmalen Bildschirmen sichtbar) ──
      div(class="help-link-mobile",
          uiOutput("help_link_einstellungen_mobile", class="help-slot")
      ),
      # ── Simulieren-Button (zentral, außerhalb der Box) ─────────
      div(class="run-section",
          actionButton("run_btn", "▶ 开始模拟", class="btn")
      ),
      # ── Mobile: Methodik-Button (nur auf schmalen Bildschirmen sichtbar) ──
      div(class="help-link-mobile below",
          uiOutput("help_link_methodik_mobile", class="help-slot")
      ),
      uiOutput("podium_ui"),

      tabsetPanel(id="main_tabs",
                  tabPanel("🏅 小组积分榜", div(style="margin-top:16px;", uiOutput("groups_ui"))),
                  tabPanel("⚽ 小组赛程", div(style="margin-top:16px;", uiOutput("group_matches_ui"))),
                  tabPanel("⚔️ 淘汰赛", div(style="margin-top:16px;", uiOutput("ko_ui"))),
                  tabPanel(
                    "🌦️ 天气与球场",
                    div(
                      style = "margin-top:16px;",
                      selectInput(
                        "context_match",
                        "选择比赛",
                        choices = setNames(match_schedule$match_number, match_schedule$choice_label_zh),
                        selected = default_context_match,
                        width = "100%"
                      ),
                      uiOutput("context_ui")
                    )
                  ),
                  tabPanel("⚙️ 球队参数", div(style="margin-top:16px;", uiOutput("elo_ui")))
      ),

      # ── Haftungsausschluss am Fuß der App ───────────────────────
      div(class="disclaimer",
          div(class="disclaimer-title", "说明"),
          tags$p("本页面中的模拟结果仅用于教学、学习和娱乐展示，基于 ELO、Dixon-Coles 与 Monte Carlo 等统计方法生成，不构成真实比赛结果承诺，也不构成任何博彩或投资建议。"),
          tags$p("新增的天气与球场模块只提供赛前上下文参考，目前不会直接改写 ELO 或 Dixon-Coles 的核心概率计算。任何基于本页面作出的判断与决策，均由使用者自行承担责任。")
      )
  ),

  tags$script(HTML("
    /* ── Theme ── */
    var lightMode = true;
    document.addEventListener('DOMContentLoaded', function() {
      document.body.classList.add('light-mode');
      document.getElementById('toggle_track').classList.add('on');
      document.getElementById('theme_icon').textContent  = '☀️';
      document.getElementById('theme_label').textContent = '';
    });

    function toggleTheme() {
      lightMode = !lightMode;
      var body  = document.body;
      var track = document.getElementById('toggle_track');
      var icon  = document.getElementById('theme_icon');
      var label = document.getElementById('theme_label');
      if (lightMode) {
        body.classList.add('light-mode');
        track.classList.add('on');
        icon.textContent  = '☀️';
        label.textContent = '';
        document.getElementById('fustat-logo').src = 'FUStatBlueOnGreen.png';
        document.getElementById('stuko-logo').src  = 'StuKoLogoLight_Trans.png';
      } else {
        body.classList.remove('light-mode');
        track.classList.remove('on');
        icon.textContent  = '🌙';
        label.textContent = '';
        document.getElementById('fustat-logo').src = 'FUStatBlueOnGreen_DARK.png';
        document.getElementById('stuko-logo').src  = 'StuKoLogoDark_Trans.png';
      }
    }

    /* ── Spinner ── */
    $(document).on('click', '#run_btn', function() {
      $('#loader').addClass('active');
    });
    $(document).on('shiny:idle', function() {
      $('#loader').removeClass('active');
    });

    /* ── Reset-Handler: setzt Seed-Felder zurück ── */
    /* (Slider/Select/Radio werden vom Server via update*Input zurückgesetzt) */
    $(document).on('shiny:connected', function() {
      Shiny.addCustomMessageHandler('resetUI', function(message) {
        document.getElementById('seed_elo').value = '';
        document.getElementById('seed_dc').value = '';
      });
    });
  "))
  )
}

# ── SERVER ───────────────────────────────────────────────────

# ── SERVER ───────────────────────────────────────────────────

server <- function(input, output, session) {
  # ── Session-Tracking ──
  # Schreibt "start" beim Verbindungsaufbau und "end" beim Schließen
  # der Session in die TSV-Datei (Setup oben in der Datei).
  log_session_event("start", session$token)
  session$onSessionEnded(function() {
    log_session_event("end", session$token)
  })

  result <- reactiveVal(NULL)

  # ── Modell-abhängige Hilfe-Links (Einstellungen + Methodik) ──
  # ELO und Dixon-Coles haben getrennte Hilfe-/Methodik-Seiten. Die Links
  # werden server-seitig gerendert und folgen dem aktiven Reiter
  # (input$prediction_model). Genutzt sowohl im Desktop-Header als auch in
  # den beiden Mobile-Buttons.
  help_urls <- reactive({
    if (identical(input$prediction_model %||% "elo", "dixon_coles")) {
      list(
        einstellungen = "https://www.wiwiss.fu-berlin.de/wm2026/DC_Einstellungen.html",
        methodik      = "https://www.wiwiss.fu-berlin.de/wm2026/DC_Methodik.html"
      )
    } else {
      list(
        einstellungen = "https://www.wiwiss.fu-berlin.de/wm2026/Elo_Einstellungen.html",
        methodik      = "https://www.wiwiss.fu-berlin.de/wm2026/Elo_Methodik.html"
      )
    }
  })

  output$help_links_desktop <- renderUI({
    u <- help_urls()
    tagList(
      tags$a(href = u$einstellungen, target = "_blank", class = "help-link",
             "ℹ️ 参数说明"),
      tags$a(href = u$methodik, target = "_blank", class = "help-link",
             "📐 方法说明")
    )
  })
  output$help_link_einstellungen_mobile <- renderUI({
    tags$a(href = help_urls()$einstellungen, target = "_blank", class = "help-link",
           "ℹ️ 参数说明")
  })
  output$help_link_methodik_mobile <- renderUI({
    tags$a(href = help_urls()$methodik, target = "_blank", class = "help-link",
           "📐 方法说明")
  })

  # ── Persistenter Speicher für die Per-Team-ELO-Slider ──
  # Wir cachen die zuletzt vom User eingestellten Slider-Werte (Slider-Wert
  # = gewünschte Start-ELO im Bereich 1000–2500) in einem reactiveValues-Container.
  # So überleben die Einstellungen jedes Re-Rendering der ELO-Tabelle, ohne
  # auf das (beim Re-Render unzuverlässige) input$adj_<id> angewiesen zu sein.
  adj_state <- reactiveValues(
    values = setNames(as.list(round(teams_init$elo)),
                      as.character(teams_init$id))
  )

  # ── Sync: Slider-Veränderungen → reactiveValues ──
  # Wird einmal pro Team registriert. Jeder observeEvent feuert nur, wenn der
  # zugehörige Slider tatsächlich (vom User) verändert wurde.
  lapply(teams_init$id, function(tid) {
    input_id <- paste0("adj_", tid)
    observeEvent(input[[input_id]], {
      adj_state$values[[as.character(tid)]] <- as.numeric(input[[input_id]])
    }, ignoreInit = TRUE)
  })

  # ── Dixon-Coles: persistente Slider-States für Angriff & Abwehr (absolut, 0–2.5) ──
  # Slider zeigen exp(attack_log) bzw. exp(defense_log) — d.h. 1.0 = neutral.
  # Init aus dem gefitteten Modell, damit untouched = Originalverhalten.
  # Fallback auf 1.0 (neutraler Wert), falls Modell oder Team-ID nicht verfügbar.
  dc_init_values <- local({
    n <- nrow(teams_init)
    att_default <- setNames(as.list(rep(0, n)), as.character(teams_init$id))
    def_default <- setNames(as.list(rep(0, n)), as.character(teams_init$id))
    if (dc_available()) {
      tryCatch({
        fit <- load_dc_model()
        p_a <- fit$parameters$attack
        p_d <- fit$parameters$defense
        mu_fit <- as.numeric(fit$parameters$intercept %||% 0)
        for (idc in as.character(teams_init$id)) {
          va <- p_a[idc]; vd <- p_d[idc]
          # Slider-Init = direkter Modellparameter (log-Skala, Range ~−3 bis +1.5).
          if (length(va) > 0 && !is.na(va)) att_default[[idc]] <- round(as.numeric(va), 2)
          if (length(vd) > 0 && !is.na(vd)) def_default[[idc]] <- round(as.numeric(vd), 2)
        }
      }, error = function(e) {
        message("DC-Initialisierung fehlgeschlagen: ", conditionMessage(e))
      })
    }
    list(attack = att_default, defense = def_default)
  })
  dc_att_state <- reactiveValues(values = dc_init_values$attack)
  dc_def_state <- reactiveValues(values = dc_init_values$defense)
  lapply(teams_init$id, function(tid) {
    att_id <- paste0("dc_att_", tid)
    def_id <- paste0("dc_def_", tid)
    observeEvent(input[[att_id]], {
      dc_att_state$values[[as.character(tid)]] <- as.numeric(input[[att_id]])
    }, ignoreInit = TRUE)
    observeEvent(input[[def_id]], {
      dc_def_state$values[[as.character(tid)]] <- as.numeric(input[[def_id]])
    }, ignoreInit = TRUE)
  })

  # Run on startup with defaults (entspricht ursprünglichem Verhalten)
  # Wichtig: seed = 111 mit default_params ist deterministisch und für ALLE Sessions
  # identisch. Wir berechnen das genau einmal pro R-Prozess und teilen das Ergebnis —
  # spart bei N parallelen Session-Starts (N−1) Simulationen.
  observe({ result(default_result_cache()) })

  observeEvent(input$run_btn, {
    seed_input <- if (identical(input$prediction_model, "dixon_coles")) {
      input$seed_dc
    } else {
      input$seed_elo
    }
    seed <- suppressWarnings(as.integer(seed_input))
    if (is.na(seed)) seed <- as.integer(as.numeric(Sys.time())) %% .Machine$integer.max

    # Per-Team-ELO-Adjustments aus dem persistenten Cache einsammeln und in
    # Differenzen zur Original-Start-ELO umrechnen, weil apply_elo_modifiers
    # die Werte additiv aufschlägt. Auf [-500, 500] geclamped als Schutz vor
    # extremen Eingaben.
    orig_lookup <- setNames(teams_init$elo, as.character(teams_init$id))
    adj_vec <- sapply(teams_init$id, function(tid) {
      key   <- as.character(tid)
      slv   <- adj_state$values[[key]]
      if (is.null(slv) || is.na(slv)) return(0)
      diff <- as.numeric(slv) - as.numeric(orig_lookup[[key]])
      max(-500, min(500, diff))
    })
    names(adj_vec) <- as.character(teams_init$id)

    # DC-Per-Team-Werte aus den reactiveValues einsammeln.
    # Werte sind absolute Slider-Stände auf 0–2.5 Skala (exp(attack_log)).
    dc_att_vec <- sapply(teams_init$id, function(tid) {
      v <- dc_att_state$values[[as.character(tid)]]
      if (is.null(v) || is.na(v)) 1.0 else as.numeric(v)
    })
    dc_def_vec <- sapply(teams_init$id, function(tid) {
      v <- dc_def_state$values[[as.character(tid)]]
      if (is.null(v) || is.na(v)) 1.0 else as.numeric(v)
    })
    names(dc_att_vec) <- as.character(teams_init$id)
    names(dc_def_vec) <- as.character(teams_init$id)

    # UI-Werte in params-Liste übersetzen.
    # Alle Defaults entsprechen dem Originalverhalten der App.
    user_params <- modifyList(default_params, list(
      k                      = as.integer(input$k_slider %||% 60),
      use_historical         = isTRUE(input$use_historical == "1"),
      home_advantage         = as.numeric(input$home_advantage   %||% 0),
      team_boost_id          = as.integer(input$team_boost_id    %||% NA),
      team_boost_value       = as.numeric(input$team_boost_value %||% 0),
      team_adjustments       = adj_vec,
      goal_scale             = as.numeric(input$goal_scale       %||% 1.0),
      draw_max               = as.numeric(input$draw_max         %||% (.3)),
      upset_factor           = 1 - as.numeric(input$upset_factor %||% 0),
      prediction_model       = input$prediction_model %||% "elo",
      dc_host_factor         = as.numeric(input$dc_host_factor     %||% 1),
      dc_intercept_delta     = as.numeric(input$dc_intercept_delta %||% 0),
      dc_attack_values       = dc_att_vec,
      dc_defense_values      = dc_def_vec
    ))

    # Asynchrone Berechnung im Hintergrund-Worker. Der R-Hauptprozess
    # bleibt frei für andere Sessions, während diese Simulation läuft.
    # Lokale Kopien, damit der Future garantiert die richtigen Werte
    # captured (defensive Programmierung gegen Lazy-Evaluation-Überraschungen).
    local_seed   <- seed
    local_params <- user_params
    local_simfile <- sim_file
    # globals = nur die drei kleinen Objekte (seed, params, Pfad). Dadurch
    # wird NICHT mehr der gesamte ~49 MB Funktions-/Datenballast pro Aufruf
    # in den Worker serialisiert (das war die RAM-Leak-Ursache).
    # Der Worker sourct simulation.R genau EINMAL pro Prozess: beim ersten
    # future lädt er Daten+Funktionen in sein globales Environment und cached
    # das über das Flag .wm2026_sim_loaded. Folge-Aufrufe finden alles vor.
    future_promise({
      if (!isTRUE(get0(".wm2026_sim_loaded", ifnotfound = FALSE))) {
        # Worker startet i.d.R. NICHT im App-Verzeichnis. simulation.R nutzt
        # relative Pfade (../data/...), daher vor dem Sourcing dorthin wechseln.
        setwd(dirname(local_simfile))
        source(local_simfile, local = FALSE)
        .wm2026_sim_loaded <<- TRUE
      }
      run_tournament(seed = local_seed, params = local_params)
    },
    seed = TRUE,
    globals = list(local_seed = local_seed,
                   local_params = local_params,
                   local_simfile = local_simfile),
    packages = character(0)) %...>%
      result() %...!%
      (function(e) {
        showNotification(
          paste("Simulation fehlgeschlagen:", conditionMessage(e)),
          type = "error", duration = 10
        )
      })
    # WICHTIG: NULL zurückgeben, damit observeEvent keinen Promise zurückgibt
    # (Shiny würde sonst eine Warnung loggen).
    NULL
  })
  # ── Zurücksetzen-Button: alle Einstellungen auf Default ──
  # Default-Werte stammen aus default_params (siehe Datei-Anfang).
  # JS-Anteil (Seed-Feld leeren) läuft über Custom Message,
  # weil das Seed-Feld kein klassisches Shiny-Input ist.
  # Die Per-Team-Slider werden bewusst NICHT mit zurückgesetzt — dafür gibt es
  # einen eigenen Button in der ELO-Rangliste, weil sie konzeptuell dorthin gehören.
  observeEvent(input$reset_btn, {
    # Modus-abhängig: nur die Slider des aktuell sichtbaren Tabs zurücksetzen.
    # Insbesondere NICHT den Tab wechseln — der User bleibt da wo er ist.
    current_mode <- input$prediction_model %||% "elo"

    if (identical(current_mode, "elo")) {
      updateSliderInput(session, "k_slider",           value = default_params$k)
      updateSliderInput(session, "home_advantage",     value = default_params$home_advantage)
      updateSliderInput(session, "upset_factor",       value = 0)
      updateSliderInput(session, "goal_scale",         value = default_params$goal_scale)
      updateSliderInput(session, "draw_max",           value = default_params$draw_max)
      updateSliderInput(session, "team_boost_value",   value = default_params$team_boost_value)
      updateRadioButtons(session, "use_historical",    selected = "0")
      updateSelectInput(session, "team_boost_id",
                        selected = (teams_init %>%
                                      filter(fifa_code == "GER") %>%
                                      pull(id))[1])
    } else if (identical(current_mode, "dixon_coles")) {
      updateSliderInput(session, "dc_host_factor",     value = default_params$dc_host_factor)
      updateSliderInput(session, "dc_intercept_delta", value = default_params$dc_intercept_delta)
    }
    session$sendCustomMessage("resetUI", list())
  })

  # ── Per-Team-ELO-Slider: Reset-Button im ELO-Tab ──
  # Setzt alle Slider AUF die jeweilige Original-Start-ELO zurück,
  # womit alle Anpassungen wieder 0 sind.
  # Greift wirksam erst beim nächsten "Simulieren"-Klick (wie alle anderen Einstellungen).
  observeEvent(input$reset_adj_btn, {
    for (i in seq_len(nrow(teams_init))) {
      tid  <- teams_init$id[i]
      orig <- round(teams_init$elo[i])
      updateSliderInput(session, paste0("adj_", tid), value = orig)
      adj_state$values[[as.character(tid)]] <- orig
    }
  })

  # ── DC-Per-Team-Slider: Reset-Button in der Rangliste (DC-Modus) ──
  # Setzt alle Angriffs-Δ und Abwehr-Δ Slider auf 0 zurück.
  observeEvent(input$reset_dc_btn, {
    # Reset = zurück zu den exp(Originalwerten) des gefitteten Modells.
    fit_full <- if (dc_available()) tryCatch(load_dc_model(), error = function(e) NULL) else NULL
    p_att <- if (dc_available()) tryCatch(load_dc_model()$parameters$attack,  error = function(e) NULL) else NULL
    p_def <- if (dc_available()) tryCatch(load_dc_model()$parameters$defense, error = function(e) NULL) else NULL

    for (i in seq_len(nrow(teams_init))) {
      tid <- teams_init$id[i]
      idc <- as.character(tid)
      av <- if (!is.null(p_att)) p_att[idc] else NA
      dv <- if (!is.null(p_def)) p_def[idc] else NA
      a_init <- if (length(av) > 0 && !is.na(av)) round(as.numeric(av), 2) else 0
      d_init <- if (length(dv) > 0 && !is.na(dv)) round(as.numeric(dv), 2) else 0
      updateSliderInput(session, paste0("dc_att_", tid), value = a_init)
      updateSliderInput(session, paste0("dc_def_", tid), value = d_init)
      dc_att_state$values[[idc]] <- a_init
      dc_def_state$values[[idc]] <- d_init
    }
  })

  # ── Podium ──
  output$podium_ui <- renderUI({
    r <- result(); req(r)
    champ  <- r$champion; runner <- r$runner_up; third <- r$third

    make_card <- function(team, cls, label, trophy) {
      elo_val <- r$final_elo %>% filter(id == team$id) %>% pull(final_elo)
      div(class=paste("podium-card", cls),
          div(class="podium-label", label),
          tags$span(class="trophy", trophy),
          tags$span(class="podium-flag", get_flag(team$fifa_code)),
          div(class="podium-team", team$team_name_de),
          div(style="color:var(--muted);font-size:11px;margin-top:4px;",
              paste("ELO:", round(elo_val)))
      )
    }

    tagList(div(class="podium",
                make_card(runner, "second", "亚军", "🥈"),
                make_card(champ,  "first",  "冠军", "🏆"),
                make_card(third,  "third",  "季军", "🥉")
    ))
  })

  # ── Gruppen-Tabellen ──
  output$groups_ui <- renderUI({
    r <- result(); req(r)
    std <- r$standings
    cards <- lapply(sort(unique(std$group)), function(grp) {
      gd <- std %>% filter(group == grp) %>% arrange(rank)
      rows <- lapply(1:nrow(gd), function(i) {
        row    <- gd[i,]
        cls    <- if (i <= 2) "qualify" else if (i == 3) "qualify-3rd" else ""
        gd_val <- row$gd
        gd_cls <- if (gd_val > 0) "gd-pos" else if (gd_val < 0) "gd-neg" else ""
        gd_str <- if (gd_val > 0) paste0("+", gd_val) else as.character(gd_val)
        tags$tr(class=cls,
                tags$td(tags$span(class=paste("rank-badge", paste0("rank-", i)), i),
                        get_flag(row$fifa_code), " ", row$team_name_de),
                tags$td(class="pts-cell", row$pts),
                tags$td(row$gf), tags$td(row$ga),
                tags$td(class=gd_cls, gd_str),
                tags$td(style="color:var(--muted);font-size:12px;", round(row$elo))
        )
      })
      div(class="group-card",
          div(class="group-header", paste0(grp, "组")),
          tags$table(class="group-table",
                     tags$thead(tags$tr(
                       tags$th("球队"), tags$th("积分"), tags$th("进球"),
                       tags$th("失球"), tags$th("净胜球"), tags$th("ELO")
                     )),
                     tags$tbody(rows)
          )
      )
    })
    div(class="groups-grid", cards)
  })

  # ── Gruppenspiele ──
  output$group_matches_ui <- renderUI({
    r <- result(); req(r)
    gm <- r$group_matches
    sections <- lapply(sort(unique(gm$group)), function(grp) {
      ms   <- gm %>% filter(group == grp)
      rows <- lapply(1:nrow(ms), function(i) {
        m <- ms[i,]
        tags$tr(tags$td(m$home), tags$td(class="ko-score", m$score), tags$td(m$away))
      })
      div(class="ko-section",
          div(class="ko-round-title", paste0(grp, "组")),
          tags$table(class="ko-table",
                     tags$thead(tags$tr(
                       tags$th("主队"), tags$th(style="text-align:center","比分"), tags$th("客队")
                     )),
                     tags$tbody(rows)
          )
      )
    })
    div(sections)
  })

  # ── K.O.-Runde ──
  output$ko_ui <- renderUI({
    r <- result(); req(r)
    ko     <- r$ko_matches
    rounds <- c("Round of 32","Round of 16","Quarter-Final","Semi-Final","Third Place","Final")
    sections <- lapply(rounds, function(rnd) {
      ms <- ko %>% filter(stage == rnd)
      if (nrow(ms) == 0) return(NULL)
      rows <- lapply(1:nrow(ms), function(i) {
        m <- ms[i,]
        tags$tr(tags$td(m$home), tags$td(class="ko-score", m$score),
                tags$td(m$away), tags$td(class="ko-winner", m$result))
      })
      div(class="ko-section",
          div(class="ko-round-title", stage_de_map[rnd]),
          tags$table(class="ko-table",
                     tags$thead(tags$tr(
                       tags$th("主队 / A 位"), tags$th(style="text-align:center","比分"),
                       tags$th("客队 / B 位"), tags$th("胜者")
                     )),
                     tags$tbody(rows)
          )
      )
    })
    div(sections)
  })

  output$context_ui <- renderUI({
    req(input$context_match)
    match_row <- match_schedule %>%
      filter(match_number == as.integer(input$context_match)) %>%
      slice(1)
    req(nrow(match_row) == 1)

    weather <- get_match_weather(match_row)
    notes <- build_match_context_notes(match_row, weather)

    metric_card <- function(label, value) {
      div(
        style = paste(
          "background:var(--panel);border:1px solid var(--border);border-radius:10px;",
          "padding:12px 14px;min-height:84px;display:flex;flex-direction:column;",
          "justify-content:center;gap:4px;"
        ),
        div(style = "font-size:12px;color:var(--muted);text-transform:uppercase;", label),
        div(style = "font-size:20px;font-weight:700;color:var(--text);", value)
      )
    }

    weather_block <- if (identical(weather$status, "ok")) {
      div(
        style = "display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:14px;",
        metric_card("天气", weather_code_zh(weather$weather_code)),
        metric_card("气温", paste0(round(weather$temperature_2m), "°C")),
        metric_card("体感", paste0(round(weather$apparent_temperature), "°C")),
        metric_card("湿度", paste0(round(weather$relative_humidity_2m), "%")),
        metric_card("风速", paste0(round(weather$wind_speed_10m), " km/h")),
        metric_card("降水概率", paste0(round(weather$precipitation_probability), "%"))
      )
    } else {
      div(
        style = "margin-top:14px;padding:14px 16px;background:var(--panel);border:1px solid var(--border);border-radius:10px;color:var(--muted);",
        weather$message
      )
    }

    div(
      style = "display:flex;flex-direction:column;gap:14px;",
      div(
        style = "background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px;",
        div(style = "font-size:24px;font-weight:700;", paste0("M", match_row$match_number, " ", match_row$matchup_label_zh)),
        div(style = "margin-top:6px;color:var(--muted);",
            paste(match_row$stage_label_zh, match_row$kickoff_label_zh, sep = " | ")),
        div(style = "margin-top:6px;color:var(--muted);",
            paste0(match_row$stadium_zh, " / ", match_row$city_zh, " / ", match_row$country_zh))
      ),
      div(
        style = "display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;",
        metric_card("球场环境", roof_type_zh(match_row$roof_type)),
        metric_card("海拔", paste0(round(match_row$altitude_m), " m")),
        metric_card("草坪", match_row$pitch_type),
        metric_card("当前模块", "辅助分析")
      ),
      weather_block,
      div(
        style = "background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px;",
        div(style = "font-size:16px;font-weight:700;margin-bottom:10px;", "赛前解读"),
        tags$ul(
          style = "margin:0;padding-left:20px;display:flex;flex-direction:column;gap:8px;",
          lapply(notes, tags$li)
        )
      )
    )
  })

  # ── ELO-Rangliste ──
  # Spaltenreihenfolge: # | Team | Start-ELO | ELO-Anpassung (Slider 1000–2500)
  #                     | ELO-Änderung (Slider − Start-ELO) | End-ELO
  #
  # Persistenz: Slider-Werte werden in adj_state$values gehalten und beim
  # Re-Render der Tabelle als Default-Wert benutzt. Beim allerersten Aufbau
  # eines Slider-Eintrags ist der Wert = Original-Start-ELO (siehe Initialisierung
  # von adj_state oben), so dass das angezeigte Delta beim ersten Mal 0 ist.
  output$elo_ui <- renderUI({
    mode <- input$prediction_model %||% "elo"

    # ── Dixon-Coles-Modus: Per-Team-Slider (absolut, 0–2.5; 1.0 = neutral) ──
    if (identical(mode, "dixon_coles")) {
      if (!dc_available()) {
        return(div(style="margin-top:16px;color:var(--muted);",
                   "Dixon-Coles 模型当前不可用。"))
      }
      model_fit <- load_dc_model()
      p_att <- model_fit$parameters$attack
      p_def <- model_fit$parameters$defense

      # Sortierung nach Originalstärke (attack − defense auf log-Skala).
      dc_df <- teams_init %>%
        mutate(
          id_chr      = as.character(id),
          flag        = sapply(fifa_code, get_flag),
          attack_log  = as.numeric(p_att[id_chr]),
          defense_log = as.numeric(p_def[id_chr])
        ) %>%
        filter(!is.na(attack_log) & !is.na(defense_log)) %>%
        arrange(desc(attack_log - defense_log))
      if (nrow(dc_df) == 0) {
        return(div(style="margin-top:16px;color:var(--muted);",
                   "没有找到可用于 Dixon-Coles 的球队参数。"))
      }

      # Slider-Zeile (#, Team, EIN Slider) für einen Reiter bauen.
      # `which` = "att" oder "def" wählt Angriffs- bzw. Abwehrparameter.
      # Beide Reiter werden gleichzeitig ins DOM gerendert (Bootstrap blendet
      # nur den inaktiven aus), damit beide Slider-Sätze registriert/persistent
      # bleiben — auf dem Handy ist je Reiter nur EINE schmale Slider-Spalte
      # sichtbar, sodass beide Werte mobil einstellbar sind.
      make_dc_rows <- function(which) {
        lapply(seq_len(nrow(dc_df)), function(i) {
          row <- dc_df[i, ]
          idc <- as.character(row$id)
          if (identical(which, "att")) {
            sid <- paste0("dc_att_", row$id)
            cur <- isolate(dc_att_state$values[[idc]])
            if (is.null(cur) || is.na(cur)) cur <- round(row$attack_log, 2)
          } else {
            sid <- paste0("dc_def_", row$id)
            cur <- isolate(dc_def_state$values[[idc]])
            if (is.null(cur) || is.na(cur)) cur <- round(row$defense_log, 2)
          }
          tags$tr(
            tags$td(as.character(i)),
            tags$td(paste(row$flag, row$team_name_de)),
            tags$td(div(class="elo-adj-slider",
                        sliderInput(sid, label = NULL,
                                    min = -1, max = 2.5,
                                    value = cur, step = 0.05,
                                    ticks = FALSE, width = "100%")))
          )
        })
      }

      dc_table <- function(rows, value_header) {
        tags$table(class="ko-table dc-team-table",
                   tags$thead(tags$tr(
                     tags$th("#"),
                     tags$th("球队"),
                     tags$th(value_header)
                   )),
                   tags$tbody(rows)
        )
      }

      return(tagList(
        div(class="elo-adj-reset-wrap",
            actionButton("reset_dc_btn", "↺ 重置 DC 调整", class="btn-reset")
        ),
        # Zwei Reiter: Angriffs- und Abwehrstärke getrennt, damit beide auch
        # auf schmalen (mobilen) Displays vollständig bedienbar sind.
        div(class="dc-tabs-wrap",
            tabsetPanel(
              id = "dc_team_tabs", type = "tabs",
              tabPanel("进攻强度", dc_table(make_dc_rows("att"), "进攻强度")),
              tabPanel("防守强度", dc_table(make_dc_rows("def"), "防守强度"))
            )
        )
      ))
    }

    # ── ELO-Modus: bisherige Rangliste ──
    r <- result(); req(r)
    fe <- r$final_elo
    # Wenn beim Modus-Wechsel das letzte Simulationsergebnis aus dem DC-Lauf
    # stammt, hat es keine final_elo-Komponente. In dem Fall einen Platzhalter
    # zeigen statt zu crashen.
    if (is.null(fe) || !is.data.frame(fe) || nrow(fe) == 0) {
      return(div(style="margin-top:16px;color:var(--muted);",
                 "请先点击一次“开始模拟”，再查看 ELO 排名。"))
    }

    rows <- lapply(seq_len(nrow(fe)), function(i) {
      row     <- fe[i,]
      orig    <- as.numeric(row$orig_elo)        # ORIGINAL Start-ELO (vor Modifiern)
      medal   <- as.character(i)                 # Nur Platznummer, keine Medaille
      slider_id <- paste0("adj_", row$id)

      # Aktueller Slider-Wert aus dem persistenten Cache (überlebt Re-Renderings).
      # isolate(): wir wollen den aktuellen Wert beim Aufbau der Tabelle lesen,
      # aber KEINE reaktive Abhängigkeit erzeugen — sonst würde jeder
      # Slider-Schub die ganze Tabelle neu rendern.
      cur_val <- isolate(adj_state$values[[as.character(row$id)]])
      if (is.null(cur_val) || is.na(cur_val)) cur_val <- orig

      # Turnier-Δ: Differenz zwischen Endstand und Start-ELO NACH Modifiern.
      # Diese Spalte zeigt ausschließlich das Ergebnis der Simulation und ändert
      # sich nicht beim Schieben der Regler — erst wenn Simulieren neu gedrückt wird.
      tour_delta     <- as.numeric(row$change)
      tour_delta_cls <- if (tour_delta > 0) "elo-up" else if (tour_delta < 0) "elo-dn" else ""
      tour_delta_str <- if (tour_delta > 0) paste0("+", round(tour_delta)) else as.character(round(tour_delta))

      tags$tr(
        tags$td(medal),
        tags$td(paste(row$flag, row$team_name_de)),
        # Start-ELO: in Textfarbe (schwarz im Light Mode, weiß im Dark Mode)
        tags$td(style="font-family:monospace;color:var(--text);", orig),
        # ELO-Anpassung: voller Shiny-Slider in der Tabellenzelle
        tags$td(div(class="elo-adj-slider",
                    sliderInput(slider_id, label = NULL,
                                min = 1000, max = 2500,
                                value = cur_val, step = 10,
                                ticks = FALSE, width = "100%"))),
        # Turnier-Δ: rein lesend, Vorzeichen + Farbe
        tags$td(class=paste("elo-user-delta", tour_delta_cls), tour_delta_str),
        # End-ELO: nach Simulation
        tags$td(style="font-family:monospace;font-weight:600;color:var(--gold);", row$final_elo)
      )
    })

    tagList(
      div(class="elo-adj-reset-wrap",
          actionButton("reset_adj_btn", "↺ 重置 ELO 调整", class="btn-reset")
      ),
      tags$table(class="ko-table elo-rangliste-table",
                 tags$thead(tags$tr(
                   tags$th("#"),
                   tags$th("球队"),
                   tags$th("初始 ELO"),
                   tags$th("ELO 调整"),
                   tags$th("赛事 Δ"),
                   tags$th("最终 ELO")
                 )),
                 tags$tbody(rows)
      )
    )
  })
}

shinyApp(ui, server)

```
