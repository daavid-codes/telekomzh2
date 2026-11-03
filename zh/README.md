# 2. ZH – megoldások magyarázata

Mindhárom feladat ugyanarra a néhány alapelemre épül, ezért először ezeket nézzük át, utána jönnek a feladatok egyenként.

## Közös alapok

### `struct` – bináris üzenetek

A hálózaton bájtok mennek, nem Python-objektumok. A `struct` modul egy formátumleírás alapján bájtsorozattá alakítja (`pack`) és visszaalakítja (`unpack`) az adatokat.

| Formátum | Jelentés |
|---|---|
| `i` | 4 bájtos egész szám (int) |
| `6s` | pontosan 6 bájtos bájtsztring |

```python
p = struct.Struct("6s 8s 7s")
p.size                                  # 21 bájt
p.pack(b"ABC123", b"RZ65", b"request")  # 21 bájtos bytes
```

Két fontos tulajdonság:

- **Kitöltés `\x00`-val.** Ha a sztring rövidebb a mezőnél, a `pack` nullbájtokkal tölti fel. A `b"RZ65"` egy `8s` mezőben `b"RZ65\x00\x00\x00\x00"` lesz. Visszaolvasáskor ezt le kell vágni: `.rstrip(b"\x00")`. A sima `.strip()` **nem** veszi le a nullbájtokat, mert csak a whitespace-t vágja le. Ez gyakori hibaforrás, például a `"economy" == "economy\x00\x00\x00"` összehasonlítás hamis.
- **Igazítás (alignment).** Előtag nélkül (`"3s 6s 8s i"`) a `struct` natív igazítást használ, ezért az `i` elé kitöltő bájtok kerülhetnek. A `3s 6s 8s i` formátum 17 + 3 kitöltés + 4 = **20 bájt**, nem 21. Ezért mindig a `Struct(...).size` értékét használjuk, nem kézzel számolunk. A tesztkliens ugyanazt a formátumsztringet használja, így a méretek egyeznek.

### TCP: egy `recv` nem egy üzenet

A TCP bájtfolyam, nem üzenetek sorozata. Egy `recv(n)` hívás kevesebbet is visszaadhat, mint `n` bájt, de akár két üzenetet is egyben. Ezért:

- **Kliensnél** (1. feladat) egy `recv_exact` segédfüggvény addig olvas, amíg pontosan a kívánt bájtszám meg nem érkezik.
- **Szervernél** (2. és 3. feladat) minden kliensnek saját **puffere** van. A beérkezett bájtokat ehhez fűzzük, és amíg a pufferben van legalább egy teljes üzenetnyi adat, levágjuk és feldolgozzuk.

```python
pufferek[s] += data
while len(pufferek[s]) >= keres.size:
    uzenet, pufferek[s] = pufferek[s][:keres.size], pufferek[s][keres.size:]
    ...
```

### `select` – több kliens egy szálon

A `select.select(olvasni, irni, hiba)` addig blokkol, amíg a megadott socketek közül valamelyik olvasható nem lesz, aztán visszaadja azokat. Egy szerver így egyetlen szálon tud sok klienst kiszolgálni:

- ha a **listening socket** olvasható, új kliens kapcsolódik, ezt `accept()`-tel fogadjuk;
- ha egy **kliens socket** olvasható, adat jött, ezt `recv()`-vel olvassuk;
- ha a `recv()` **üres bájtsztringet** (`b""`) ad, a kliens bezárta a kapcsolatot, ilyenkor mi is lezárjuk és kivesszük a listából.

A `SO_REUSEADDR` opció azért kell, hogy a szerver újraindításakor ne kapjunk „Address already in use” hibát.

---

## 1. feladat – TCP kliens (`feladat1/client.py`)

Indítás: `python client.py localhost 20001`

### A protokoll

```
kliens                                   szerver
  | -- (neptun, "RZ65", "request")  6s 8s 7s -->  |
  | <-- (szabad_helyek, osztály)    i 10s     --  |
  | -- (neptun, "RZ65", "reserve"/"reject") -->   |
  | <-- foglalási azonosító         12s       --  |
```

Mind a négy üzenet **ugyanazon a kapcsolaton** megy, tehát a socketet csak a legvégén szabad lezárni.

### Döntési szabály

Reserve akkor kell, ha **mindkét** feltétel teljesül: legalább 4 szabad hely van, **és** az osztály `economy`. Minden más esetben reject:

```python
tipus = b"reserve" if szam >= 4 and osztaly == b"economy" else b"reject"
```

(Ennek tagadott alakja a feladatszöveg feltétele: „nem economy **vagy** kevesebb mint 4”. Ha `and`-del tagadnánk, az rossz lenne.)

### Megoldás

```python
host, port = sys.argv[1], int(sys.argv[2])
neptun, jarat = b"ABC123", b"RZ65"          # ABC123 helyére a saját neptun kód

p = struct.Struct("6s 8s 7s")
valasz = struct.Struct("i 10s")
vegso = struct.Struct("12s")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(p.pack(neptun, jarat, b"request"))

    szam, osztaly = valasz.unpack(recv_exact(s, valasz.size))
    osztaly = osztaly.rstrip(b"\x00")

    tipus = b"reserve" if szam >= 4 and osztaly == b"economy" else b"reject"
    s.sendall(p.pack(neptun, jarat, tipus))

    (azon,) = vegso.unpack(recv_exact(s, vegso.size))
    print("Foglalasi azonosito:", azon.rstrip(b"\x00").decode())
```

### Lépésenként

1. **Paraméterek.** A host és a port a parancssorból jön (`sys.argv[1]`, `sys.argv[2]`). A portot `int()`-té kell alakítani. A neptun kód és a járatszám fix, ezek a kódban szerepelnek.
2. **Kapcsolódás és kérés.** `connect`, majd `sendall` a 21 bájtos `request` üzenettel. A `sendall` garantálja, hogy minden bájt elmegy, a `send` nem.
3. **Válasz fogadása.** A `recv_exact` pontosan `valasz.size` bájtot olvas, ezután jön az `unpack`. Az osztálynévről levágjuk a `\x00` kitöltést.
4. **Döntés és második üzenet.** Ugyanazon a socketen elküldjük a `reserve` vagy `reject` üzenetet.
5. **Végső válasz.** Fogadjuk a 12 bájtos foglalási azonosítót, és kiírjuk.

---

## 2. feladat – select alapú TCP szerver (`feladat2/server.py`)

Indítás: `python server.py <port>`

### Adatszerkezet

```python
keszlet = defaultdict(lambda: defaultdict(int))   # raktar -> termek -> darab
```

A beágyazott `defaultdict` miatt egy még nem létező raktár vagy termék automatikusan 0 darabbal jön létre. Így a `GET` egy ismeretlen termékre 0-t ad, a `TOT` egy üres raktárra szintén 0-t, és nem kell külön ellenőrizni, hogy létezik-e a kulcs.

### Üzenetek

- **Kérés:** `(3s 6s 8s i)`, vagyis parancs, raktár, termék és mennyiség. A natív igazítás miatt ez 20 bájt.
- **Válasz:** `(i)`, egyetlen egész szám.

### A parancsok feldolgozása

```python
cmd, w, p, q = keres.unpack(uzenet)
cmd = cmd.rstrip(b"\x00")
w, p = w.rstrip(b"\x00"), p.rstrip(b"\x00")

if cmd == b"ADD":
    keszlet[w][p] += q
    eredmeny = keszlet[w][p]
elif cmd == b"GET":
    eredmeny = keszlet[w][p]
else:  # TOT
    eredmeny = sum(keszlet[w].values())

s.sendall(valasz.pack(eredmeny))
```

| Parancs | Mit csinál | Mit ad vissza |
|---|---|---|
| `ADD W P Q` | `keszlet[W][P] += Q` | a termék új darabszáma |
| `GET W P 0` | semmit | a termék darabszáma |
| `TOT W AAAAAAAA 0` | semmit | a raktár összes termékének összege |

A `\x00` levágása itt is fontos. A `"WH001"` egy `6s` mezőben `b"WH001\x00"` lesz. A kulcsok így mindenhol egységesek, a kiírás is szép, és nem marad nullbájt a kulcsokban.

A `TOT` parancsnál a `P` mezőben álló `"AAAAAAAA"` csak kitöltés, ezért nem használjuk. Az egész raktárat összegezzük.

### A fő ciklus

```python
while True:
    olvashato, _, _ = select.select([server, *pufferek], [], [])
    for s in olvashato:
        if s is server:            # új kliens
            kliens, _ = server.accept()
            pufferek[kliens] = b""
            continue
        data = s.recv(1024)
        if not data:               # a kliens kilépett
            del pufferek[s]
            s.close()
            continue
        pufferek[s] += data
        while len(pufferek[s]) >= keres.size:
            ...                    # egy teljes üzenet feldolgozása
```

A `pufferek` szótár kulcsai egyben az aktív kliensek listája is. Ezért a `select`-nek a `[server, *pufferek]` listát adjuk át, és nem kell külön listát vezetni.

### Teszt a feladat példájával

A feladat példáját két külön klienssel futtattam le (ADD és GET, ADD és TOT felváltva). A válaszok `[10, 10, 5, 15]` lettek, ahogy a feladat kéri. Ebből az is látszik, hogy a készlet közös minden kliens között.

---

## 3. feladat – TCP→UDP proxy (`feladat3/proxy.py`)

Indítás: `python proxy.py 10002 20002`

### Az adatfolyam

```
kliens --TCP (i 20s)--> proxy --UDP (5s 20s)--> Azonosítási Szerver
kliens <--TCP (válasz)-- proxy <--UDP (válasz)-- Azonosítási Szerver
```

| Kliens típusa | Proxy → szerver |
|---|---|
| 0 (Felhasználó) | `("LOGIN", név)` |
| 1 (Vendég) | `("GUEST", név)` |

```python
TIPUSOK = {0: b"LOGIN", 1: b"GUEST"}
tipus, nev = kliens_uzenet.unpack(uzenet)
kliens_udp[s].sendto(szerver_uzenet.pack(TIPUSOK[tipus], nev), szerver)
```

A felhasználónév már eleve egy 20 bájtos, kitöltött mező, ezért itt **nem** vágjuk le a nullbájtokat. Változatlanul megy tovább az új `20s` mezőbe.

### A fő tervezési döntés: minden kliensnek saját UDP socketje van

A UDP kapcsolat nélküli. Ha egyetlen közös UDP socketen menne minden kérés, a beérkező válaszról nem tudnánk eldönteni, melyik kliensé. Ha például A és B kliens egyszerre küld kérést, a két válasz bármilyen sorrendben visszajöhet.

Ennek megoldására minden új TCP kliens kap egy saját UDP socketet. A szerver a választ arra a címre és portra küldi, ahonnan a kérés jött, így a válasz automatikusan a megfelelő UDP sockethez érkezik. Két szótárban tartjuk nyilván a párosítást:

```python
udp_kliens = {}  # udp socket -> tcp kliens
kliens_udp = {}  # tcp kliens -> udp socket
```

Az egyszerűbb megoldás az lenne, ha minden kérés után blokkolva várnánk a választ (`sendto`, majd rögtön `recvfrom`). Ez azonban a várakozás alatt megállítaná az összes többi klienst, és elveszne a `select` lényege.

### A fő ciklus

A `select` háromféle socketet figyel:

```python
olvashato, _, _ = select.select([proxy, *pufferek, *udp_kliens], [], [])
```

| Melyik socket olvasható | Teendő |
|---|---|
| `proxy` (TCP listening) | `accept()`, új UDP socket létrehozása és a pár bejegyzése |
| UDP socket | `recvfrom()`, a válasz változatlanul megy a párjához: `sendall(data)` |
| TCP kliens | `recv()`, pufferelés, minden teljes `(i 20s)` üzenet átalakítása és továbbküldése UDP-n |

Ha egy TCP kliens bontja a kapcsolatot (`recv` → `b""`), a `lezar()` függvény a hozzá tartozó UDP socketet is lezárja, és mindkét szótárból kitörli a párt.

Az ágak `elif s in udp_kliens` / `elif s in pufferek` alakúak. Ha egy klienst ugyanabban a körben már lezártunk, a még a listában lévő UDP socketje egyik ágba sem kerül bele, így nem írunk lezárt socketre.

### Teszt

Egy saját, egyszerűsített UDP szerverrel próbáltam ki, amely visszaküldi a kapott üzenetet. Két egyidejű klienssel (egy 0-s és egy 1-es típusúval) mindkettő a saját válaszát kapta vissza: `LOGINalice` és `GUESTbob`.

---

## Ellenőrzés

A csomag mappájából (ahol a `tests.py` van), futó Docker Desktoppal:

```
python tests.py check <KÓD> feladat1
python tests.py check y8h4tq2b7kmx feladat2
python tests.py check R8mK2vX7pQ4n feladat3
```

Az 1. feladat kódja a Moodle-kérdésben szerepel.
