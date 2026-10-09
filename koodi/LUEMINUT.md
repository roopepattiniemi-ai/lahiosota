# Lähiösota: Etelä-Tampere – raakaversio (koodi)

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
- Z / X / C: kouluta Tölkkijussi / Lähiöjermu / Mopopoika. H: seis. M: äänet päälle/pois.
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

## Mitä ei vielä ole
Sumu (fog of war), ajoneuvot, molotovit, Grillimestari, puolikohtaiset erikoisyksiköt, satunnaistapahtumat, animaatiot, tasapainotus.

## Tiedostot
- `server.js` – HTTP + WebSocket, huoneet linkeillä, 10 tickiä/s.
- `game.js` – koko pelilogiikka (A*-reitinhaku, talous, kännimittari, valtaus, taistelu).
- `public/` – selainasiakas (Canvas 2D, ei kirjastoja): `index.html`, `peli.js`, `tyyli.css`.
- Grafiikka luetaan kansiosta `../grafiikka/`, äänet `../aanet/`, kartta `../kartta/pelikentta_v1_tiles.json`.
- Odotetut assetit: `/workspace/peli/ASSET_LISTA.md`.

Karttadata © OpenStreetMap-tekijät (ODbL).
