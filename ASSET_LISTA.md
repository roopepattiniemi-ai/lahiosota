# ASSET_LISTA – mitä koodi lataa (raakaversio)

Koodi: `/workspace/peli/koodi/` (Koodaribotti). Polut ovat suhteessa kansioon `/workspace/peli/`.
Kaikki PNG läpinäkyvällä taustalla, piirretään ilman pehmennystä (pixelated). Puuttuva kuva korvataan placeholderilla, peli ei kaadu.

## Grafiikka (ylhäältä viistoon, ei isometrinen) – kaikki jo olemassa ✅
| Tiedosto | Koko | Ankkuri | Käyttö |
|---|---|---|---|
| `grafiikka/maasto/NN_nimi.png` (00_ruoho … 12_silta) | 32x32 | vasen yläkulma | maastoruutu tiles.jsonin id:n mukaan |
| `grafiikka/yksikot/{tolkkijussi,lahiojermu,mopopoika}_{sininen,punainen}.png` | 32x32 | (0.5, 0.875) | yksikkö, katsoo oikealle (koodi peilaa vasemmalle) |
| `grafiikka/rakennukset/paamaja_{sininen,punainen}.png` | 64x64 | vasen yläkulma = 2x2 ruudun nurkka | päämajat |
| `grafiikka/rakennukset/kmarket.png` | 64x64 | sama | MAKKARA-VARASTO (K-Market) |
| `grafiikka/rakennukset/baari.png` | 64x64 | sama | KALJA-VARASTO (Pub Pättäri, Peltsun Saluuna) |
| `grafiikka/ikonit/tolkki_16.png` | 16x16 | keskipiste | tölkkikasa kartalla, kantava Jussi |

## Grafiikka – toivotaan seuraavaksi (nyt placeholder-laatikko nimellä)
Kaikki 64x64, sama ankkuri kuin rakennuksissa, puolueeton ulkoasu (omistajan väri piirretään koodissa reunukseksi):
`grafiikka/rakennukset/pizzatehdas.png`, `karkkikaivos.png` (R-Kioski), `laakintaasema.png` (apteekki), `tiedustelukeskus.png` (kirjasto), `kahvilahde.png` (Pupukahvila), `perunapelto.png`, `huoltovarikko.png`, `romutarvikevarasto.png` (Biltema), `polttoainevarasto.png` (St1), `kaasuvarasto.png` (Gasum), `lihapullalinnake.png` (IKEA).
Myöhemmin hyödyllisiä: yksiköiden kävely-/ampumisanimaatiot (spritesheet 32x32-kehyksin, vaakarivi), sammunut-asento, suuliekki 8x8, räjähdys 64x64 spritesheet, UI-ikonit 24x24 jokaiselle yksikölle koulutusnappeihin.

## Äänet – kaikki jo olemassa ✅ (`aanet/<nimi>.ogg`, varalla `.mp3`)
| Nimi | Milloin koodi soittaa |
|---|---|
| `musiikki_taistelu` | loopissa ensimmäisestä klikkauksesta, volume 0.4 (M = mute) |
| `sfx_tolkki_kilina` | oma Jussi poimii tölkin näkyvissä, pantit palautetaan |
| `sfx_laukaus_rk62` | Lähiöjermu ampuu (näkyvissä) |
| `sfx_laukaus_jatimatic` | Mopopoika ampuu (näkyvissä) |
| `sfx_valtaus_valmis` / `sfx_valtaus_menetetty` | oma valtaus onnistui / oma rakennus menetettiin |
| `sfx_rakennus_tuhoutui` | päämaja tuhoutuu |
| `sfx_mopo` | Mopopojalle annetaan käsky |
| `sfx_ui_klikkaus` | koulutusnapit |
| `aani_<yksikkö>_valittu` | valinta ja yksikkö valmistui |
| `aani_<yksikkö>_kuittaus_N` | liikekäsky (satunnainen N) |
| `aani_<yksikkö>_hyokkays` | hyökkäyskäsky (Jussilla `kuittaus_1`) |
| `aani_lahiojermu_kanni` | oma yksikkö lähtee kotiin täydessä kännissä |

Toivotaan seuraavaksi: `sfx_sammui` (kuorsaus/kaatuminen), `sfx_kuolema`, `aani_<yksikkö>_baariin` ("Mää käyn yhellä…"), `sfx_koulutus_valmis`.
