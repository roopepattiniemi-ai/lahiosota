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

## V2 (generoi_aanet_v2.py)
Efektit:
| tiedosto | käyttö |
|---|---|
| `sfx_dnepr`, `sfx_volvo`, `sfx_monkija`, `sfx_lada` | ajoneuvo lähtee liikkeelle (käskyääni, ~2 s) |
| `sfx_dnepr_loop`, `sfx_volvo_loop` | moottori käy, `loop: true` (3 s) |
| `sfx_ajoneuvo_tormays` | Volvo jyrää / ajoneuvo osuu |
| `sfx_laukaus_emma` | Emma-sarja (Dnepr, Grillimestari) |
| `sfx_laukaus_suomikp` | Suomi-konepistooli, sarja |
| `sfx_puukko` | puukon viuhahdus + isku |
| `sfx_molotovi` | heitto, lasin särkyminen, liekin humahdus |
| `sfx_molotovi_sammuu` | molotovi sateessa: sihahdus, ei syty |
| `sfx_parveke_ampuu` | parvekeampujan laukaus + vihellys + osuma (~2 s) |
| `sfx_trimmeri` | isän trimmeri hyökkää |
| `sfx_grilli_kary` / `sfx_grilli_ampuu` | grillin sihinä / makkaran sylkäisy |
| `sfx_rollaattori` | mummon liike |
| `sfx_poliisi_sireeni` | poliisipartio-tapahtuma (~3 s) |
| `sfx_sade_loop` | sadekuuro, `loop: true` (7,5 s) |
| `sfx_tapahtuma_jingle` | soi ennen jokaista tapahtumailmoitusta |

Repliikit `aani_<yksikkö>_<avain>`, avaimet `valittu`, `kuittaus_1`, `kuittaus_2`, `hyokkays`, `baariin`:
- `parvekeampuja`, `mummo`, `isa_trimmeri`, `grillimestari`: kaikki viisi avainta
- `volvo`: valittu, kuittaus_1, kuittaus_2, hyokkays
- `dnepr`: valittu, kuittaus_1, hyokkays
- `monkija`, `lada`: valittu, kuittaus_1

Tapahtumakuulutukset `aani_tapahtuma_<nimi>` (soita jinglen jälkeen):
poliisipartio, alkon_alennus, sadekuuro, panttiautomaatti_rikki, pihakirppis, saunailta, taloyhtion_kokous, bussi3_myohassa, kesajuhlat

## Kännitilat (generoi_aanet_kanni.py)
- `sfx_hikka_1..3` – hikka (satunnainen), kuplaan "Hik!"
- `sfx_yokkays_1`, `sfx_yokkays_2` – yökkäys + loiskahdus, kuplaan "Nyt lentää laatta!"
- `sfx_kippis_kilistys` – tuoppien kilistys buustissa, kuplaan "Kippis!"
- Yhteiset humalarepliikit, joita voi käyttää millä tahansa jalkaväellä kuplan kanssa: `aani_kanni_` + `laatta_1`, `laatta_2`, `yks_viela`, `ups_sori`, `kippis`, `baariin`, `hik`, `kotiin`
- Sammuminen: vanha `sfx_sammui` (kuorsaus) "Zzz..."-kuplaan
Suositus: soita repliikki korkeintaan 1/yksikkö/8 s ja vain näkyvissä oleville omille yksiköille, ettei äänimatto täyty.
- `sfx_laatta_latsahdys` – laattalätän syntyminen (soita yökkäyksen perään tai sen sijaan)
- `sfx_laatta_karpaset_loop` – hiljainen kärpästen pörinä + kupliminen lätän päälle, `loop: true`, volume ~0.2, vain kun lättä näkyy

## Tapahtumailmoitukset (generoi_aanet_tapahtumat.py)
Järjestys: `sfx_tapahtuma_varoitus` (5 s ennakkovaroitus) → `sfx_tapahtuma_jingle` + banneri → `aani_tapahtuma_<nimi>` (kuulutus heti jinglen perään, ~1,9 s) → … → `sfx_tapahtuma_loppui` kun tapahtuma päättyy.

## Lisämusiikit (generoi_musiikki.py)
Kaikki saumattomia looppeja (`loop: true`), suositus volume 0.4–0.5.
- `musiikki_piiritys` – raskas, 95 BPM, marssivirveli + matala D-riffi, ~1:41
- `musiikki_kannirynnakko` – 130 BPM, vuorottelee umpa-pa-polkkaa harmonikalla ja särörokkia, ~1:58
- `musiikki_valikko` – tumma valikkoteema, 80 BPM, ~0:48
Pelin soittolista: `musiikki_taistelu`, `musiikki_piiritys`, `musiikki_kannirynnakko` (satunnainen, ei samaa kahdesti peräkkäin). Valikossa `musiikki_valikko`.

## V3: olennot (generoi_aanet_olennot.py)
Vesihiisi:
- `sfx_vesihiisi_ennakko` (4 s) + `sfx_vesihiisi_kuplat` tai `sfx_vesihiisi_kuplat_loop` – ennakkovaroitus kuplien kanssa ennen nousua
- `sfx_vesihiisi_sihina_1..3` – Roopen toivoma sihinä, satunnainen (nousun jälkeen / hyökätessä / ennen sukellusta)
- `sfx_vesihiisi_nousu` (iso loiske), `sfx_vesihiisi_hyokkays`, `sfx_vesihiisi_sukellus`
- huudot: `aani_vesihiisi_tulkaa` ("Tulkaa veteen..."), `aani_vesihiisi_syvyyksiin` ("Syvyyksiin!"), `aani_vesihiisi_sss`
Peikko:
- `sfx_peikko_murina_1..3` (vaeltaa / huomaa yksikön), `sfx_peikko_karjunta_1..2` (hyökkäys, pelotus)
- `sfx_peikko_kivi_heitto` + `sfx_peikko_kivi_osuma`, `sfx_peikko_askel`, `sfx_peikko_kaatuu`
- huudot: `aani_peikko_` + `mun_metsa`, `tolkit` (varastaa kuorman), `pois` (pelotus), `nalka`
Tapahtumat: `aani_tapahtuma_peikot`, `aani_tapahtuma_vesihiisi` (jinglen jälkeen kuten muut).
