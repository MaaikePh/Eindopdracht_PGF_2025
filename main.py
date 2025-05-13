import requests
from pyairtable import Api
from prettytable import PrettyTable
from dotenv import load_dotenv
import os
from datetime import datetime

# access_token en base_id staan in de .env die los bijgeleverd zal worden.
# Airtable instellingen
load_dotenv()
access_token = os.getenv("AIRTABLE_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")
api = Api(access_token)
tabel_signaleringsplan = api.table(base_id, "Signaleringsplan")
tabel_checkins = api.table(base_id, "Check-ins")

def signaleringsplan_maken():
    print("\nJe hebt gekozen voor het maken van jouw signaleringsplan.")
    print("Laten we een signaal en actie voor een bepaalde fase aanmaken om aan je plan toe te voegen:\n")

    while True:
        fase = input("Voor welke fase wil je iets toevoegen? Groen, oranje of rood:\n").strip().lower()
        if fase in ["groen", "oranje", "rood"]:
            break
        else:
            print("\nVerkeerde waarde ingevoerd. Kies de kleur groen, oranje of rood:\n")

    while True:
        signaal = input(f"Wat voor signaal wil je toevoegen voor de fase {fase}:\n").lower()
        if signaal:
            break
        else:
            print("\nGeen antwoord gegeven. Vul een waarde in.\n")

    while True:
        actie = input(f"Wat voor actie helpt je voor deze fase {fase} en dit signaal {signaal}:\n").lower()
        if actie:
            break
        else:
            print("\nGeen antwoord gegeven. Vul een waarde in.\n")

    record = tabel_signaleringsplan.create({
        "Fase": fase,
        "Signalen": signaal,
        "Acties": actie
    })

    print(f"\nFase, signaal en actie zijn succesvol toegevoegd:")
    print(f"Fase: {record['fields']['Fase']}")
    print(f"Signaal: {record['fields']['Signalen']}")
    print(f"Actie: {record['fields']['Acties']}\n")

def signaleringsplan_bekijken():
    print("Je hebt gekozen voor het bekijken van jouw signaleringsplan.\n")
    records = tabel_signaleringsplan.all()
    pt = PrettyTable()
    pt.field_names = ["Fase", "Signalen", "Acties"]
    if not records:
        print("Geen signaleringsplan gevonden.")
    else:
        sorted_records = sorted(records, key=lambda record: record['fields'].get('Fase', 'z'), reverse=False)
        print("Hier is jouw signaleringsplan:\n")
        for r in sorted_records:
            velden = r["fields"]
            pt.add_row([
                velden.get("Fase", ""),
                velden.get("Signalen", ""),
                velden.get("Acties", "")
            ])
        print(pt)
        print("\n")

def engels_affirmations():
    url = "https://www.affirmations.dev/"
    try:
        antwoord = requests.get(url)
        antwoord.raise_for_status()
        data = antwoord.json()
        affirmation = data.get("affirmation")
        return affirmation
    except requests.exceptions.RequestException as e:
        return f"Er ging iets mis: {e}"

def registreer_fase(fase_kleur, boodschap):
    vandaag = datetime.now().replace(microsecond=0)
    vandaag_iso = vandaag.isoformat()
    record = tabel_checkins.create({
            "Datum": vandaag_iso,
            "Gekozen fase": [fase_kleur]
    })
    print(f"\nFase: {record['fields']['Gekozen fase'][0]}")
    print("Datum:", vandaag.strftime("%d-%m-%Y %H:%M"))
    print(f"{boodschap}\n")

def fase_check():
    print("\nJe hebt gekozen voor de fase check.")
    print("In welke fase voel jij je op dit moment?\n")
    while True:
        fase = input("Kies de kleur groen, oranje of rood:\n").strip().lower()
        if fase == "groen":
            registreer_fase("groen", "Goed bezig! Blijf zo doorgaan.\n")
            break
        elif fase == "oranje":
            registreer_fase("oranje", "Kijk uit, je wil nu niet te veel gaan doen. Informeer je signaleringsplan voor acties.\n")
            break
        elif fase == "rood":
            registreer_fase("rood", "Dat is een probleem. Kijk meteen in je signaleringsplan om je beter te voelen.\n")
            break
        else:
            print("\nVerkeerde waarde ingevoerd. Kies de kleur groen, oranje of rood:\n")

def check_in_keuze():
    while True:
        print("Maak een keuze tussen:\n"
                "1. Fase check\n"
                "2. Een Engelse Affirmatie om je dag beter te maken\n"
                "3. Terug naar hoofdmenu\n")
        keuze_input = input("Kies het getal van je keuze: \n")
        try:
            keuze = int(keuze_input)
        except ValueError:
            print("\nVerkeerde waarde ingevoerd. Kies het getal 1, 2 of 3 voor je keuze.\n")
            continue

        if keuze == 1:
            fase_check()
        elif keuze == 2:
            print("\nEngelse affirmatie van vandaag:")
            print(f"{engels_affirmations()}\n")
        elif keuze == 3:
            print("\nJe gaat terug naar het hoofdmenu.\n")
            break
        else:
            print("\nVerkeerde waarde ingevoerd. Kies het getal 1, 2 of 3 voor je keuze.\n")

def dagelijkse_check_in():
    print("\nJe hebt gekozen voor een dagelijkse Check-in.")
    print("Waar wil je mee beginnen vandaag?\n")
    check_in_keuze()

def logboek():
    print("\nJe hebt gekozen voor het bekijken van jouw logboek.\n")
    records = tabel_checkins.all()
    pt = PrettyTable()
    pt.field_names = ["Datum", "Gekozen fase"]
    if not records:
        print("Geen logboek gevonden.")
    else:
        sorted_records = sorted(records, key=lambda record: record['fields'].get('Datum', 'z'), reverse=False)
        print("Hier is jouw logboek:\n")
        for r in sorted_records:
            velden = r["fields"]
            datum_iso = velden.get("Datum", "")
            try:
                dt_obj = datetime.fromisoformat(datum_iso)
                datum_geformatteerd = dt_obj.strftime("%d-%m-%Y %H:%M")
            except (ValueError, TypeError):
                datum_geformatteerd = datum_iso
            fase = velden.get("Gekozen fase", [""])[0]
            pt.add_row([datum_geformatteerd, fase])
        print(pt)
        print("\n")

def main():
    print("\nWelkom bij de autisme signaleringsplan applicatie.\n")
    while True:
        print("Wat wil je doen vandaag?")
        print("Maak een keuze tussen:\n"
                "1. Signaleringsplan maken\n"
                "2. Signaleringsplan bekijken\n"
                "3. Dagelijkse check-in\n"
                "4. Logboek bekijken\n"
                "5. Afsluiten\n"
                )
        try:
            keuze = int(input("Kies het getal van je keuze: \n"))
            if keuze == 1:
                signaleringsplan_maken()
            elif keuze == 2:
                signaleringsplan_bekijken()
            elif keuze == 3:
                dagelijkse_check_in()
            elif keuze == 4:
                logboek()
            elif keuze == 5:
                print("\nBedankt, tot de volgende keer!\n")
                break
            else:
                print("\nVerkeerde waarde ingevoerd. Kies een getal tussen de 1 en 5 voor je keuze.\n")
        except ValueError:
            print("\nVerkeerde waarde ingevoerd. Kies een getal tussen de 1 en 5 voor je keuze.\n")

if __name__ == "__main__":
    main()