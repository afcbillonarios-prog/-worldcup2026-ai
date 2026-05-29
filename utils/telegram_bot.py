import requests
import json
import time
import os
from datetime import datetime

def get_bot_token():
    try:
        import streamlit as st
        return st.secrets.get("TELEGRAM_BOT_TOKEN")
    except (ImportError, Exception):
        pass
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    return "8698243400:AAGtghFXqdTWcTaZx64p3XeNUTo6fCMEoOE"

BOT_TOKEN = get_bot_token()
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, parse_mode="HTML"):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_updates(limit=10):
    url = f"{BASE_URL}/getUpdates"
    try:
        resp = requests.get(url, params={"limit": limit, "timeout": 10}, timeout=15)
        data = resp.json()
        if data.get("ok"):
            chats = []
            for update in data.get("result", []):
                msg = update.get("message") or update.get("channel_post") or {}
                chat = msg.get("chat", {})
                if chat.get("id"):
                    chats.append({
                        "chat_id": chat["id"],
                        "type": chat.get("type", "unknown"),
                        "title": chat.get("title") or f"{chat.get('first_name', '')} {chat.get('last_name', '')}",
                        "username": chat.get("username", ""),
                    })
            return chats
        return []
    except Exception as e:
        return []

def format_signal_message(signals, match_time=0, team_a=None, team_b=None):
    emoji_map = {
        "xG_dynamics": "🎯",
        "possession": "⚽",
        "pressing_intensity": "🔥",
        "momentum": "📈",
        "defensive_line": "🛡️",
        "fatigue": "😰",
        "attack_danger": "⚡",
        "control_index": "🎮",
        "expected_goals": "🥅",
        "shot_accuracy": "🎯",
    }
    label_map = {
        "xG_dynamics": "xG Dinámico",
        "possession": "Posesión",
        "pressing_intensity": "Presión Alta",
        "momentum": "Momentum",
        "defensive_line": "Línea Defensiva",
        "fatigue": "Fatiga",
        "attack_danger": "Peligro Ofensivo",
        "control_index": "Control Juego",
        "expected_goals": "xG Esperado",
        "shot_accuracy": "% Tiro",
    }

    line = "━" * 30
    header = f"🏆 <b>WORLD CUP 2026</b> 🏆\n{line}\n"
    if team_a and team_b:
        header += f"⚔️ <b>{team_a} vs {team_b}</b>\n"
    header += f"⏱️ Minuto {match_time}\n📅 {datetime.now().strftime('%H:%M:%S')}\n{line}\n\n"

    signals_text = ""
    for key, value in signals.items():
        if key == "minute":
            continue
        emoji = emoji_map.get(key, "📊")
        label = label_map.get(key, key.replace("_", " ").title())
        bar_len = int(value / 100 * 15) if value <= 100 else min(int(value * 3), 15)
        bar = "█" * bar_len + "░" * (15 - bar_len)

        if isinstance(value, float):
            val_str = f"{value:.2f}" if value < 1 else f"{value:.1f}"
        else:
            val_str = str(value)
        signals_text += f"{emoji} <b>{label}:</b> {val_str}\n{bar}\n\n"

    footer = f"{line}\n🤖 <i>AI Analytics · Señales en vivo</i>"

    return header + signals_text + footer

def format_alert_message(alert_type, description, team_a=None, team_b=None):
    icons = {
        "goal": "⚽⚽⚽",
        "shot": "🔫",
        "card": "🟨",
        "penalty": "🔴",
        "substitution": "🔄",
        "injury": "🚑",
        "var": "📺",
    }
    icon = icons.get(alert_type, "📌")
    line = "─" * 25
    text = f"{line}\n{icon} <b>ALERTA</b> {icon}\n{line}\n"
    if team_a and team_b:
        text += f"⚔️ {team_a} vs {team_b}\n"
    text += f"⏱️ {datetime.now().strftime('%H:%M:%S')}\n\n"
    text += f"<b>{description}</b>\n{line}"
    return text

def send_signal_alert(chat_id, signals, match_time=0, team_a=None, team_b=None):
    msg = format_signal_message(signals, match_time, team_a, team_b)
    return send_message(chat_id, msg)

def send_event_alert(chat_id, alert_type, description, team_a=None, team_b=None):
    msg = format_alert_message(alert_type, description, team_a, team_b)
    return send_message(chat_id, msg)

def test_bot():
    updates = get_updates(1)
    if updates:
        chat_id = updates[0]["chat_id"]
        resp = send_message(chat_id, "🤖 <b>World Cup 2026 AI Analytics</b>\n✅ Conexión establecida correctamente")
        return resp.get("ok", False), chat_id
    return False, None
