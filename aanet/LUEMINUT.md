# Lähiösota – äänet (raakaversio)

Kaikki äänet on generoitu itse skriptillä `generoi_aanet.py` (numpy-synteesi + espeak-ng-puhe), ei ulkopuolisia sampleja. Vapaasti käytettävissä projektissa. Uudelleengenerointi: `/workspace/peli/venv/bin/python generoi_aanet.py` (vaatii ffmpeg + espeak-ng).

Jokainen ääni on sekä `.ogg` että `.mp3` -muodossa (Phaser: `this.load.audio(key, ['x.ogg','x.mp3'])`).

## Musiikki
- `musiikki_taistelu` – industrial-rock, 112 BPM, 48 tahtia ≈ 1:43, saumaton loop (`loop: true`). Suositus volume 0.4–0.5.

## Efektit
| tiedosto | käyttö |
|---|---|
| `sfx_tolkki_kilina` | tölkin poiminta / palautus K-Marketiin |
| `sfx_laukaus_rk62` | Lähiöjermun Pystykorva, yksi laukaus |
| `sfx_laukaus_jatimatic` | Jatimatic-sarja (4 laukausta) |
| `sfx_valtaus_valmis` | rakennuksen valtaus onnistui |
| `sfx_valtaus_menetetty` | vihollinen valtasi oman rakennuksen |
| `sfx_rakennus_tuhoutui` | päämaja / rakennus tuhoutuu |
| `sfx_mopo` | Mopopojan liikkeellelähtö |
| `sfx_ui_klikkaus` | UI-napit |

## Yksiköiden repliikit (`aani_<yksikkö>_<avain>`)
- tolkkijussi: `valittu` ("No mitä nyt?"), `kuittaus_1` ("Selvä pomo!"), `kuittaus_2` ("Tölkit talteen."), `kuittaus_3` ("Joo joo, mennään.")
- lahiojermu: `valittu` ("Häh? Mitä?"), `kuittaus_1` ("Selvä pomo!"), `kuittaus_2` ("Mennään!"), `hyokkays` ("Turpaan!"), `kanni` ("Mää lähen kotiin...", kun kännimittari on täynnä)
- mopopoika: `valittu` ("Mitä?"), `kuittaus_1` ("Kaasu pohjaan!"), `kuittaus_2` ("Mopolla mennään!"), `hyokkays` ("Ne on meidän tölkit!")

Valinta: `valittu`; liikekäsky: satunnainen `kuittaus_*`; hyökkäyskäsky: `hyokkays` (Jussilla `kuittaus_1`).
Huom: puheet ovat robottimaista syntetisaattoria radiopuhelinsuodatuksella – placeholder, kunnes Roope haluaa oikeat ääninäyttelijät.

## Lisäykset (ASSET_LISTAn toiveet)
- `sfx_sammui` – kaatuminen + kuorsaus (~3 s)
- `sfx_kuolema` – yksikkö kuolee
- `sfx_koulutus_valmis` – yksikkö valmistui
- `aani_<yksikkö>_baariin` – tolkkijussi "Mää käyn yhellä...", lahiojermu "Mää käyn yhellä... tai kahella.", mopopoika "Pikaset kaljat!"
