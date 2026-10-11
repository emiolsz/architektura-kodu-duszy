# app.py - Silnik Soul Decoder: profil urodzenia i osobna analiza wibracji przejścia
import datetime
from flask import Flask, request, render_template

from dane import KABALA_DICTIONARY
from analiza_opisowa import pobierz_analize_premium
from generator_pdf import wybuduj_archiwalny_pdf

app = Flask(__name__, template_folder='.')

def redukuj_do_22(liczba):
    if liczba == 0: return 22
    while isinstance(liczba, int) and liczba > 22:
        liczba = sum(int(c) for c in str(liczba))
    return liczba

def generuj_profil_urodzenia(d, m, r):
    """Profil urodzenia według pierwotnej metodyki 22 energii.

    Dzień = Dar, miesiąc = Karma, suma cyfr roku (redukcja tylko gdy >22)
    = Głęboka Osobowość. Talent powstaje z sumy cyfr Głębokiej Osobowości.
    Węzeł oporu wyznaczamy od najwyższej wartości bazowej, odejmując miesiąc;
    Tikkun wyznaczamy z różnicy między Węzłem Oporu a dniem.
    Ta funkcja jest niezależna od analizy wibracji przejścia.
    """
    prawa = redukuj_do_22(d)
    lewa = redukuj_do_22(m)

    # Rok: sumujemy cyfry; jeśli wynik przekracza 22, redukujemy do zakresu 1–22.
    gleboka = redukuj_do_22(sum(int(c) for c in str(r)))

    # Talent/Dar: sumujemy cyfry Głębokiej Osobowości (np. 21 -> 2+1 = 3).
    talent = sum(int(c) for c in str(gleboka))

    # Bierzemy najwyższą z trzech wartości bazowych, następnie odejmujemy miesiąc.
    najwyzsza = max(prawa, lewa, gleboka)
    wezel = redukuj_do_22(najwyzsza - lewa)

    # Tikkun: różnica Węzła Oporu i wartości dnia.
    # Wartość bezwzględna zachowuje wynik w zakresie obsługiwanym przez system 1–22.
    tikkun = redukuj_do_22(abs(wezel - prawa))

    return {
        "Prawa": prawa,
        "Lewa": lewa,
        "Gleboka": gleboka,
        "Talent": talent,
        "Wezel": wezel,
        "Tikkun": tikkun,
    }

def generuj_profil_smierci(d, m, r):
    return {"Transformacja": redukuj_do_22(sum(int(c) for c in f"{d}{m}{r}")), "Fizyczny": redukuj_do_22(d), "Emocjonalny": redukuj_do_22(m), "Duchowy": redukuj_do_22(r)}


def redukuj_do_9(liczba):
    """Redukcja numerologiczna do 1–9; używana wyłącznie w analizie wibracji przejścia."""
    liczba = abs(int(liczba))
    while liczba > 9:
        liczba = sum(int(c) for c in str(liczba))
    return liczba


def wibracja_dat(rok, miesiac, dzien):
    """Wibracja pełnej daty jako suma wszystkich jej cyfr z redukcją do 1–9."""
    return redukuj_do_9(sum(int(c) for c in f"{dzien:02d}{miesiac:02d}{rok:04d}"))


def analiza_wibracji_przejscia(data_urodzenia, data_smierci):
    """Dwie odrębne, symboliczne metody analizy wibracji przejścia.

    Interpretacje są opisowe i metaforyczne. Nie stanowią dowodu na stan duszy,
    istnienie karmicznego długu ani wpływ na los potomków.
    """
    if not data_urodzenia or not data_smierci or data_smierci < data_urodzenia:
        return None

    vib_ur = wibracja_dat(data_urodzenia.year, data_urodzenia.month, data_urodzenia.day)
    vib_sm = wibracja_dat(data_smierci.year, data_smierci.month, data_smierci.day)
    roznica = abs(vib_ur - vib_sm)

    rok_osobisty = redukuj_do_9(
        sum(int(c) for c in f"{data_urodzenia.day:02d}{data_urodzenia.month:02d}{data_smierci.year:04d}")
    )
    wibracja_dnia_miesiaca_smierci = redukuj_do_9(
        sum(int(c) for c in f"{data_smierci.day:02d}{data_smierci.month:02d}")
    )
    metoda2_spelniona = rok_osobisty == 9 and wibracja_dnia_miesiaca_smierci == 9

    archetypy = {
        1: ("Nowy Początek", "inicjacja, samodzielność, pierwszy krok i odwaga otwarcia drzwi"),
        2: ("Wrażliwość i Relacja", "spotkanie, współodczuwanie, intuicja i to, co łączy ludzi"),
        3: ("Kreacja", "twórczość, ekspresja, wzrost i nadawanie uczuciom formy"),
        4: ("Fundament", "struktura, odpowiedzialność, dom i budowanie trwałych ram"),
        5: ("Przemiana", "ruch, wolność, doświadczenie i przechodzenie przez zmianę"),
        6: ("Harmonia", "miłość, wybór, więź oraz godzenie przeciwieństw"),
        7: ("Mędrzec", "poszukiwanie sensu, wgląd, wiedza i wewnętrzna droga"),
        8: ("Sprawiedliwość i Równowaga", "odpowiedzialność, konsekwencje, wyrównywanie i porządkowanie spraw"),
        9: ("Dopełnienie", "domykanie rozdziałów, synteza doświadczeń, mądrość i uwalnianie tego, co zakończone"),
    }
    nazwa_ur, sens_ur = archetypy[vib_ur]
    nazwa_sm, sens_sm = archetypy[vib_sm]
    nazwa_roznicy, sens_roznicy = archetypy[roznica] if roznica in archetypy else ("Odmienny Rytm", "napięcie pomiędzy dwiema odmiennymi jakościami")

    opis_zero = (
        "Gmar Tikkun — Ostateczne Naprawienie. W języku tej metody zero nie oznacza pustki pozbawionej znaczenia, "
        "lecz symboliczne domknięcie rachunku: początek i moment odejścia spotykają się w tej samej wibracji, "
        "a różnica między nimi znika. Obrazowo można to odczytać jak weksel życia zwrócony z adnotacją „spłacono” — "
        "nie jako ocenę całego człowieka, lecz jako znak pełnego koła. W duchowym języku tej interpretacji pojawia się "
        "motyw czystej karty dla rodu oraz powrotu do Ain Soph, nieprzejawionego Źródła. To poetycka, symboliczna "
        "perspektywa metody, a nie sprawdzalny dowód na los duszy czy przyszłość potomków."
    )
    if roznica == 0:
        metoda1_wprowadzenie = (
            f"Droga rozpoczęła się pod znakiem {nazwa_ur} ({vib_ur}), a moment odejścia również niesie "
            f"wibrację {vib_sm} — {nazwa_sm}. Obie daty spotykają się w tej samej liczbie. "
            "W ramach przyjętej symboliki nie ma tu rozbieżności, którą trzeba byłoby opisać jako niedomknięcie."
        )
        metoda1_wniosek = "Wynik 0 — dopełnienie cyklu. " + opis_zero
    else:
        metoda1_wprowadzenie = (
            f"Droga narodzin niesie wibrację {vib_ur} — {nazwa_ur}, kojarzoną z {sens_ur}. "
            f"Moment odejścia przypada na wibrację {vib_sm} — {nazwa_sm}, której symboliczny język mówi o {sens_sm}. "
            "Te dwie jakości nie są identyczne; można je czytać jak początek i ostatni akord, które nie wybrzmiały "
            "w tej samej tonacji. Sama różnica nie przesądza jednak o winie, długu ani o obciążeniu pozostawionym rodzinie."
        )
        metoda1_wniosek = (
            f"Różnica wynosi {roznica} — {nazwa_roznicy}. W tej symbolicznej opowieści zwraca uwagę temat: {sens_roznicy}. "
            "Nie jest to wynik 0, dlatego metoda nie oznacza tego układu jako absolutnego wyzerowania cyklu. "
            "Można potraktować go jako zaproszenie do refleksji nad tym, co zostało przekazane, zapamiętane "
            "i jak żyjący nadają temu własne znaczenie."
        )

    if metoda2_spelniona:
        metoda2_wprowadzenie = (
            "W tej metodzie spotykają się dwie dziewiątki: rok osobisty osiąga wibrację 9, a dzień i miesiąc odejścia "
            "również redukują się do 9. Dziewiątka jest tu obrazem ostatniej strony księgi — porządkowania, "
            "zbierania doświadczeń i łagodnego zamykania rozdziału."
        )
        metoda2_wniosek = (
            "Warunek 9–9 został spełniony. W symbolice metody można nazwać to Portalem Dopełnienia: "
            "czas osobisty i data przejścia niosą ten sam motyw zakończenia, dlatego metoda przypisuje temu układowi "
            "wynik 0 i interpretację Gmar Tikkun. To duchowa metafora domknięcia, nie obiektywne orzeczenie o życiu "
            "zmarłego ani o losie jego bliskich. " + opis_zero
        )
    elif rok_osobisty == 9 and wibracja_dnia_miesiaca_smierci == 1:
        metoda2_wprowadzenie = (
            "Rok osobisty 9 przypomina ostatnią stronę księgi: czas podsumowań, porządkowania i pożegnania tego, "
            "co dobiegło końca. Tymczasem wibracja dnia i miesiąca odejścia wynosi 1 — symbol pierwszego kroku, "
            "inicjacji i otwarcia nowej przestrzeni. W tej konfiguracji obraz zamknięcia spotyka się z obrazem początku."
        )
        metoda2_wniosek = (
            "Portal 9–9 nie został spełniony, więc metoda nie przypisuje wyniku 0 ani interpretacji absolutnego "
            "wyzerowania. Można natomiast odczytać układ 9 i 1 jako symboliczną klamrę: domykający się rozdział "
            "oraz próg, za którym zaczyna się nieznane. To metafora przejścia, a nie twierdzenie o dosłownym "
            "rozpoczęciu nowej drogi w zaświatach."
        )
    else:
        nazwa_roku, sens_roku = archetypy[rok_osobisty]
        nazwa_dnia, sens_dnia = archetypy[wibracja_dnia_miesiaca_smierci]
        metoda2_wprowadzenie = (
            f"Rok osobisty w chwili odejścia wynosi {rok_osobisty} — {nazwa_roku}; jego symboliczny temat to {sens_roku}. "
            f"Wibracja dnia i miesiąca śmierci wynosi {wibracja_dnia_miesiaca_smierci} — {nazwa_dnia}, "
            f"czyli {sens_dnia}. Te dwie liczby opowiadają o odmiennych etapach i jakości przejścia."
        )
        metoda2_wniosek = (
            "Warunek 9–9 nie został spełniony, dlatego ta metoda nie przypisuje wyniku 0 ani etykiety Gmar Tikkun. "
            "Nie oznacza to automatycznie niedokończonej karmy czy negatywnego spadku dla rodu. W granicach tej "
            "symbolicznej interpretacji można przyjrzeć się relacji między tematem danego roku a jakością dnia odejścia, "
            "pozostawiając miejsce na osobistą pamięć i historię tej osoby."
        )

    return {
        "wibracja_urodzenia": vib_ur,
        "wibracja_smierci": vib_sm,
        "roznica": roznica,
        "metoda1_zero": roznica == 0,
        "metoda1_opis": opis_zero if roznica == 0 else "Różnica wibracji nie wynosi 0; warunek dopełnienia cyklu w tej metodzie nie został spełniony.",
        "metoda1_wprowadzenie": metoda1_wprowadzenie,
        "metoda1_wniosek": metoda1_wniosek,
        "archetyp_urodzenia": nazwa_ur,
        "archetyp_smierci": nazwa_sm,
        "archetyp_roznicy": nazwa_roznicy,
        "rok_osobisty": rok_osobisty,
        "wibracja_dnia_miesiaca_smierci": wibracja_dnia_miesiaca_smierci,
        "metoda2_zero": metoda2_spelniona,
        "metoda2_wynik": 0 if metoda2_spelniona else None,
        "metoda2_opis": opis_zero if metoda2_spelniona else "Warunek 9–9 nie został spełniony; metoda nie przypisuje wyniku 0.",
        "metoda2_wprowadzenie": metoda2_wprowadzenie,
        "metoda2_wniosek": metoda2_wniosek,
        "gmar_tikkun": roznica == 0 or metoda2_spelniona,
    }


def analizuj_synergie_rodowa(profil_a, nazwa_a, profil_b, nazwa_b, relacja_b):
    """Porównanie symbolicznych punktów dwóch profili; nie jest diagnozą ani dowodem dziedziczenia."""
    punkty = [
        ("Dar", "Prawa", "Zasoby i mocne strony"),
        ("Karma", "Lewa", "Wzorce do świadomej pracy"),
        ("Talent", "Talent", "Wspólna kreacja"),
        ("Głęboka osobowość", "Gleboka", "Wewnętrzny rdzeń"),
        ("Węzeł Oporu", "Wezel", "Możliwa wspólna blokada"),
        ("Tikkun", "Tikkun", "Lekcja i kierunek rozwoju"),
    ]
    wynik = {"a": nazwa_a or "Profil główny", "b": nazwa_b or relacja_b or "Osoba bliska", "relacja": relacja_b, "punkty": [], "alert_wezla": False, "misja": None, "dopelnienia": []}
    for etykieta, klucz, kontekst in punkty:
        a, b = profil_a.get(klucz), profil_b.get(klucz)
        if a is None or b is None:
            continue
        if a == b:
            interpretacja = f"Oba profile mają w punkcie {etykieta} tę samą wibrację {a}. W ujęciu symbolicznym może to być temat, który warto wspólnie omówić."
            typ = "wspólna wibracja"
        else:
            interpretacja = f"Profile w punkcie {etykieta} różnią się: {nazwa_a or 'Profil główny'} — {a}, {nazwa_b or relacja_b or 'osoba bliska'} — {b}. Można potraktować to jako odmienne perspektywy, które mogą się uzupełniać."
            typ = "różne wibracje"
        wynik["punkty"].append({"nazwa": etykieta, "a": a, "b": b, "typ": typ, "opis": interpretacja, "kontekst": kontekst})
    if profil_a.get("Wezel") == profil_b.get("Wezel"):
        wynik["alert_wezla"] = True
        n = profil_a.get("Wezel")
        wynik["alert_opis"] = f"WSPÓLNY WĘZEŁ RODOWY — oba profile mają Węzeł Oporu {n}. W tej symbolicznej interpretacji może to oznaczać podobny temat do przepracowania; nie przesądza o rzeczywistym dziedziczeniu wzorca."
    for osoba, dar, druga, cel in [(nazwa_a or "Profil główny", profil_a.get("Prawa"), nazwa_b or relacja_b or "osoba bliska", profil_b.get("Tikkun")), (nazwa_b or relacja_b or "osoba bliska", profil_b.get("Prawa"), nazwa_a or "Profil główny", profil_a.get("Tikkun"))]:
        if dar is not None and dar == cel:
            wynik["dopelnienia"].append(f"Dar {osoba} ({dar}) odpowiada liczbowo Tikkun osoby {druga} ({cel}); można zbadać, jak te tematy wzajemnie się inspirują.")
    suma = profil_a.get("Tikkun", 0) + profil_b.get("Tikkun", 0)
    wynik["misja"] = {"suma": suma, "wibracja": redukuj_do_22(suma), "opis": f"Symboliczna suma Tikkun wynosi {suma}, czyli wibrację wspólnej misji {redukuj_do_22(suma)}."}
    return wynik

@app.route("/", methods=["GET", "POST"])
def index():
    p1, posag1, przejscie1 = None, None, None
    aktywne_profile_wynik, mecze, synergie_rodowe, gilgul_zbieznosci = [], [], [], []
    
    imie1, data_ur1, data_sm1, status1 = "", "", "", "ZYJE"
    ile_osob = 1
    aktywne_role, aktywne_imiona, aktywne_ur, aktywne_sm = [], [], [], []
    
    if request.method == "POST":
        imie1 = request.form.get("imie1", "")
        data_ur1 = request.form.get("data_ur1", "")
        data_sm1 = request.form.get("data_sm1", "")
        status1 = request.form.get("status1", "ZYJE")
        
        try:
            ile_osob = max(1, min(10, int(request.form.get("ile_osob", 1))))
        except (ValueError, TypeError):
            ile_osob = 1
            
        for i in range(ile_osob):
            aktywne_role.append(request.form.get(f"p_rel_{i}", "Brat"))
            aktywne_imiona.append(request.form.get(f"p_imie_{i}", ""))
            aktywne_ur.append(request.form.get(f"p_ur_{i}", ""))
            aktywne_sm.append(request.form.get(f"p_sm_{i}", ""))
            
        if request.form.get("akcja_dekoduj") == "TAK":
            try:
                dt1 = datetime.datetime.strptime(data_ur1, "%Y-%m-%d") if data_ur1 else None
            except ValueError:
                dt1 = None
            if dt1:
                p1 = generuj_profil_urodzenia(dt1.day, dt1.month, dt1.year)
            if status1 == "TRANSGRESJA" and data_sm1:
                try:
                    dt_sm1 = datetime.datetime.strptime(data_sm1, "%Y-%m-%d")
                    posag1 = generuj_profil_smierci(dt_sm1.day, dt_sm1.month, dt_sm1.year)
                    if dt1:
                        przejscie1 = analiza_wibracji_przejscia(dt1.date(), dt_sm1.date())
                except ValueError:
                    posag1 = None
                
            for i in range(ile_osob):
                r_imie, r_rel, r_ur, r_sm = aktywne_imiona[i], aktywne_role[i], aktywne_ur[i], aktywne_sm[i]
                prof_u, pos_s = None, None
                if r_ur:
                    try:
                        dtX = datetime.datetime.strptime(r_ur, "%Y-%m-%d")
                        prof_u = generuj_profil_urodzenia(dtX.day, dtX.month, dtX.year)
                    except ValueError:
                        prof_u = None
                if r_sm:
                    try:
                        dt_sm = datetime.datetime.strptime(r_sm, "%Y-%m-%d")
                        pos_s = generuj_profil_smierci(dt_sm.day, dt_sm.month, dt_sm.year)
                    except ValueError:
                        pos_s = None
                if prof_u:
                    przejscie_osoby = None
                    if r_ur and r_sm:
                        try:
                            dt_ur_osoby = datetime.datetime.strptime(r_ur, "%Y-%m-%d").date()
                            dt_sm_osoby = datetime.datetime.strptime(r_sm, "%Y-%m-%d").date()
                            przejscie_osoby = analiza_wibracji_przejscia(dt_ur_osoby, dt_sm_osoby)
                        except ValueError:
                            przejscie_osoby = None
                    aktywne_profile_wynik.append({"imie": r_imie, "rel": r_rel, "prof": prof_u, "pos": pos_s, "przejscie": przejscie_osoby})
                    
            if p1 and aktywne_profile_wynik:
                for item in aktywne_profile_wynik:
                    n_wys = item["imie"] if item["imie"] else item["rel"]
                    if p1["Tikkun"] == item["prof"]["Tikkun"]:
                        mecze.append(f"✨ <b>Linia Przekazu Tikkun:</b> Posiadasz wspólny Tikkun ({p1['Tikkun']}) z: {n_wys} ({item['rel']}).")
                    if item["prof"]["Wezel"] == p1["Lewa"]:
                        mecze.append(f"⚠️ <b>Przejęty Wzorzec:</b> Węzeł Oporu osoby {n_wys} rezonuje jako Twoja Karma.")
                    if item["pos"] and p1["Talent"] == item["pos"]["Transformacja"]:
                        mecze.append(f"💎 <b>Aktywacja Zasobu:</b> Przejście osoby {n_wys} zasila Twój Talent ({p1['Talent']})!")
                if not mecze: mecze.append("💡 Linie energetyczne wykazują zrównoważoną ścieżkę.")
                for item in aktywne_profile_wynik:
                    synergie_rodowe.append(analizuj_synergie_rodowa(p1, imie1, item["prof"], item["imie"], item["rel"]))

                # Gilgul: moduł refleksji nad symboliczną zbieżnością dat przejścia i narodzin.
                # Nie stwierdza reinkarnacji; pokazuje wyłącznie daty do dalszej refleksji.
                osoby = [{"imie": imie1 or "Profil główny", "rel": "Profil główny", "ur": data_ur1, "sm": data_sm1}]
                osoby.extend({"imie": x["imie"] or x["rel"], "rel": x["rel"], "ur": aktywne_ur[j], "sm": aktywne_sm[j]} for j, x in enumerate(aktywne_profile_wynik))
                for zmarla in osoby:
                    if not zmarla.get("sm"):
                        continue
                    try:
                        data_przejscia = datetime.datetime.strptime(zmarla["sm"], "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        continue
                    for nowa_osoba in osoby:
                        if not nowa_osoba.get("ur") or nowa_osoba is zmarla:
                            continue
                        try:
                            data_narodzin = datetime.datetime.strptime(nowa_osoba["ur"], "%Y-%m-%d").date()
                        except (ValueError, TypeError):
                            continue
                        lata = data_narodzin.year - data_przejscia.year
                        if lata >= 0 and data_narodzin.month == data_przejscia.month and data_narodzin.day == data_przejscia.day:
                            gilgul_zbieznosci.append({"zmarla": zmarla["imie"], "rel_zmarlej": zmarla["rel"], "zyjaca": nowa_osoba["imie"], "rel_zyjacej": nowa_osoba["rel"], "lata": lata, "data": data_przejscia.strftime("%d.%m.%Y"), "opis": f"Data narodzin osoby {nowa_osoba['imie']} przypada w tę samą datę kalendarzową co rocznica przejścia osoby {zmarla['imie']} ({lata} lat różnicy). W podejściu inspirowanym pojęciem gilgul można potraktować to jako symboliczny temat do refleksji nad pamięcią i ciągłością rodu; sama zbieżność dat nie dowodzi wędrówki duszy."})

    return render_template("index.html", p1=p1, posag1=posag1, przejscie1=przejscie1, aktywne_profile_wynik=aktywne_profile_wynik, mecze=mecze, imie1=imie1, data_ur1=data_ur1, data_sm1=data_sm1, status1=status1, ile_osob=ile_osob, aktywne_role=aktywne_role, aktywne_imiona=aktywne_imiona, aktywne_ur=aktywne_ur, aktywne_sm=aktywne_sm, dict=KABALA_DICTIONARY, synergie_rodowe=synergie_rodowe, gilgul_zbieznosci=gilgul_zbieznosci)

@app.route("/pobierz-pdf", methods=["POST"])
def pobierz_pdf():
    typ = request.form.get("typ_wydruku")
    imie1, data_ur1 = request.form.get("d_imie1"), request.form.get("d_ur1")
    profil_glowny = None
    if data_ur1:
        try:
            dt = datetime.datetime.strptime(data_ur1, "%Y-%m-%d")
            profil_glowny = generuj_profil_urodzenia(dt.day, dt.month, dt.year)
        except ValueError:
            profil_glowny = None
    return wybuduj_archiwalny_pdf(typ, imie1, data_ur1, profil_glowny, request.form, generuj_profil_urodzenia, generuj_profil_smierci, analiza_wibracji_przejscia)

application = app

if __name__ == "__main__":
    app.run(debug=False)






