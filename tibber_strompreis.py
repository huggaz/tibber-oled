# Erstellt mit python 3.9.7
# Danke an https://github.com/SomethingWithComputers/pixoo er hat eine Library für das Pixoo64 Display geschrieben


from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path

import time
import requests
import api_key

print(api_key.API_KEY)

serial = i2c(port=2,address=0x3C)
device = sh1106(serial)





# Funktion um den Strompreis von Tibber abzufragen und auf dem Pixoo64 Display anzuzeigen
def main():
    # Setzte die Api URL
    url = "https://api.tibber.com/v1-beta/gql"

    # Setze die Abfrage
    query = """
    {
    viewer {
        homes {
        currentSubscription {
            priceInfo {
            current {
                total
                energy
                tax
                startsAt
            }
            }
        }
        }
    }
    }
    """
    img_path = str(Path(__file__).resolve().parent.joinpath('tup.jpg'))
    thumbup = Image.open(img_path).convert("1")
    img_path = str(Path(__file__).resolve().parent.joinpath('tdown.jpg'))
    thumbdown = Image.open(img_path).convert("1")
    img_path = str(Path(__file__).resolve().parent.joinpath('cheap.jpg'))
    cheapicon = Image.open(img_path).convert("1")

    # Trage hier deine  Authentifizierung ein
    headers = {
        "Authorization": 'Bearer ' + api_key.API_KEY,
        "Content-Type": "application/json",
    }

#    virtual = viewport(device, width=128, height=64)

    # Setze die Abfrage
    data = {"query": query}

    # Sende die Abfrage
    response = requests.post(url, json=data, headers=headers)

    # Drucke die Antwort
    print(response.json())

    # Schreibe die Antwort in eine Variable
    response_data = response.json()

    # Bilde den Strompreis aus der Antwort
    homes = response_data["data"]["viewer"]["homes"]
    total_price = None
    for home in homes:
        if home.get("currentSubscription") is not None:
            total_price = home["currentSubscription"]["priceInfo"]["current"]["total"]
            break
    if total_price is None:
        print("No current subscription found.")
    else:
        print("Total price:", total_price)

    # Drucke den Strompreis
    print(total_price)



    # Zeige aktuelle Uhrzeit und gebe sie im deutschen Format aus
    fontsize = 12  # starting font size
    fonttime = ImageFont.truetype("Veranda.ttf", fontsize)
    fontprice = ImageFont.truetype("Veranda.ttf", 15)


    while True:
        with canvas(device) as draw:
            now = time.localtime()
            jetzt = time.strftime('%H:%M:%S', now)
            datum = time.strftime('%d.%m.%y', now)

            draw.text((66,5), datum, font=fonttime , fill="white")
            draw.text((66,18), jetzt, font=fonttime , fill="white")

#            draw.text((1,30), "Strompreis")
            draw.text((66,50), str(round(total_price,3))+"ct" , font=fontprice, fill="white")


            if total_price < 0.31 and total_price > 0.25:
                draw.bitmap((0, 0), thumbup, fill = "white")
            if total_price > 0.31:
                draw.bitmap((0, 0), thumbdown, fill = "white")
            if total_price < 0.25:
                draw.bitmap((0, 0), cheapicon, fill = "white")

        time.sleep(5)

"""
    # Ist der total_price kleiner als 0,3 dann zeige grüne Ampel
    if total_price < 0.3:
        pix.draw_image('images/ampel_gruen.png')
    # Ist der total_price größer als 0,3 und kleiner als 0,4 dann zeige gelbe Ampel
    elif total_price > 0.3 and total_price < 0.4:
        pix.draw_image('images/ampel_gelb.png')
    # Ist der total_price größer als 0,4 dann zeige rote Ampel
    elif total_price > 0.4:
        pix.draw_image('images/ampel_rot.png')

    # Schreibe die Texte auf dem Display
    pix.draw_text('Tibber', (3,  3), (  0,   255, 0))
    pix.draw_text('Strompreis', (3,  9), (255,   0,   0))
    pix.draw_text(time.strftime('%d.%m.%Y', now), (3,  15), (252,253,254))
    pix.draw_text(time.strftime('%H:%M', now), (3,  21), (252,253,254))
    # Ist der total_price kleiner als 0,3 dann zeige grüne Schrift
    if total_price < 0.3:
        pix.draw_text(str(total_price) + ' Euro', (3,  28), (0,255,0))
    # Ist der total_price größer als 0,3 und kleiner als 0,4 dann zeige gelbe Schrift
    elif total_price > 0.3 and total_price < 0.4:
        pix.draw_text(str(total_price) + ' Euro', (3,  28), (255,255,0))
    # Ist der total_price größer als 0,4 dann zeige rote Schrift
    elif total_price > 0.4:
        pix.draw_text(str(total_price) + ' Euro', (3,  28), (255,   0,   0))

    pix.draw_text('Preis', (3, 50), (252,   253,   254))
    pix.draw_text('inkl. Abgaben', (3, 56), (252,   253,   254))
    # Zeige die Texte auf dem Display
    pix.push()
    # Schreibe die Laufschrift auf dem Display
    pix.send_text( '    Jede Stunde wird der Preis angepasst                    ' , (0, 32), (  0,   255, 0), 1, 0, 46,  75)

    # Setze den Hintergrund auf schwarz
    pix.fill((0, 0, 0))
    # Bestimme das Hintergrundbild
    # Ist der total_price kleiner als 0,3 dann zeige grüne Ampel
    if total_price < 0.3:
        pix.draw_image('images/ampel_gruen.png')
    # Ist der total_price größer als 0,3 und kleiner als 0,4 dann zeige gelbe Ampel
    elif total_price > 0.3 and total_price < 0.4:
        pix.draw_image('images/ampel_gelb.png')
    # Ist der total_price größer als 0,4 dann zeige rote Ampel
    elif total_price > 0.4:
        pix.draw_image('images/ampel_rot.png')


        oled_font = ImageFont.truetype('FreeSans.ttf', 14)
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline = "white", fill = "black")
            draw.text((10, 10), "OLED-Display", font = oled_font, fill = "white")
"""
    # wiederholen alle 10 Sekunden die Funktion


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
