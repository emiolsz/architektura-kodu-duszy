"""Testy metod analizy wibracji przejścia. Uruchom: python -m unittest discover -s tests"""
import datetime
import unittest

from app import (
    analiza_wibracji_przejscia,
    generuj_profil_urodzenia,
)


class TestAnalizaWibracjiPrzejscia(unittest.TestCase):
    def test_metoda1_zero_gdy_wibracje_dat_sa_rowne(self):
        wynik = analiza_wibracji_przejscia(
            datetime.date(1970, 5, 12), datetime.date(2016, 8, 24)
        )
        self.assertEqual(wynik["wibracja_urodzenia"], 7)
        self.assertEqual(wynik["wibracja_smierci"], 5)
        self.assertEqual(wynik["roznica"], 2)
        self.assertFalse(wynik["metoda1_zero"])

    def test_metoda2_zero_dla_warunku_9_9(self):
        wynik = analiza_wibracji_przejscia(
            datetime.date(1980, 9, 27), datetime.date(2016, 9, 27)
        )
        self.assertEqual(wynik["rok_osobisty"], 9)
        self.assertEqual(wynik["wibracja_dnia_miesiaca_smierci"], 9)
        self.assertTrue(wynik["metoda2_zero"])
        self.assertEqual(wynik["metoda2_wynik"], 0)
        self.assertTrue(wynik["gmar_tikkun"])

    def test_metoda2_nie_zwroci_zera_bez_9_9(self):
        wynik = analiza_wibracji_przejscia(
            datetime.date(1970, 5, 12), datetime.date(2016, 8, 24)
        )
        self.assertFalse(wynik["metoda2_zero"])
        self.assertIsNone(wynik["metoda2_wynik"])

    def test_brak_analizy_gdy_smierc_przed_urodzeniem(self):
        self.assertIsNone(analiza_wibracji_przejscia(
            datetime.date(2016, 8, 24), datetime.date(1970, 5, 12)
        ))

    def test_profil_emilii_zgodny_z_pierwotna_metodyka(self):
        profil = generuj_profil_urodzenia(6, 11, 1974)
        self.assertEqual(profil, {
            "Prawa": 6,
            "Lewa": 11,
            "Gleboka": 21,
            "Talent": 3,
            "Wezel": 10,
            "Tikkun": 4,
        })

    def test_talent_nie_jest_hardkodowany_dla_jednej_daty(self):
        profil_emilii = generuj_profil_urodzenia(6, 11, 1974)
        profil_innej_osoby = generuj_profil_urodzenia(7, 4, 1985)
        self.assertEqual(profil_emilii["Talent"], 3)
        self.assertNotEqual(profil_innej_osoby, profil_emilii)
        self.assertEqual(
            profil_innej_osoby["Talent"],
            sum(int(c) for c in str(profil_innej_osoby["Gleboka"]))
        )

    def test_profil_urodzenia_jest_niezalezny_od_analizy_przejscia(self):
        profil = generuj_profil_urodzenia(6, 11, 1974)
        self.assertEqual(profil["Gleboka"], 21)
        self.assertEqual(profil["Talent"], 3)
        self.assertEqual(profil["Wezel"], 10)
        self.assertEqual(profil["Tikkun"], 4)


if __name__ == "__main__":
    unittest.main()
