# popis pôvodnej databázy
## export

> *tabuľka záznamov o zápise predmetu spolu s hodnotou pass/fail*

- **id** - unikátny identifikátor (anonymného) študenta
- **idpred** - identifikátor predmetu - kľúč pre tabuľku **predmet**
- **akrok** - akademický rok v ktorom sa tento zápis konal
- **semester** - hodnota Z/L označujúca semester
- **pass** - údaj o tom či študent prešiel (hodnota 1 ak je známka z {A,B,C,D,E}) alebo nie (hodnota 0, známka Fx)
- **skratkasp** - skratka študijného programu študenta z tabuľky **studprog**

## predmet

> *zoznam všetkých bakalárskych a magisterských predmetov*

- **idpred** - identifikátor predmetu
- **kodpred** - oficiálny kód predmetu
- **stredisko** - stredisko ktoré zabezpečuje výučbu tohto predmetu
- **skratkapres** - skratka oficiálneho kódu
- **nazovpred** - celý oficiálny názov predmetu

## studprog

> *zoznam všetkých ponúkaných študijných programov*

- **skratkasp** - skratka študijného programu
- **sp** - celý názov študijného programu

## poctyznamok2

> *počet konkrétnej známky pre každú známku a každý predmet kde bolo v danom ak.roku aspoň 10 študentov*

- **idpred** - identifikátor predmetu
- **akrok** - akademický rok v ktorom sa tento zápis konal
- **kodhod** - konkrétna známka (A/B/C/D/E/FX)
- **pocet** - počet študentov ktorí v **akrok** dostali známku **kodhod**

## znamky2

> *počty študentov, ktorí skončili s jednotlivými známkami v danom ak.roku kde bolo zapísaných aspoň 10 študentov*

- **idpred** - identifikátor predmetu
- **akrok** - akademický rok v ktorom sa tento zápis konal
- **a** - pocet študentov ktorí v danom **akrok** skončili so známkou A
- **b** - pocet študentov ktorí v danom **akrok** skončili so známkou B
- **c** - pocet študentov ktorí v danom **akrok** skončili so známkou C
- **d** - pocet študentov ktorí v danom **akrok** skončili so známkou D
- **e** - pocet študentov ktorí v danom **akrok** skončili so známkou E
- **fx** - pocet študentov ktorí v danom **akrok** skončili so známkou FX
- **bez** - pocet neudelenych hodnoteni
- **n** - celkovy pocet studentov na danom predmete v danom roku

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

 