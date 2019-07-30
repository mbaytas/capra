# Capra 🎥 ⛰️

*A system for hikers to document and revisit their past hikes.*

---

## Remote Connection
There is a RealVNC Capra group for connecting to both the cameras and projectors remotely. Login details can be found in the Dropbox.

## Collector (Camera unit)
### Services
The timelapse program is started on power up by the service: `/lib/systemd/system/capra-startup.service`

The (on/off) button is controlled by the service: `/lib/systemd/system/capra-listen-for-shutdown.service`

### Hardware
Electronically, the Capra Collector consists of the following components _(items with an asterisk are further elaborated on)_:
- Raspberry Pi Zero
- [Adafruit Powerboost 1000](https://www.adafruit.com/product/2465)
- Custom PCB: Cam Multiplexer *
- Custom PCB: Buttonboard *
- 2 x 21700 LiPo Batteries *
- 3 x Raspberry Pi Camera V2's.

In the image below, a systematic view of the respective components is given. Note that power and GND connections are typically not shown in this image.

![Capra system](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/CapraPCBprinciple.jpg)

#### Cam Multiplexer
The Cam Muliplexer is a 30x70mm board directly placed on top of the RPi. While the RPi is typically only capable of connecting to a single camera the _'Cam Multiplexer V4'_ enables the RPi to switch between cameras and take pictures. The CamMultiplexer also contains a MPL3115A2 Altimeter that allows the RPi to sense the altitude of the Collector. Lastly, there is a DS3231 Real Time Clock on the board that allows the RPi to keep its internal clock synchronised. The DS3231 which will continue to run even when the RPi is off (or even runs out of battery) because it is connected to a small CR1220 Coincell battery. This battery will slowly drain, but will keep the collector running for several years!

The flat cables (called 'FFC' - Flat Flexible Cable) contain all signals that travel between the cameras and the RPi. These signals can be categorised in two protocols:

| Protocol   | Function   | Through |
| ---------- | ---------- | ------- |
| [I2C](https://en.wikipedia.org/wiki/I%C2%B2C)        | RPI issue commands to the camera. | VideoCore (GPU) of RPi and Camera through Analog Multiplexer 74HC4051 |
| [MIPI](https://mipi.org/specifications/d-phy)       | Contains all the data that comprise the image taken by the camera. | VideoCore (GPU) of RPi and Camera through (one or both) FSA642UMX |

The table above echoes the systematic drawing in that it shows the signals between the RPi and the cameras being split up and switched via two different chips; this is due to the vastly different electronic requirements of those signals.

Note that the I2C meant in the context of the cameras is NOT easily directly programmable. The I2C bus that runs between the cameras and the RPi is called I2C-0. I2C-0 is controlled by the 'GPU' of the RPi (also referred to as the VideoCore). The 'regular' I2C bus (BCM 2 & BCM3) is an entirely separate I2C bus and is controlled by the ARM processor on the RPi. The latter bus talks to the Altimeter and the RTC and is called I2C-1.

#### Buttonboard
This PCB is placed towards the lower end of the Capra enclosure; and is fixed against the back piece. A 7-cable ribbon connects the buttonboard with the Cam Multiplexer. The following components are on the buttonboard:
- On Button
- Off Button
- Pause button
- 2-colour indicator LED

![Button Board](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/Capra_Buttonboard.png)

The Buttonboard has a row of connections labelled `'To_Raspberry'`. These connections have individual names and should be routed as follows:

| ButtonBoard | Cam Multiplexer |
| ----------- | --------------- |
| GND         | GND             |
| LED_R       | LED             |
| LED_G       | LED2            |
| 3V3         | 3V3             |
| OFF         | OFF             |
| PAUSE       | PLAY            |
| SCL         | SCL             |


#### Batteries
Capra uses two 21700 LiPo batteries. More specifically, the batteries used are the Samsung 40T batteries. This specific battery was chosen because two such batteries placed in parallel fit the shape of Capra perfectly and because the 40T model packs an impressive 4000 mAh capacity. The name _21700_ refers to the diameter (21mm) and the height (70mm) of the battery - this is common naming convention with cylindrical LiPo batteries.
> Fun Fact: 21700 batteries were initially [developed for electric vehicles](https://electrek.co/2017/01/09/samsung-2170-battery-cell-tesla-panasonic/). However, their main use nowadays is to power e-cigarettes.

At an average draw of approximately 800mA @ 5V by the Capra system, the two batteries are able to power the system for an approximate 7,5 hours.

![Samsung 40T](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/40T.jpg)

LiPo batteries do require a specific circuit to regulate their charging. For Capra, I chose the Adafruit PowerBoost 1000. This module is able to provide the necessary 800mA to the RPi and has a load-sharing circuit. The load sharing circuit is what makes it possible to connect the Collector to a 5V USB power source (e.g. 5V powerbank, 5V wall outlet, etc.). Connecting such a power source will have the Collector run on that power AND charge the batteries while connected.

**NEVER ATTEMPT TO CHARGE THESE BATTERIES WITHOUT AN APPROPRIATE CIRCUIT OR MODULE.**

21700 batteries have poorly indicated '+' and '-' terminals. This is **_extremely_** important to remain aware of while inserting them into the battery holders. If inserted the wrong way around, the batteries will immediately short circuit, resulting in **melting wires** at best and **exploding batteries** at worst. This will also irreparably damage the PowerBoost module. To mitigate such mistakes, mark the '-' side of new batteries with tape or permanent marker. The '+' terminal is recognisable by a round indentation. The '-' terminal is entirely flat.

![Battery Marking](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/BatteryMarking.JPG)

The + terminal should be pointed upwards. The '-' terminal should be pointed down (towards the buttonboard). There is also a marking on the back piece that shows the orientation of the batteries:

![Battery Orientation](https://raw.githubusercontent.com/EverydayDesignStudio/guides/master/images/capra/BatteryOrientation.JPG)


#### LED Meanings
| LED   | Location   | Meaning |
| ----- |:----------:|--------:|
| 💚 solid/blinking  | Raspberry pi Zero | Raspberry pi is on  |
| 💚    | Capra PCB | Unassigned  |
| 🧡    | Capra PCB | Unassigned  |
| 💚 blinking   | Button board | collector.py is PAUSED  |
| 🔴 blinking    | Button board | program is running  |
| 🔵 solid | Adafruit Powerbooster | Adafruit Powerbooster has power |
| 💚 solid   | Adafruit Powerbooster | Batteries fully charged  |
| 🔴 solid   | Adafruit Powerbooster | Batteries low  |
| 🧡 solid   | Adafruit Powerbooster | Batteries charging  |

## Explorer (Projector unit)
The Explorers functionality is twofold:
- Providing storage for the photos from the Collector  
- Playing the photos back via its internal projector.

### File transfer
File transfer from the Collector to the Explorer is initiated when the Collector is physically placed over the Explorers controls. This is registered by the Explorer by a magnetometer that senses the magnetic field of a small magnet in the Collectors' housing.
At this point, the Explorer starts two parallel processes: the file transfer is initiated and a __transfer animation__ is started.

The transfer animation shows
