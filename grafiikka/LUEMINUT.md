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
