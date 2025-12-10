import network
import socket
import time
import machine

CONFIG_FILE = "wlan_config.txt"
AP_SSID = "PicoConfig"
AP_PASSWORD = "salasana"
AP_IP = '192.168.4.1'

def url_decode(s):
    # Yksinkertaistettu URL-dekoodaus: korvaa '+' välilyönnillä ja dekoodaa %-koodaukset.
    s = s.replace('+', ' ')
    parts = s.split('%')
    decoded = parts[0]
    for part in parts[1:]:
        if len(part) >= 2:
            try:
                # Muunnetaan heksadesimaaliluku merkiksi
                char_code = int(part[:2], 16)
                decoded += chr(char_code) + part[2:]
            except ValueError:
                decoded += '%' + part # Jos ei ole validi heksadesimaali, jätetään ennalleen
        else:
            decoded += '%' + part
    return decoded.strip()

def setup_access_point():
    # Asettaa Pico W:n Access Point -tilaan.
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    wlan.config(essid=AP_SSID, password=AP_PASSWORD)
    # Asetetaan staattinen IP AP:lle
    wlan.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    print(f"Access Point käynnistetty: SSID='{AP_SSID}'")
    print(f"Yhdistä osoitteeseen: http://{AP_IP}")
    return wlan

def save_config(ssid, password):
    # Tallentaa uudet tunnukset tiedostoon ja käynnistää laitteen uudelleen.
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(f"{ssid}\n")
            f.write(f"{password}\n")
        print("WLAN-tunnukset tallennettu. Käynnistetään uudelleen...")
        time.sleep(4)
        machine.reset() # Käynnistää laitteen uudelleen
    except Exception as e:
        print(f"Virhe tallennuksessa: {e}")

# --- HTML-koodi konfigurointisivulle ---
def web_page():
    html = """
    <html>
    <head><title>Pico W Konfigurointi</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
      <h1>Pico W WLAN Konfigurointi</h1>
      <form action="/save" method="post">
        <label for="ssid">Verkon nimi (SSID):</label><br>
        <input type="text" id="ssid" name="ssid" required><br><br>
        <label for="password">Salasana:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <input type="submit" value="Tallenna ja Käynnistä Uudelleen">
      </form>
    </body>
    </html>
    """
    return html

# --- Palvelinlogiikka ---

# 1. Aseta Access Point
ap = setup_access_point()

# 2. Avaa Socket-portti
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        print('Saapunut pyyntö:', request)

        # Tarkista, onko kyseessä POST-pyyntö konfigurointitietojen tallentamiseen
        if request.startswith('POST /save'):
            content_start = request.find('\r\n\r\n') + 4
            post_data = request[content_start:]
            
            params = {}
            for pair in post_data.split('&'):
                try:
                    key, value_encoded = pair.split('=', 1)
                    params[key] = url_decode(value_encoded)
                except ValueError:
                    pass

            if 'ssid' in params and 'password' in params:
                print(f"Tallennetaan uudet tunnukset: SSID='{params['ssid']}'")
                save_config(params['ssid'], params['password'])
            
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Tunnukset tallennettu! Uudelleenkäynnistys käynnissä...</h1>"
        
        else:
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + web_page()

        conn.sendall(response.encode())
        conn.close()

    except OSError as e:
        conn.close()
        print('Yhteysvirhe:', e)

