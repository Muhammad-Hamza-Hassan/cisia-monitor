import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://testcisia.it/calendario.php?tolc=cents&l=gb&lingua=inglese"
NTFY_TOPIC = "Cisia_CENT-S_tracking_bot_nigga"  
STATE_FILE = "seen_slots.json"

def send_push(title, message, priority="high"):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": "rotating_light,mortar_board",
            "Click": URL
        },
        timeout=10
    )

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(slots):
    with open(STATE_FILE, "w") as f:
        json.dump(list(slots), f)

def main():
    send_push("Test", "Bot is alive!")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tbody tr")

    seen = load_seen()
    current_open = set()

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 8:
            fmt, uni, _, _, deadline, seats, state, date = cols[:8]

            # Monitors CENT@HOME seats
            if "CENT@UNI" in fmt and "AVAILABLE SEATS" in state.upper():
                slot_id = f"{fmt}|{uni}|{date}"
                current_open.add(slot_id)

                if slot_id not in seen:
                    msg = (
                        f"Format: {fmt}\n"
                        f"University: {uni}\n"
                        f"Test Date: {date}\n"
                        f"Deadline: {deadline} | Seats: {seats}\n"
                        f"Tap notification to open CISIA!"
                    )
                    send_push("CENT@UNI SEAT OPEN!", msg, priority="urgent")
                    print("ALERT SENT:", slot_id)

    save_seen(current_open)
    print(f"Done. Open CENT@HOME slots right now: {len(current_open)}")

if __name__ == "__main__":
    main()
