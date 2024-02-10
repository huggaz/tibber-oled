A small project to display the current tibber price on a sh1106 128x64 pixel OLED display. Works find on a banana pi and raspberry pi. 
The display changes every 30 seconds between date&time and current price and a chart previewing the next 12 hours price. 

Also on the first screen an icon is shown to view at a quick glance if the price is cheap or not. 

Hardware:
https://www.amazon.de/dp/B078J78R45/ref=twister_B07Z5C98B4

HowTo:
Just create an API Key on the Tibber site and replace the demo key in api_key.py ( https://developer.tibber.com/settings/accesstoken )

The script pauses the output between 23 and 7 o'clock. This can be configured with displausab and displausbis.

Also the high and low price can be configured with preishoch preisniedrig variables, which affect the icon that is displayed.

Inspired by https://github.com/techpirat-de/pixoo64-tibber-preisanzeige 
