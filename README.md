# iotemb
IoT &amp; embedded systems

##Käyttöohje:
- Lataa main.py picoon ja käynnistä
- Kirjaudu PicoConfig WLAN verkkoyhteyspisteeseen
- Avaa web-selaimella picon IP (konsoliin tulostuu SSID, salasana ja IP-osoite)
- Anna oma WLAN SSID, salasana ja halutessa ntfy-palvelimen URL
- Pico boottaa, jonka jälkeen kirjautuu annettuun WLAN verkkoon ja alkaa lähettää ntfy-viestejä
- Paina nappia asettaaksesi korkeuden nollapisteen
- Pitämällä picon bootsel-nappia hetken pohjassa, pico unohtaa annetut asetukset ja palaa "tehdasasetuksiin"(AP-moodi)
- Käynnissä ollessa näytöllä näkyy korkeus ja lämpötila arvot
