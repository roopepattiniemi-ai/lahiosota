# Lähiösota: Etelä-Tampere – v2 (koodi)

Selaimessa pelattava 1v1-reaaliaikastrategia. Palvelin (Node.js + WebSocket) pyörittää pelin ja on auktoriteetti; selain vain piirtää ja lähettää käskyt.

## Käynnistys paikallisesti
Tarvitaan Node.js 18 tai uudempi.

```
cd /workspace/peli/koodi
npm install
npm start
```

Avaa selaimessa http://localhost:3000. Portin voi vaihtaa: `PORT=8080 npm start`.

- **Luo uusi peli (1v1)**: saat linkin (`/?huone=xxxxxx`). Kaveri avaa saman linkin, ja peli alkaa kun molemmat ovat paikalla. Ensimmäinen on sininen (Multisilta), toinen punainen (Peltolammi).
- **Harjoittele yksin**: peli alkaa heti, vastustaja ei tee mitään (testaukseen).
- Samassa koneessa voi testata kahdella välilehdellä (toinen esim. incognito-ikkunassa).
- Jos yhteys katkeaa, saman linkin avaaminen samalla selaimella palauttaa sinut omalle puolellesi.

Kaverin kanssa netin yli: palvelimen pitää näkyä internetiin (esim. oma palvelin tai tunneli kuten ngrok/cloudflared). Hosting on vielä avoin kysymys (Roope/Pelimestari päättää).

## Ohjaus
- Vasen klikkaus / raahaus: valitse omia yksiköitä (Shift lisää). Klikkaus rakennukseen näyttää tiedot.
- Oikea klikkaus: liiku / kerää tölkkikasa (Tölkkijussi, Mopopoika) / hyökkää vihollisen yksikköön tai päämajaan / vie pantit omaan K-Marketiin.
- Oikea klikkaus minikarttaan = käsky sinne, vasen = kamera sinne.
- Nuolet tai WASD tai hiiri ruudun reunaan: kamera. Rulla: zoom (1x, 1,5x, 2x). Välilyönti: kamera omaan päämajaan.
- Koulutus: Z Tölkkijussi, X Lähiöjermu, C Mopopoika, B Grillimestari, T Parvekeampuja (Multisilta) / Isä trimmerin kanssa (Peltolammi), Y Mummo rollaattorilla (Multisilta) / Tuunattu Volvo (Peltolammi), F Dnepr, G Mönkijä, J Lada.
- V + klikkaus: molotovi (Lähiöjermu, Mopopoika, Isä). U: pura kyyti. Kyytiin: valitse jalkaväkeä ja oikea klikkaus omaan Volvoon tai Ladaan.
- H: seis. M: äänet päälle/pois. Paneelissa musiikin äänenvoimakkuus.
- Ctrl+1–9 tallentaa ryhmän, 1–9 valitsee sen.

## Säännöt raakaversiossa
- Aloitus: 250 €, 2 Tölkkijussia ja 2 Lähiöjermua. Päämaja 2500 HP.
- **Tölkit**: kasoja ympäri karttaa (uusia ilmestyy), kaatuneet pudottavat tölkkejä. Tölkkijussi kantaa 8, palauttaa omaan K-Marketiin (10 €/tölkki) ja palaa sitten keräämään automaattisesti. Jos omaa K-Marketia ei ole, päämaja ottaa tölkit puoleen hintaan.
- **Yksiköt**: Tölkkijussi 50 € (aseeton), Lähiöjermu 80 € (RK-62), Mopopoika 120 € (Jatimatic, nopea, voi kerätä 4 tölkkiä vaikka vihollisen pudottamia).
- **Kännimittari** (0–100) nousee itsestään, nopeasti oman baarin lähellä, laskee päämajan ja apteekin lähellä.
  - 20–60: pieni hiprakka, +25 % vahinko ja parempi tarkkuus.
  - 60–85: hitaampi ja epätarkempi.
  - 85+: satunnaisesti sammuu (8 s), lähtee kotiin (poistuu), lähtee baariin tai ampuu omiaan.
- **Valtaus**: seiso rakennuksen vieressä ilman vihollisia, 10 s (nopeampi kun useampi, max 3). Vihollisen läsnäolo pysäyttää valtauksen.
- **Bonukset**: K-Market = pantinpalautus, baari = +15 % vahinko lähellä (ja kännit), R-Kioski = +15 % nopeus, Pizzeria = hidas paraneminen, apteekki = parantaa ja selvittää, kahvila = sammuneet heräävät tuplanopeudella, viljelypalsta = +1 €/s, IKEA = puolet vähemmän vahinkoa lähellä. Muut (kirjasto, varikot, St1, Gasum) antavat raakaversiossa +0,5 €/s.
- **Voitto**: vihollisen päämaja tuhottu.

## V2: uudet yksiköt, aseet ja ajoneuvot
| Yksikkö | Puoli | Hinta | Ase / erityistä |
|---|---|---|---|
| Grillimestari | molemmat | 150 | pihagrilli: makkara + käry hidastaa, lähes paikallaan |
| Kerrostalon parvekeampuja | Multisilta | 180 | tykistö 9 ruutua, roiskevahinko, ampuu vain paikallaan, ei osu alle 2,5 ruudun |
| Mummo rollaattorilla | Multisilta | 220 | 500 HP, ottaa puolet vahingosta, ei juuri juo |
| Isä trimmerin kanssa | Peltolammi | 130 | lähitaistelu, kulkee metsässä kuin tiellä |
| Tuunattu Volvo | Peltolammi | 300 | kuljettaa 4, jyrää vihollisen jalkaväkeä |
| Dnepr-sivuvaunupyörä | molemmat | 260 | Emma-konekivääri sivuvaunussa |
| Mönkijä | molemmat | 160 | Suomi-KP, nopea maastossa, kerää 6 tölkkiä |
| Lada | molemmat | 120 | kuljettaa 3 |
- Puukko: Lähiöjermu ja Mopopoika vaihtavat puukkoon, kun vihollinen on vieressä.
- Molotovi: 15 € (puolet, jos St1 tai Gasum on omistuksessa), +8 kännit, palaa 5 s ja polttaa myös omia. Kännissä (60 %+) voi pudota omiin jalkoihin. Sateessa ei syty.
- Ajoneuvot ovat 25 % halvempia, jos Huoltovarikko tai Biltema on omistuksessa. Raskaat ajoneuvot ovat hitaita metsässä, suolla ja kalliolla.
- Humala: tilan noustessa yksikön päälle tulee puhekupla (enintään yksi kupla ja ääni yksikköä kohden 8 s välein, enintään 6 kerralla ruudulla). Kun jalkaväen kännit nousevat 85 %:iin, se oksentaa: laattalättä (säde 1,5 ruutua, 25 s) syö HP:ta 1,5/s, hidastaa kaikkia (myös omia) ja hidastaa tölkkien keräystä.

## Satunnaistapahtumat
Ensimmäinen noin 90 s kohdalla, sitten 60–110 s välein, 5 s ennakkovaroitus. Ilmoitus näkyy molemmille: banneri, jingle ja kuulutus, paneelissa ikoni ja laskuri, kartalla ja minikartalla paikka, kun tapahtumalla on sijainti.
Poliisipartio (humalaiset putkaan), Alkon alennusmyynti, Sadekuuro, Panttiautomaatti rikki, Pihakirppis, Saunailta (Peltolammi), Taloyhtiön kokous (Multisilta), Bussi 3 myöhässä, Kesäjuhlat (aselepo, tuplapantit).

## Testaus
- `node test/sim.js` ajaa pelilogiikan savutestit (koulutus, kyyti, molotovi, sade, kaikki tapahtumat, pitkä bottimatsi).
- Harjoitushuoneessa (`&harjoitus=1`) selaimen konsolissa toimii `__lahiosota.send({t:'debug', tap:'sadekuuro'})`, `{t:'debug', raha:1000}`, `{t:'debug', kanni:90}` ja `{t:'debug', spawn:'volvo'}`. Näillä ei voi vaikuttaa 1v1-peleihin.

## Mitä ei vielä ole
Sumu (fog of war), kartan räjähtävät rakennukset (St1/Gasum), tasapainotus.

## Tiedostot
- `server.js` – HTTP + WebSocket, huoneet linkeillä, 10 tickiä/s.
- `game.js` – koko pelilogiikka (A*-reitinhaku, talous, kännimittari, valtaus, taistelu).
- `public/` – selainasiakas (Canvas 2D, ei kirjastoja): `index.html`, `peli.js`, `tyyli.css`.
- Grafiikka luetaan kansiosta `../grafiikka/`, äänet `../aanet/`, kartta `../kartta/pelikentta_v1_tiles.json`.
- Odotetut assetit: `/workspace/peli/ASSET_LISTA.md`.

Karttadata © OpenStreetMap-tekijät (ODbL).

## V3: metsäpeikot ja vesihiisi
- Kartta: `kartta/pelikentta_v2_tiles.json` (maastotyyppi 13 = metsäpolku, move_cost 0.8).
- **Metsäpeikot** (puolueettomia, owner 3): ensimmäiset noin 2,5 min kohdalla ja sen jälkeen 70–120 s välein, enintään 3 kerrallaan, metsään vähintään 12 ruudun päähän päämajoista. Ne vaeltavat lähellä kotiaan, heittelevät kiviä, varastavat tölkkikuormia ja karjaisevat, jolloin lähellä olevat jalkaväet pakenevat. Jos peikkoon osuu, se suuttuu ampujalle. Kaatunut peikko pudottaa 6 tölkkiä ja kaikki varastamansa.
- **Vesihiisi**: noin 3,3 min kohdalla ja sen jälkeen 45–80 s välein valitsee lammen tai järven rantaruudun, jonka lähellä (≤ 3 ruutua) on joukkoja. Ensin 4 s kuplia, sihinää ja varoitus, sitten se nousee 14 sekunniksi, iskee kaikkia 3 ruudun säteellä ja sukeltaa. Ampua voi, lähitaistelijat eivät pääse veteen.
- Molemmista tulee banneri, karttamerkki ja puhekuplahuudot. Testaus harjoituksessa: `__lahiosota.send({t:'debug', olento:'peikot'})` tai `olento:'vesihiisi'`.

## V4 – kerrostalot, tapahtumarakennukset, lumimyrsky, NPC:t
- **Kerrostalot** (2–4 kpl kartan rakennusruuduista, ei kuvaa: omistajakehys + "Kerrostalo"): vallattava; omat jalkaväet oikealla klikkauksella sisään (max 6, eivät ole maalina), ampuvat talon keskeltä kantama +1,5. Infopaneelissa "Tyhjennä talo" (`{t:'tyhjenna', b}`). 4–5 sisällä: kotibileet → 10 s "Naapurit valittaa!" → 18 s häätö (k=95, hidastus 20 s). 6 sisällä: poliisipiiritys, 4 s → kaikki putkaan. Omistuksen vaihtuessa asukkaat heitetään ulos.
- **Sauna** (puolueeton): känni laskee nopeasti, HP palautuu, ei puolusta; yli 25 s → sammuu 15 s. Uusi käsky = lähtee.
- **Pihagrilli** (vallattava): omat 4 ruudun säteellä humaltuvat puolet hitaammin; 20 s välein `paljastus`-tapahtuma (vastustajalle vilkkuvat merkit).
- **Pullonkerääjämummo** (owner 0): kerää tölkkikasoja. Oikea klikkaus häneen tölkkejä kantavilla = lahjonta 60 s, jonka aikana hänen keräämänsä kasat ovat lahjojan rahaa.
- **Kirpputori** (puolueeton): 3 tölkkiä → satunnainen esine (kypärä −30 % vahinkoa, lenkkarit +20 % nopeus, muut turhia).
- **Lumimyrsky** satunnaistapahtumana: nopeus ×0,6, mönkijä ×0,9, Lada 0.
- **Kännitekstarit**: täysi känni → pieni todennäköisyys viestiin exälle; koko joukkueen sijainti paljastuu vastustajalle 8 s.
- **Hemuli** (Peltolammin puolella): vaeltaa, syö kasveja; 20 % ateria → Puolijumala Caesar 30 s (owner 3, 400 HP, salama kaikkiin lähellä).
- **Vänä** (Multisillan puolella): baari → känni 30 s, potkii jalkapalloa lähimpään (5 ruutua, 50 vahinkoa, 4 s välein) → takaisin baariin.
- Debug (harjoitus): `{t:'debug', v4:'caesar'|'vana'|'mummo'|'tekstari'|'grilli'|'bileet'|'piiritys'}`, `{t:'debug', tap:'lumimyrsky'}`.
