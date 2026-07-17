"""Testy generatora sekcji anty-slop. Uruchom: python3 -m unittest discover -s tools -v"""
import unittest

from gen_anty_slop import (
    NieznanaKategoria,
    generuj_markdown,
    kategorie_dla_jezyka,
)

REGULY_TESTOWE = [
    {"id": "PL-RHET", "lang": "pl", "klasa": "block", "pattern": "x", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "y", "opis": "nieważne"},
    {"id": "PL-SIGN", "lang": "pl", "klasa": "review", "pattern": "z", "opis": "duplikat id"},
    {"id": "EN-TRIAD", "lang": "en", "klasa": "review", "pattern": "w", "opis": "nieważne"},
]


class TestKategorieDlaJezyka(unittest.TestCase):
    def test_filtruje_po_jezyku(self):
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "pl"), ["PL-RHET", "PL-SIGN"])
        self.assertEqual(kategorie_dla_jezyka(REGULY_TESTOWE, "en"), ["EN-TRIAD"])

    def test_deduplikuje_powtorzone_id(self):
        # PL-SIGN wystepuje dwukrotnie w rules.json (jeden id grupuje wiele wzorcow)
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
        # PL-RHET ma klase block -> sekcja twarda; PL-SIGN review -> sekcja przegladu
        twarde, przeglad = wynik.split("## Do świadomej decyzji")
        self.assertIn("To nie X — to Y", twarde)
        self.assertNotIn("To nie X — to Y", przeglad)

    def test_naglowek_ostrzega_ze_plik_jest_generowany(self):
        self.assertIn("GENEROWANY", generuj_markdown(REGULY_TESTOWE, "pl"))

    def test_nieznana_kategoria_wywala_sie_glosno(self):
        reguly = [{"id": "PL-NOWE", "lang": "pl", "klasa": "review", "pattern": "a", "opis": ""}]
        with self.assertRaises(NieznanaKategoria) as ctx:
            generuj_markdown(reguly, "pl")
        self.assertIn("PL-NOWE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
