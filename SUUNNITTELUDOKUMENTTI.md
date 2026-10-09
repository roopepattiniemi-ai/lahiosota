# LÄHIÖSOTA: ETELÄ-TAMPERE – suunnitteludokumentti v0.1

Omistaja: Roope Pättiniemi. Projektin vetäjä: Pelimestari (botti).
Kaikki projektin tiedostot: `/workspace/peli/` (jaettu kone, kaikki botit näkevät).

## 1. Ydinidea
Humoristinen, hidastempoinen reaaliaikastrategia (Red Alert -henkinen, vähän mikromanagerointia).
Tampereen Multisillan (SININEN, etelä) ja Peltolammin (PUNAINEN, pohjoinen) asukkaat sodassa.
Alkoholi ja päihteet vaikuttavat yksiköihin. Selainpeli, 1 vs 1 kaveria vastaan linkin kautta.
Matsin kesto noin 15–20 min.

## 2. Voittoehto
Vastustajan päämaja tuhotaan.

## 3. Resurssit
- Ainoa resurssi: pantilliset tyhjät tölkit.
- Tölkkejä on ympäri kenttää, ja kuolleet sotilaat pudottavat tölkkejä.
- Tölkit viedään kummankin alueen K-Marketiin (pantinpalautus) -> pantit = raha.

## 4. Kännimittari (ydinmekaniikka)
Jokaisella yksiköllä on kännimittari.
- Pieni humala: buusti (rohkeus, tarkkuus).
- Iso humala: riski kasvaa, että yksikkö
  - ilmoittaa lähtevänsä kotiin (poistuu),
  - sammuu (lamaantuu hetkeksi),
  - ampuu omiaan,
  - hidastuu,
  - lähtee baariin.

## 5. Rakennukset
Uusia rakennuksia EI rakenneta. Kartan oikeat paikat vallataan:
ensin vihollisen puolustajat ajetaan ulos, sitten valtaus kestää hetken.
Yksiköt koulutetaan omassa päämajassa. Vallatut paikat antavat bonuksia:

| Paikka (oikea) | Pelinimi | Bonus |
|---|---|---|
| Pub Pättäri (Multisilta) / Peltsun Saluuna (Peltolammi) | Kalja-varasto | Ilmainen kalja = buusti lähellä oleville, mutta karkaamisriski tiskille |
| K-Market (molemmilla) | Makkara-varasto / pantinpalautus | Tölkkien palautuspiste; vihollisen K-Marketin valtaus pakottaa sen kuskaamaan kauemmas |
| Peltolammin apteekki | Lääkintäasema | Parantaa ja laskee kännimittaria |
| Peltolammin kirjasto | Tiedustelukeskus | Paljastaa koko kartan hetkeksi |
| R-Kioski | Karkkikaivos | Energiajuoma: nopeampi liike |
| Multisillan Kultatähti Pizzeria | Pizzatehdas | Lisää kestävyyttä |
| Pupukahvila | Kahvilähde | Sammuneet heräävät nopeammin |
| Peltolammin viljelypalsta | Perunapelto | Tuottaa hitaasti pantteja passiivisesti |
| Tampereen logistiikkakeskus / Biltema | Huoltovarikko / Romutarvikevarasto | Halvemmat ajoneuvot |
| St1 / Gasum | Polttoaine- / Kaasuvarasto | Halvemmat molotovit; räjähtää jos tuhotaan |
| IKEA Tampere | Lihapullalinnake | Iso neutraali linnoitus, kova puolustusbonus |

## 6. Yksiköt
Yhteiset:
- **Tölkkijussi** – kerääjä; hidas, aseeton, kantaa paljon.
- **Lähiöjermu** – perusjalkaväki; halpa, juo herkimmin liikaa. Ase: Pystykorva (RK-62), vaihtoehtona Jatimatic.
- **Mopopoika** – nopea tiedustelija, voi varastaa vihollisen tölkkikuorman. Ase: Jatimatic.
- **Grillimestari** – puolustuspiste (pihagrilli sylkee makkaraa ja käryä, hidastaa). Tukena Emma-konekivääri.
- **Lähibaari** – buustipiste (vallattavat baarit).
Multisilta:
- **Kerrostalon parvekeampuja** – paikallaan pysyvä tykistö, kauas kantava.
- **Mummo rollaattorilla** – hidas, lähes tuhoutumaton "tankki".
Peltolammi:
- **Isä trimmerin kanssa** – lähitaistelu, raivaa pusikot.
- **Tuunattu Volvo** – kuljettaa jermuja ja jyrää, bensa kallis.

## 7. Aseet
- Jatimatic – konepistooli, nopea, epätarkka humalassa.
- Pystykorva (RK-62) – luotettava rynnäkkökivääri.
- Emma-konekivääri – raskas tukiase.
- Suomi-konepistooli – raskaampi konepistooli.
- Puukko – lähitaistelu.
- Molotovin cocktail – halpa heitettävä, valmistukseen kuluu kaljaa; humalainen voi pudottaa omiin jalkoihin. Sateessa ei syty kunnolla.

## 8. Ajoneuvot
- Dnepr-sivuvaunumoottoripyörä – nopea kuljetus/hyökkäys, sivuvaunussa Emma-ampuja.
- Mönkijä – kevyt ja nopea maastossa.
- Lada – halpa kuljetus.
- Tuunattu Volvo (Peltolammi).

## 9. Satunnaistapahtumat
Poliisipartio (vie humalaiset putkaan), Alkon alennusmyynti (halpa buusti, jermut jonoon),
Sadekuuro (hidastaa, molotovit eivät syty), Pantinpalautusautomaatti rikki (toinen K-Market kiinni),
Pihakirppis (tölkkikasoja kentälle), Saunailta (Peltolammi: osa löylyihin, palaavat terästettyinä),
Taloyhtiön kokous (Multisilta: osa jumissa sisällä), Bussi 3 myöhässä (tukijoukot viivästyvät),
Kesäjuhlat (aselepo, tuplapantit).

## 10. Kartta
Oikea alue OpenStreetMap-datasta: `/workspace/peli/kartta/`
- `pelikentta_v1.png` (tyyli-/suunnittelukartta), `pelikentta_v1_tiles.json` (64x64 ruudukko, ruutu ~45 m, maastotyypit, omistus, tukikohdat, resurssit, pullonkaulat).
- Peltolammi pohjoisessa (punainen), Multisilta etelässä (sininen). Raja Peltolammen lammen ja Lempääläntien kohdalla.
- Pullonkaulat: Lempääläntie, Ratasilta (Päärata), Pyörätiesola (Vt 3:n lähellä).
- Huom: 15–20 min matsiin karttaa voi joutua tiivistämään/skaalaamaan.
- OSM-attribuutio pakollinen: © OpenStreetMap contributors.

## 11. Grafiikka
Retro pikselitaide, isometrinen 90-luvun RTS-tyyli (Red Alert). Referenssi:
`/workspace/peli/tyyli/tyyli_1_pikseli.jpg`. Oikeanpuoleinen sivupaneeli UI:lle.
Ei oikeita brändilogoja (K-Market, R-Kioski ym. nimetään pelinimillä tai neutraalisti).

## 12. Musiikki ja äänet
Sotilaallinen industrial-rock, Red Alertin (Hell March) henkeen. Lisäksi yksiköiden suomenkieliset
huudahdukset ("Selvä pomo!", "Mää lähen kotiin…") ja ääniefektit (tölkin kilinä, mopo, Dnepr).

## 13. Tekniikka (raakaversio)
- Selainpeli: HTML5 Canvas / esim. Phaser 3 + TypeScript tai pelkkä JS.
- Moninpeli: 1v1 huone linkillä (esim. WebSocket-palvelin Node.js:llä, palvelin auktoriteettina tai lockstep).
- Raakaversion tavoite: yksi kartta pelattavana, Tölkkijussi + Lähiöjermu + Mopopoika, tölkkien keruu,
  K-Market-palautus, kännimittarin perusvaikutukset, rakennusten valtaus, päämajan tuhoaminen,
  placeholder-grafiikat sallittuja.

## 14. Avoimet kysymykset
- Hosting: missä peli pyörii netissä (esim. ilmainen palvelin)?
- Pelin lopullinen nimi (työnimi "Lähiösota: Etelä-Tampere").
- Yksiköiden tarkat hinnat ja tasapaino.
