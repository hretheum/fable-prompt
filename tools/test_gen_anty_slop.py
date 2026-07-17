"""Testy generatora sekcji anty-slop. Uruchom: python3 -m unittest discover -s tools -v"""
import unittest

from gen_anty_slop import (
    ZAKAZY,
    NieznanaKategoria,
    generuj_markdown,
    kategorie_dla_jezyka,
    wytnij_ladunek,
)

REGULY_TESTOWE = [
    {"id": "PL-RHET", "lang": "pl", "klasa": "block", "pattern": "x", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "y", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "z", "opis": "duplikat id"},
    {"id": "EN-TRIAD", "lang": "en", "klasa": "review", "pattern": "w", "opis": "nieważne"},
]

POLSKIE_ZNAKI = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")


class TestKategorieDlaJezyka(unittest.TestCase):
    def test_filtruje_po_jezyku(self):
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "pl"), ["PL-RHET", "PL-SIGN"])
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "en"), ["EN-TRIAD"])

    def test_deduplikuje_powtorzone_id(self):
        # PL-SIGN występuje dwukrotnie w rules.json (jeden id grupuje wiele wzorców)
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "pl").count("PL-SIGN"), 1)

    def test_lang_both_trafia_do_obu_warstw(self):
        reguly = [{"id": "X-UNIV", "lang": "both", "klasa": "review", "pattern": "q", "opis": ""}]
        self.assertEqual(kategorie_dla_jezyka(reguly, "pl"), ["X-UNIV"])
        self.assertEqual(kategorie_dla_jezyka(reguly, "en"), ["X-UNIV"])


class TestGenerujMarkdown(unittest.TestCase):
    def test_rozdziela_zakazy_twarde_od_przegladu(self):
        wynik = generuj_markdown(REGULY_TESTOWE, "pl")
        self.assertIn("## Zakazy twarde", wynik)
        self.assertIn("## Do świadomej decyzji", wynik)
        # PL-RHET ma klasę block -> sekcja twarda; PL-SIGN review -> sekcja przeglądu
        twarde, przeglad = wynik.split("## Do świadomej decyzji")
        self.assertIn("To nie X — to Y", twarde)
        self.assertNotIn("To nie X — to Y", przeglad)

    def test_naglowek_ostrzega_ze_plik_jest_generowany(self):
        wynik = generuj_markdown(REGULY_TESTOWE, "pl")
        self.assertIn("GENEROWANY", wynik)
        # ...ale ostrzeżenie jest metadaną utrzymaniową: do promptu wjeżdża sam ładunek.
        self.assertNotIn("GENEROWANY", wytnij_ladunek(wynik))

    def test_nieznana_kategoria_wywala_sie_glosno(self):
        reguly = [{"id": "PL-NOWE", "lang": "pl", "klasa": "review", "pattern": "a", "opis": ""}]
        with self.assertRaises(NieznanaKategoria) as ctx:
            generuj_markdown(reguly, "pl")
        self.assertIn("PL-NOWE", str(ctx.exception))


class TestLadunek(unittest.TestCase):
    """Ładunek = jedyna część pliku, która wjeżdża do promptu dla Claude Design."""

    def test_ladunek_en_nie_zawiera_polskich_znakow(self):
        # To jest regresja, która wraca: rama pliku była jedną stałą po polsku dla obu wariantów,
        # więc anglojęzyczny użytkownik dostawał sekcję LANGUAGE w większości po polsku.
        # Bierzemy CAŁY katalog EN z prawdziwej tablicy ZAKAZY, nie próbkę.
        reguly_en = [
            {"id": k, "lang": "en", "klasa": "review", "pattern": "x", "opis": ""}
            for k in ZAKAZY
            if k.startswith("EN-")
        ]
        ladunek = wytnij_ladunek(generuj_markdown(reguly_en, "en"))

        znalezione = sorted(POLSKIE_ZNAKI.intersection(ladunek))
        self.assertEqual(
            znalezione,
            [],
            f"ładunek EN zawiera polskie znaki: {znalezione}. Rama pliku albo któryś zakaz "
            f"z ZAKAZY przeciekł z warstwy polskiej.",
        )

    def test_ladunek_en_ma_angielska_rame(self):
        ladunek = wytnij_ladunek(generuj_markdown(REGULY_TESTOWE, "en"))
        self.assertIn("## Hard bans", ladunek)
        self.assertIn("## Judgement call", ladunek)
        self.assertIn("the DS wins", ladunek)  # reguła pierwszeństwa DSa zostaje w ładunku
        self.assertNotIn("## Zakazy twarde", ladunek)

    def test_pusta_sekcja_twarda_mowi_w_jezyku_wariantu(self):
        # EN nie ma reguł klasy block (świadoma decyzja człowieka) — komunikat ma być po angielsku.
        ladunek = wytnij_ladunek(generuj_markdown(REGULY_TESTOWE, "en"))
        self.assertIn("_(none in this language layer)_", ladunek)

    def test_ladunek_nie_wozi_metadanych_utrzymaniowych(self):
        ladunek = wytnij_ladunek(generuj_markdown(REGULY_TESTOWE, "pl"))
        for metadana in ("nie edytuj ręcznie", "gen_anty_slop.py", "sztuczny-miodek"):
            self.assertNotIn(metadana, ladunek)

    def test_wytnij_ladunek_wywala_sie_na_pliku_bez_znacznikow(self):
        with self.assertRaises(ValueError):
            wytnij_ladunek("# Zwykły markdown bez znaczników")


if __name__ == "__main__":
    unittest.main()
