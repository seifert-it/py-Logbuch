# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 08:50:31 2026

@author: G6
"""
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "logbuch.csv"

def show_menu():
    print("\n=== LOGBUCH ===")
    print("1) Eintrag hinzufügen")
    print("2) Einträge anzeigen")
    print("3) Suche")
    print("4) Statistik")
    print("5) Letzte 7 Tage anzeigen")
    print("6) Einträge von–bis anzeigen")
    print("0) Beenden")

def ensure_file_exists():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("datum;kategorie;text\n", encoding="utf-8")

def add_entry():
    category = input("Kategorie: ").strip()
    text = input("Text: ").strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    line = f"{date};{category};{text}\n"

    ensure_file_exists()

    with DATA_FILE.open("a", encoding="utf-8") as f:
        f.write(line)

    print("✅ Eintrag gespeichert.")

def list_entries():
    if not DATA_FILE.exists():
        print("Noch keine Einträge vorhanden.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("Noch keine Einträge vorhanden.")
        return

    print("\n--- EINTRÄGE ---")
    for i, line in enumerate(lines[1:], start=1):
        date, category, text = line.strip().split(";", maxsplit=2)
        print(f"{i:>2}. [{date}] ({category}) {text}")

def search_entries():
    if not DATA_FILE.exists():
        print("Noch keine Einträge vorhanden.")
        return

    print("\nSuche in:")
    print("1) Kategorie")
    print("2) Text")
    print("3) Kategorie + Text")
    print("4) Datum (z.B. 2026-01-07 oder 2026-01)")
    mode = input("Modus (1-4): ").strip()

    query = input("Suchbegriff(e): ").strip().lower()
    if not query:
        print("❌ Leere Sucheingabe.")
        return

    terms = [t for t in query.split() if t]

    with DATA_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    found_any = False
    print("\n--- SUCHERGEBNISSE ---")

    for i, line in enumerate(lines[1:], start=1):
        date, category, text = line.strip().split(";", maxsplit=2)

        date_l = date.lower()
        category_l = category.lower()
        text_l = text.lower()

        if mode == "1":
            searchable = category_l
            match = all(t in searchable for t in terms)

        elif mode == "2":
            searchable = text_l
            match = all(t in searchable for t in terms)

        elif mode == "3":
            searchable = f"{category_l} {text_l}"
            match = all(t in searchable for t in terms)

        elif mode == "4":
            # Datumssuche: Prefix-Match (Tag oder Monat)
            match = all(date_l.startswith(t) for t in terms)

        else:
            # Fallback: Kategorie + Text
            searchable = f"{category_l} {text_l}"
            match = all(t in searchable for t in terms)

        if match:
            print(f"{i:>2}. [{date}] ({category}) {text}")
            found_any = True

    if not found_any:
        print("Keine passenden Einträge gefunden.")

def show_stats():
    if not DATA_FILE.exists():
        print("Noch keine Einträge vorhanden.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("Noch keine Einträge vorhanden.")
        return

    count_by_category = {}
    count_by_month = {}
    total = 0
    skipped = 0

    for raw in lines[1:]:
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(";", maxsplit=2)
        if len(parts) != 3:
            skipped += 1
            continue

        date, category, text = parts
        month = date[:7]  # "YYYY-MM"

        count_by_category[category] = count_by_category.get(category, 0) + 1
        count_by_month[month] = count_by_month.get(month, 0) + 1
        total += 1

    def print_bars(title, items, max_width=25):
        print(f"\n{title}")
        if not items:
            print("(keine Daten)")
            return

        max_value = max(v for _, v in items) if items else 0
        label_width = max(len(str(label)) for label, _ in items)

        for label, value in items:
            bar_len = 0 if max_value == 0 else int(round((value / max_value) * max_width))
            bar = "#" * bar_len
            print(f"{str(label):<{label_width}} | {bar:<{max_width}} {value}")

    print("\n=== STATISTIK ===")
    print(f"Gesamt: {total}")

    if total > 0:
        top_cat, top_cat_n = max(count_by_category.items(), key=lambda x: x[1])
        print(f"Top-Kategorie: {top_cat} ({top_cat_n})")

    if skipped:
        print(f"(Hinweis: {skipped} Zeile(n) übersprungen, weil sie nicht dem CSV-Format entsprachen.)")

    cat_items = sorted(count_by_category.items(), key=lambda x: (-x[1], x[0].lower()))
    month_items = sorted(count_by_month.items())  # "YYYY-MM" sortiert chronologisch als Text

    print_bars("Einträge pro Kategorie:", cat_items, max_width=25)
    print_bars("Einträge pro Monat:", month_items, max_width=25)

def list_last_days(days=7):
    """
    Zeigt Einträge der letzten 'days' Tage.
    Nutzt echtes datetime-Parsing statt String-Tricks.
    """
    if not DATA_FILE.exists():
        print("Noch keine Einträge vorhanden.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("Noch keine Einträge vorhanden.")
        return

    cutoff = datetime.now() - timedelta(days=days)

    print(f"\n--- EINTRÄGE: LETZTE {days} TAGE ---")
    found_any = False
    skipped = 0

    for i, raw in enumerate(lines[1:], start=1):
        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split(";", maxsplit=2)
        if len(parts) != 3:
            skipped += 1
            continue

        date_str, category, text = parts

        # Datum aus "YYYY-MM-DD HH:MM" in datetime umwandeln
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            skipped += 1
            continue

        if dt >= cutoff:
            print(f"{i:>2}. [{date_str}] ({category}) {text}")
            found_any = True

    if not found_any:
        print("Keine Einträge in diesem Zeitraum gefunden.")

    if skipped:
        print(f"(Hinweis: {skipped} Zeile(n) übersprungen – Format unerwartet.)")

def parse_user_datetime(s: str):
    """
    Erlaubt:
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DD HH:MM'
    Gibt ein datetime zurück oder None bei Fehler.
    """
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt
        except ValueError:
            pass
    return None


def list_entries_between():
    """
    Fragt von/bis ab und listet alle Einträge im Zeitraum (inklusive Grenzen).
    """
    if not DATA_FILE.exists():
        print("Noch keine Einträge vorhanden.")
        return

    start_s = input("Von (YYYY-MM-DD oder YYYY-MM-DD HH:MM): ").strip()
    end_s = input("Bis (YYYY-MM-DD oder YYYY-MM-DD HH:MM): ").strip()

    start_dt = parse_user_datetime(start_s)
    end_dt = parse_user_datetime(end_s)

    if start_dt is None or end_dt is None:
        print("❌ Ungültiges Datumsformat. Beispiele: 2026-01-07 oder 2026-01-07 08:15")
        return

    # Falls Nutzer nur Datum (ohne Uhrzeit) eingibt, ist das Ende sonst 00:00.
    # Wir machen es nutzerfreundlich: wenn bis nur 'YYYY-MM-DD' war, zählen wir den ganzen Tag.
    if len(end_s) == 10:  # 'YYYY-MM-DD'
        end_dt = end_dt.replace(hour=23, minute=59)

    if start_dt > end_dt:
        print("❌ 'Von' liegt nach 'Bis'.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        print("Noch keine Einträge vorhanden.")
        return

    print(f"\n--- EINTRÄGE: {start_dt.strftime('%Y-%m-%d %H:%M')} bis {end_dt.strftime('%Y-%m-%d %H:%M')} ---")
    found_any = False
    skipped = 0

    for i, raw in enumerate(lines[1:], start=1):
        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split(";", maxsplit=2)
        if len(parts) != 3:
            skipped += 1
            continue

        date_str, category, text = parts

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            skipped += 1
            continue

        if start_dt <= dt <= end_dt:
            print(f"{i:>2}. [{date_str}] ({category}) {text}")
            found_any = True

    if not found_any:
        print("Keine Einträge in diesem Zeitraum gefunden.")

    if skipped:
        print(f"(Hinweis: {skipped} Zeile(n) übersprungen – Format unerwartet.)")


def main():
    print("✅ Logbuch gestartet.")

    while True:
        show_menu()
        choice = input("Auswahl: ").strip()

        if choice == "1":
            add_entry()
        elif choice == "2":
            list_entries()
        elif choice == "3":
            search_entries()
        elif choice == "4":
            show_stats()
        elif choice == "5":
          list_last_days(7)
        elif choice == "6":
         list_entries_between()
        elif choice == "0":
          print("👋 Tschüss!")
          break
    else:
         print("❌ Ungültige Auswahl.")

if __name__ == "__main__":
    main()

