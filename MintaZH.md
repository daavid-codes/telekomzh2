**Title:** 2026/27/1 XK85DZ-IP-18TKHG - Telekommunikációs hálózatok Gy: MintaZH

**Source:** [https://moodle.elte.hu/mod/page/view.php?id=631660](https://moodle.elte.hu/mod/page/view.php?id=631660)

---

1. Készítsünk egy TCP klienst, ami egy adott szerverrel tud kommunikálni! A ZH-n a szerver meg lesz adva! A kliens egy szöveget és egy számot küld a szervernek struct segítségével (20s i), ld. alább a változatokat. A szerver a szám alapján levág a szöveg elejéről X darab karaktert és megfordítja, amit visszaküld a kliensnek. Itt a formátum a kapott számérték alapján legyen (Xs).  
	Példa:  
	almafa,4 -> amla  
	kortefa,3 -> rok
	Feladatváltozatok:  
	a) A kliens a felhasználótól kérje be a szöveget, valamint generáljon egy véletlen számot!  
	b) A kliens töltse be az alábbi tartalmú input.txt fájlt (ezt hozzuk létre előzőleg):
	```
	almafa 4
	kortefa 3
	barackfa 5
	```
	ezután a kliens generáljon egy véletlen számot 1 és 3 között, a számnak megfelelő sort töltse be és a sornak megfelelően küldje el a szervernek a szöveget és a számot!
	c) A kliens töltse be az alábbi tartalmú input.json fájlt (ezt hozzuk létre előzőleg):
	```
	{
	"1": ["almafa", 4],
	"2": ["kortefa", 3],
	"3": ["barackfa", 5]
	}
	```
	ezután a kliens generáljon egy véletlen számot 1 és 3 között, alakítsa át sztringgé és ezt a JSON-ben kulcsként használva a hozzátartozó szöveget és számot küldje majd el a szervernek!  
	d) A TCP kliens helyett használjunk UDP klienst! (Ekkor a szerver nyilván UDP szerver lesz.)
2. Készítsünk egy TCP szervert, amely a select segítségével egyszerre több kliens kiszolgálására is képes.  
	A szerver egy egész számot tárol, amelynek kezdeti értéke 0. A kliensek háromféle parancsot küldhetnek a szervernek:  
	\- IN X – állítsa be az értéket X-re (ahol X egy egész szám)  
	\- INCR X – növelje az értéket X-szel  
	\- DECR X – csökkentse az értéket X-szel  
	A parancsokat a kliensek struct formátumban küldik (4s i). A szerver minden beérkező parancs feldolgozása után visszaküldi a kliensnek a módosított értéket bytesztringként. A ZH lesz egy teszt környezet megadva, amely hívni fogja a szerverünket!  
	Példa:  
	IN, 20 → a szervernél tárolt érték 20 lesz, és ezt küldi vissza a kliensnek  
	INCR, 4 → a szervernél tárolt érték 24 lesz, és ezt küldi vissza a kliensnek  
	DECR, 5 → a szervernél tárolt érték 19 lesz, és ezt küldi vissza a kliensnek
3. Egészítsük ki az előző feladatot úgy, hogy többféle szerver és kliens is szerepeljen a rendszerben! (*Kezdetben a szerverek nem proxy szerverek, hanem önállóan működő TCP és/vagy UDP szerverek, amelyek különböző portokon hallgatnak. A kliensek szabadon eldönthetik, melyik szerverekkel szeretnének kommunikálni, és akár több szerverrel is kapcsolatba léphetnek. A feladat később ezt részletezi!*) Ez a több szereplős feladat a ZH-n független lesz a többi feladattól, továbbá a szereplők közül várhatóan lesznek olyanok, amelyeknek az implementációja előre meg lesz adva, így a hallgatóknak csak a fennmaradó részeket kell elkészíteniük.  
	Feladatváltozatok:
	a) Készítsünk egy UDP szervert, amely szintén tárol egy egész számot a TCP szerverhez hasonlóan. A parancsok nevei itt eltérnek a TCP-s változattól:
	\- PUSH X – állítsa be az értéket X-re
	\- PLUS X – növelje az értéket X-szel
	\- MINUS X – csökkentse az értéket X-szel
	Emiatt a parancsokat (5s i) formátummal tudja fogadni, a szerver a választ szintén struct formátumban (i) küldi vissza (nem sima bytesztringként).
	b) Tegyük fel, hogy az a) részben ismertetett UDP szerver véletlenszerűen hibázhat:
	\- minden parancs feldolgozásakor a kapott számhoz véletlenszerűen hozzáad -1, 0 vagy 1 értéket.
	Készítsünk egy ellenőrző klienst, amely
	\- lekérdezi a TCP és az UDP szervertől is a tárolt értéket, azaz küldjön egy „0-val való növelést”,
	\- a visszakapott értékek összehasonlításával állapítsa meg, hogy az UDP szerver hibázott-e.
	c) Alakítsuk át az eredeti TCP szervert úgy, hogy:
	\- ne tárolja saját magánál az értéket,
	\- hanem proxyként működjön:
	\- a kliensek parancsait továbbítsa az a) részben ismertetett UDP szerver felé,
	\- az értéket ténylegesen az UDP szerver tárolja,
	\- a TCP szerver pedig az UDP szerver válaszát küldje vissza a klienseknek.

Utolsó módosítás: 2026. október 19., hétfő, 13:48