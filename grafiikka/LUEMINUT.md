# Grafiikka – raakaversio v0.1 (Grafiikkabotti)
Kaikki PNG, läpinäkyvä tausta (paitsi maastoruudut). Pikselitaide: skaalaa vain NEAREST/pixelArt: true.
Generaattori: `python3 generoi.py` (luo kaikki uudelleen).

- `maasto/NN_nimi.png` 32x32, NN = tiles.json terrain id (00 ruoho … 12 silta). Myös `maasto/maasto_tileset.png` (416x32, ruutu-id = x/32).
- `yksikot/{tolkkijussi,lahiojermu,mopopoika}_{sininen,punainen}.png` 32x32, yksi kuva per yksikkö (ei vielä animaatiota). Jalat/varjo ruudun alareunassa (ankkuri 0.5, 0.875).
- `rakennukset/paamaja_{sininen,punainen}.png`, `kmarket.png`, `baari.png` 64x64 = 2x2 ruutua, ankkuri alareuna (0.5, 1).
- `ikonit/tolkki_16.png`, `ikonit/tolkki_32.png`.
- `esikatselu.png` = kaikki kerralla suurennettuna.
Ei oikeita brändilogoja (K-Market = vihreä markiisi + tölkki-kyltti, baari = tuoppikyltti).

## Bonusrakennukset (v0.2)
`rakennukset/{pizzatehdas,karkkikaivos,laakintaasema,tiedustelukeskus,kahvilahde,perunapelto,huoltovarikko,romutarvikevarasto,polttoainevarasto,kaasuvarasto,lihapullalinnake}.png`
64x64, puolueeton ulkoasu, ankkuri kuten muissa rakennuksissa. Generaattori: `python3 bonusrakennukset.py`. Esikatselu: `esikatselu_bonus.png`.

## v2 – uudet yksiköt, ajoneuvot, animaatiot, efektit, tapahtumat, ikonit
Generaattori: `python3 generoi_v2.py` (importtaa apufunktiot `generoi.py`:stä, luo kaikki v2-tiedostot yhdellä ajolla,
ei muuta v0.1/v0.2-tiedostoja). Esikatselut 3x NEAREST: `esikatselu_v2_yksikot.png`, `esikatselu_v2_efektit.png`.
Spritesheetit ovat vaakarivejä, kehykset vasemmalta oikealle, kaikki kehykset samankokoisia. Yksiköt ja ajoneuvot katsovat OIKEALLE (koodi peilaa).
Tiimivärit: sininen #1f6fe0 (Multisilta), punainen #d8262b (Peltolammi). `<vari>` = `sininen` | `punainen`.

**Yksiköt** (`yksikot/`, kehys 32x32, ankkuri (0.5, 0.875)):
- Uudet staattiset: `{parvekeampuja,mummo,isa_trimmeri,grillimestari}_<vari>.png` 32x32 (= kävelyn kehys 0).
- Kävely kaikille 7: `{tolkkijussi,lahiojermu,mopopoika,parvekeampuja,mummo,isa_trimmeri,grillimestari}_<vari>_kavely.png` 128x32, 4 kehystä.
  Vanhoilla kolmella kehys 0 on pikselintarkasti sama kuin nykyinen staattinen kuva (generaattori tarkistaa assertilla).
- Hyökkäys: `{lahiojermu,mopopoika,parvekeampuja,mummo,isa_trimmeri,grillimestari}_<vari>_ampuu.png` 64x32, 2 kehystä
  (kehys 0 = laukaus/suuliekki, kehys 1 = rekyyli/savu; mummo: laukku ylhäällä -> isku, isä: trimmeri pyörii + silppua,
  grillimestari: k0 Emma ampuu, k1 grilli sylkee makkaran + käryä). Tölkkijussi on aseeton -> ei ampuu-kuvaa.
- Sammunut kaikille 7: `<nimi>_<vari>_sammunut.png` 32x32, makaa maassa pää oikealla, keltainen zzz mukana kuvassa.

**Ajoneuvot** (`ajoneuvot/`, kehys 48x32, ankkuri (0.5, 0.875), katsovat oikealle):
- `{dnepr,monkija,lada,volvo}_<vari>.png` 48x32 (= kävelyn kehys 0) ja `_<vari>_kavely.png` 192x32, 4 kehystä (renkaat pyörivät 45°/kehys, runko pomppii, pakokaasu).
- `{dnepr,monkija}_<vari>_ampuu.png` 96x32, 2 kehystä (Dnepr: Emma sivuvaunussa; Mönkijä: Suomi-KP). Lada/Volvo aseettomia -> ei ampuu-kuvaa.
- `poliisiauto.png` 48x32 (puolueeton, ei tunnuksia) + `poliisiauto_kavely.png` 192x32, 4 kehystä, valopalkki vuorottelee sininen/punainen.

**Efektit** (`efektit/`, ankkuri keskipiste ellei toisin mainita):
- `suuliekki_8.png` 8x8 (osoittaa oikealle, vasen reuna = piippu), `makkara_8.png` 8x8 (grillin ammus), `molotovi_16.png` 16x16 (pullo + palava rätti), `zzz_16.png` 16x16.
- `rajahdys_64.png` 384x64, 6 kehystä 64x64 (välähdys -> tulipallo -> savu).
- `tuli_32.png` 128x32, 4 kehystä 32x32, looppaa (ankkuri (0.5, 0.875), liekit maassa).
- `sade_64.png` 64x64, saumattomasti tiilittyvä läpinäkyvä sadeoverlay (piirrä ruudun päälle toistona).
- `kary_32.png` 32x32 puoliläpinäkyvä savupilvi.
- Tapahtumaobjektit kartalle 32x32 (ankkuri (0.5, 0.875)): `kirppis_tolkkikasa_32.png`, `sauna_32.png`, `kesajuhlat_32.png`.

**Tapahtumarakennukset** (`rakennukset/`): `alko.png` 64x64 (keksitty "VIINA"-kyltti, ei logoa; ankkuri kuten muissa rakennuksissa),
`bussi3.png` 64x32 (linjakilpi '3', katsoo oikealle, ankkuri (0.5, 0.875)).

**Ikonit** (`ikonit/`):
- Tapahtumat 32x32: `tapahtuma_{poliisipartio,alkon_ale,sadekuuro,automaatti_rikki,pihakirppis,saunailta,taloyhtion_kokous,bussi_myohassa,kesajuhlat}.png`.
  Aliakset (identtiset kopiot) koodin `TAPAHTUMAT`-avaimille: `tapahtuma_alkon_alennus.png`, `tapahtuma_panttiautomaatti_rikki.png`, `tapahtuma_bussi3_myohassa.png`.
- Koulutusnapit 24x24, läpinäkyvä tausta: `ui_<nimi>.png` (sininen) ja `ui_<nimi>_punainen.png`, nimi = tolkkijussi, lahiojermu, mopopoika,
  parvekeampuja, mummo, isa_trimmeri, grillimestari, dnepr, monkija, lada, volvo.

## Laattalättä (v2.1) – `python3 laatta.py`
- `efektit/laatta_latta_{1,2,3}.png` 96x96 (≈1,5 ruudun säde), keskiankkuri (0.5, 0.5). 1 = tuore, 2 = puoliksi haihtunut, 3 = melkein kuiva (myös alfa laskee).
- `efektit/laatta_latta_pieni_{1,2,3}.png` 64x64 (≈1 ruudun säde), samat vaiheet.
- `efektit/laatta_tiili_{1,2,3}.png` 32x32 saumattomasti tiilittyvä versio isommille alueille.
- `efektit/laatta_hoyry.png` 128x32, 4 kehystä: nouseva vihreä höyry + pörräävät kärpäset, piirretään lätän päälle loopissa (~4 fps).

## Tapahtumailmoitukset (UI) – `python3 ilmoitus.py`
- `ui/tapahtuma_banneri.png` 480x96 tumma, keltaiset varoitusraidat; vasemmalla 64x64 ikonipaikka kohdassa (14,18) (piirrä `ikonit/tapahtuma_<nimi>.png` 2x-skaalattuna), teksti alueelle x 90–470.
- `ui/tapahtuma_karttamerkki.png` 64x16, 4 kehystä sykkivä keltainen huutomerkkineula, ankkuri (0.5, 1) – kartalle tapahtumapaikkaan.
- `ui/puoli_{sininen,punainen,molemmat}.png` 16x16 lippu: kumpaa puolta tapahtuma koskee (banneriin, sivupaneeliin ja lokiin).
- Tapahtumaikonit 32x32 löytyvät jo: `ikonit/tapahtuma_<nimi>.png`.

## Kartan yhtenäinen taustakuva (v3)
Generaattori: `python3 generoi_kartta.py` (seedattu, SEED=1995, toistettava; ajoaika ~15 s). Pohja: `../kartta/pelikentta_v1_tiles.json`.
- `kartta/kartta_tausta.png` 2048x2048, mittakaava **32 px/ruutu**: ruutu (col,row) = pikselit (col*32, row*32)…(col*32+31, row*32+31). Piirretään kohtaan (0,0) ilman pehmennystä.
- `kartta/kartta_tausta_{rivi}_{sarake}.png` 16 palaa à 512x512 (rivi, sarake 0–3; pala (i,j) alkaa pikselistä (j*512, i*512) = ruudut col j*16…, row i*16…).
- `kartta/minikartta_256.png` 256x256 (8 px -> 1 px, ruutu = 4x4 px).
- `kartta/debug_ruudukko.png` tarkistuskuva: ruudukko + estemaasto (vesi, moottoritie, rakennus) punaisella, sillat vihreällä.
- Esikatselut: `kartta/esikatselu_kartta.png` (1024x1024) ja `kartta/esikatselu_kartta_lahikuva.png` (Lempääläntien pullonkaula col 28 row 33, 2x).
Tekniikka: maastoluokat pehmennetystä ruutumaskista + kohinalla rosoistettu raja + Bayer-dither-siirtymävyö; tiet ruutugraafista Chaikin-pyöristettyinä
viivoina (keskiviivat, reunakivet, tasoristeykset), rata ja Vt 3 jatkuvina polylinjoina (pölkyt, kiskot, kaistaviivat, keskikaide), sillat silta-ruuduille.
Kerrostalojen katot vain rakennus-ruuduilla, puut vain metsässä/puistoissa (eivät ulotu esteisiin tai teille), pikkudetaljit vain kuljettavilla alueilla.
Päämajoja, K-Marketeja ja bonusrakennuksia EI ole kuvassa (koodi piirtää spritet); niiden 2x2-ruudun alla on laatoitettu pihapohja.
Paletti kvantisoitu ≤64 väriin (PNG-palettikuva).
Karttadata © OpenStreetMap contributors (ODbL 1.0, https://www.openstreetmap.org/copyright) – attribuutio näytettävä pelissä.
