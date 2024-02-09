# Erstellt mit python 3.9.7
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path
import array as arr

import time
import requests
import api_key

debug=False


if debug:
    print(api_key.API_KEY)

serial = i2c(port=2,address=0x3C)
device = sh1106(serial)

def getprices():
    preiseheute = arr.array('f')
    preisnext12 = arr.array('f')

    url = "https://api.tibber.com/v1-beta/gql"
    query = """
    {
    viewer {
        homes {
            currentSubscription{
                priceInfo{
                    today {
                        total
                        startsAt
                    }
                    tomorrow {
                        total
                        startsAt
                    }
                }
            }
        }
    }
    }
    """
    headers = {
        "Authorization": 'Bearer ' + api_key.API_KEY,
        "Content-Type": "application/json",
    }
    data = {"query": query}

    response = requests.post(url, json=data, headers=headers)
    # Drucke die Antwort
    if debug:
        print(response.json())

    response_data = response.json()
    prices = response_data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today']
    for price in prices:
        preiseheute.append(price["total"])
    pricestomorrow = response_data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['tomorrow']
    for price in pricestomorrow:
        preiseheute.append(price["total"])

    stunde = time.strftime('%H', time.localtime())
    for x in range(int(stunde),int(stunde) + 12):
        if debug:
            print(round(preiseheute[x],3))
        preisnext12.append(round(preiseheute[x],3))


    return preisnext12

def getprice():
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
    if debug:
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
        if debug:
            print("No current subscription found.")
    else:
        if debug:
            print("Total price:", total_price)

    # Drucke den Strompreis
    if debug:
        print(total_price)

    return total_price




def main():

    #Anzeige initialisieren
    fontsize = 12  # starting font size
    fonttime = ImageFont.truetype("Veranda.ttf", fontsize)
    fontprice = ImageFont.truetype("Veranda.ttf", 15)
    img_path = str(Path(__file__).resolve().parent.joinpath('tup.jpg'))
    thumbup = Image.open(img_path).convert("1")
    img_path = str(Path(__file__).resolve().parent.joinpath('tdown.jpg'))
    thumbdown = Image.open(img_path).convert("1")
    img_path = str(Path(__file__).resolve().parent.joinpath('cheap.jpg'))
    cheapicon = Image.open(img_path).convert("1")

    #Variablen initialisieren
    displausab=23
    displausbis=6

    preishoch=0.3
    preisniedrig=0.23


    while True:
        total_price=getprice()
        nextprices=getprices()

        #Display nachts ausschalten
        stunde = time.strftime('%H', time.localtime())
        if int(stunde) > displausbis and int(stunde) < displausab:

            #Datum, Preise und Icon anzeigen
            for i in range(1,10):
                if debug:
                    print(i)
                with canvas(device) as draw:
                    now = time.localtime()
                    jetzt = time.strftime('%H:%M:%S', now)
                    datum = time.strftime('%d.%m.%y', now)
                    #beim Stundenwechsel den aktuellen Preis holen
                    if stunde != int(time.strftime('%H', now)):
                        total_price=getprice()

                    draw.text((66,5), datum, font=fonttime , fill="white")
                    draw.text((66,18), jetzt, font=fonttime , fill="white")
                    draw.text((66,50), str(round(total_price,3))+"e" , font=fontprice, fill="white")

                    if total_price < preishoch and total_price > preisniedrig:
                        draw.bitmap((0, 0), thumbup, fill = "white")
                    if total_price > preishoch:
                        draw.bitmap((0, 0), thumbdown, fill = "white")
                    if total_price < preisniedrig:
                        draw.bitmap((0, 0), cheapicon, fill = "white")

                time.sleep(3)
                i+=1

            #Balkendiagramme malen
            if debug:
                print("weiter gehts")

            with canvas(device) as draw:
                draw.rectangle((0,0,128,64),fill = "black", outline = "black")
                draw.line((0,15,128,15), fill=10 )
                draw.line((0,35,128,35), fill=10 )
                draw.text((109,21), "25", font=fonttime , fill="white")
                draw.line((0,55,128,55), fill=10 )
                draw.text((109,41), "15", font=fonttime , fill="white")

                n=1
                for i in range(1,12):
                    nextbar=85 - (int(nextprices[i]*100)*2)
                    if debug:
                        print(nextbar)
                        print(nextprices[i])

                    draw.rectangle((n,nextbar,(n+5),64), fill = "white", outline = "white")
        #
                    n+=9
                    i+=1

            time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
