# ASSET_LISTA – mitä koodi lataa (v2)

Koodi: `/workspace/peli/koodi/` (Koodaribotti). Polut suhteessa kansioon `/workspace/peli/`.
Kaikki PNG läpinäkyvällä taustalla, piirretään ilman pehmennystä. Puuttuva kuva/ääni ei kaada peliä (placeholder tai hiljaisuus).
Mittakaava: **32 px = 1 ruutu** (tiles.json 64x64 → kartta 2048x2048).

## Kartta
| Tiedosto | Koko | Käyttö |
|---|---|---|
| `grafiikka/kartta/kartta_tausta.png` | 2048x2048 | koko kentän tausta (jos puuttuu → maastolaatat `grafiikka/maasto/NN_*.png`) |
| `grafiikka/kartta/minikartta_256.png` | 256x256 | minikartta (skaalataan 192 px) |

## Yksiköt ja ajoneuvot (`<vari>` = sininen | punainen, katsovat oikealle, ankkuri (0.5, 0.875))
Yksikkönimet (= game.js `UNIT_TYPES`-avaimet): tolkkijussi, lahiojermu, mopopoika, grillimestari, parvekeampuja (vain sininen puoli), mummo (sininen), isa_trimmeri (punainen), volvo (punainen), dnepr, monkija, lada.
| Tiedosto | Kehys | Milloin |
|---|---|---|
| `grafiikka/yksikot/<nimi>_<vari>.png` | 32x32 | paikallaan |
| `grafiikka/yksikot/<nimi>_<vari>_kavely.png` | 4 × 32x32 | liikkuu |
| `grafiikka/yksikot/<nimi>_<vari>_ampuu.png` | 2 × 32x32 | 0,25 s jokaisen laukauksen/iskun jälkeen (aseelliset) |
| `grafiikka/yksikot/<nimi>_<vari>_sammunut.png` | 32x32 | sammunut |
| `grafiikka/ajoneuvot/<nimi>_<vari>.png`, `_kavely.png` (4 kehystä), `_ampuu.png` (dnepr, monkija) | 48x32 | kuten yllä |
| `grafiikka/ajoneuvot/poliisiauto.png`, `poliisiauto_kavely.png` | 48x32 | poliisipartio-tapahtuma |
| `grafiikka/ikonit/ui_<nimi>.png` / `ui_<nimi>_punainen.png` | 24x24 | koulutusnapit |

## Rakennukset (64x64 = 2x2 ruutua)
`grafiikka/rakennukset/paamaja_{sininen,punainen}.png`, `kmarket.png`, `baari.png`, `pizzatehdas.png`, `karkkikaivos.png`, `laakintaasema.png`, `tiedustelukeskus.png`, `kahvilahde.png`, `perunapelto.png`, `huoltovarikko.png`, `romutarvikevarasto.png`, `polttoainevarasto.png`, `kaasuvarasto.png`, `lihapullalinnake.png`, `alko.png` (Alkon ale -tapahtuma).

## Efektit (`grafiikka/efektit/`)
| Tiedosto | Käyttö |
|---|---|
| `suuliekki_8.png` | laukaus (piippu) |
| `makkara_8.png` | grillin ja parvekeampujan ammus (kaari) |
| `molotovi_16.png` | lentävä molotovi (pyörii) |
| `tuli_32.png` (4 kehystä) | palava molotovialue |
| `rajahdys_64.png` (6 kehystä) | parvekeampujan osuma (pieni), ajoneuvo tuhoutuu |
| `sade_64.png` | sadekuuro-overlay (tiilitetään) |
| `kary_32.png` | grillin käry osumassa, hidastettu yksikkö |
| `kirppis_tolkkikasa_32.png` | tölkkikasat ≥ 10 tölkkiä (pihakirppis) |
| `sauna_32.png` | saunailta: päämajan vieressä |
| `kesajuhlat_32.png` | kesäjuhlat: päämajojen vieressä |
| `laatta_latta_{1,2,3}.png` (96x96) + `laatta_hoyry.png` (4 kehystä) | laattalättä (vaihe haihtumisen mukaan) |

## UI (`grafiikka/ui/`, `grafiikka/ikonit/`)
`ui/tapahtuma_banneri.png` (480x96), `ui/tapahtuma_karttamerkki.png` (4 × 16x16), `ui/puoli_{sininen,punainen,molemmat}.png`, `ikonit/tapahtuma_<avain>.png` (32x32), `ikonit/tolkki_16.png`.
Tapahtuma-avaimet: poliisipartio, alkon_alennus, sadekuuro, panttiautomaatti_rikki, pihakirppis, saunailta, taloyhtion_kokous, bussi3_myohassa, kesajuhlat.

## Äänet (`aanet/<nimi>.ogg`, varalla `.mp3`)
- Musiikki: soittolista `musiikki_taistelu`, `musiikki_piiritys`, `musiikki_kannirynnakko` (satunnainen, ei samaa kahdesti peräkkäin), aulassa `musiikki_valikko`. Oletusvoimakkuus 0.4, säädin paneelissa.
- Aseet: `sfx_laukaus_rk62`, `_jatimatic`, `_emma`, `_suomikp`, `sfx_puukko` (puukko ja mummon rollaattori), `sfx_parveke_ampuu`, `sfx_trimmeri`, `sfx_grilli_ampuu`, `sfx_molotovi`, `sfx_molotovi_sammuu`.
- Liikekäsky: `sfx_mopo`, `sfx_dnepr`, `sfx_volvo`, `sfx_monkija`, `sfx_lada`, `sfx_rollaattori`. Volvon jyräys `sfx_ajoneuvo_tormays`.
- Muut: `sfx_tolkki_kilina`, `sfx_valtaus_valmis`/`_menetetty`, `sfx_rakennus_tuhoutui` (myös ajoneuvo tuhoutuu), `sfx_kuolema`, `sfx_sammui`, `sfx_koulutus_valmis`, `sfx_ui_klikkaus`.
- Tapahtumat: `sfx_tapahtuma_varoitus` (5 s ennen), `sfx_tapahtuma_jingle` + `aani_tapahtuma_<avain>`, `sfx_tapahtuma_loppui`, `sfx_poliisi_sireeni`, `sfx_sade_loop`.
- Humalakuplat: `sfx_kippis_kilistys`, `sfx_hikka_1..3`, `sfx_yokkays_1..2`, `sfx_laatta_latsahdys`, `sfx_laatta_karpaset_loop` (0.2), `aani_kanni_{kippis,yks_viela,hik,laatta_1,laatta_2,ups_sori,baariin,kotiin}`.
- Repliikit `aani_<yksikkö>_{valittu,kuittaus_N,hyokkays,baariin}` (+ `aani_lahiojermu_kanni`).
