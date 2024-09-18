# sematizmus

A Magyar Katolikus Egyház papjainak névsora és néhány adata

A magyarországi egyházmegyék honlapjairól bányássza ki az adatokat ez a script gyűjtemény, amit használ a katolikus KSH repo és talán majd a `papima` ami a papokért való imádságot segíti.

##  Hogyan használd?

- Mindenekelőtt telepítsd a függősegeket: `pip3 install -r requirements.txt`
- Ha csak egy egyházmegye papjait szeretnéd lekérni, akkor `python3 XScraper.py`, ahol X az egyházmegye rövidítése
- Ha mindegyikét, akkor `python3 CollectAll.py`
- Ha ezeket fájlba szeretnéd menteni, akkor használd a `--filename FAJLNEV` kapcsolót, ahol `FAJLNEV` a fájl neve.
