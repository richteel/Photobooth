# 🛰️ Optimizing USB GPS Performance on Raspberry Pi

**Copilot Prompt**

I have a USB GPS dongle that does not have a battery. It must cold start each time power is applied. In Windows, using u-center, it appears to get a lock within 3 minutes. On the Raspberry Pi, it takes nearly one hour. I suspect u-center is configuring the GPS differently than Linux on the Raspberry Pi. I ran ubxtool on the Raspberry Pi to get the configuration. Any ideas if I'm on the right path that the configuration may be different and if so, what shall I try?

```bash
pi@PhotoBooth1:~ $ ubxtool -p CFG-GNSS --device /dev/ttyACM0
UBX-CFG-GNSS:
 msgVer 0  numTrkChHw 22 numTrkChUse 22 numConfigBlocks 4
  gnssId 0 TrkCh  4 maxTrCh 255 reserved 0 Flags x00000001
   GPS  enabled
  gnssId 1 TrkCh  1 maxTrCh  3 reserved 0 Flags x00000001
   SBAS  enabled
  gnssId 5 TrkCh  0 maxTrCh  3 reserved 0 Flags x00000001
   QZSS  enabled
  gnssId 6 TrkCh  8 maxTrCh 255 reserved 0 Flags x00000000
   GLONASS  

UBX-ACK-ACK:
  ACK to Class x06 (CFG) ID x3e (GNSS)

UBX-NAV-SOL:
  iTOW 148056000 fTOW 38774 week 2373 gpsFix 0 flags x5c
  ECEF X 108365965 Y -484244931 Z 399383262 pAcc 311812
  VECEF X 0 Y 0 Z 0 sAcc 1004
  pDOP 9999 reserved1 2 numSV 0 reserved2 119684

UBX-NAV-SVINFO:
 iTOW:148056000 numCh 12 globalFlags 3 reserved1 x0
  chn   3 svid   5 flags 0x0c quality 4 cno 28 elev  76 azim 332 prRes      0
  chn   4 svid   6 flags 0x04 quality 1 cno  0 elev   6 azim 105 prRes      0
  chn   8 svid   7 flags 0x04 quality 1 cno  0 elev   3 azim  54 prRes      0
  chn   6 svid  20 flags 0x04 quality 3 cno 14 elev  55 azim  44 prRes  -1686
  chn   1 svid  21 flags 0x04 quality 4 cno 19 elev  49 azim  46 prRes      0
  chn  11 svid  23 flags 0x04 quality 1 cno  0 elev   0 azim 244 prRes      0
  chn   9 svid  25 flags 0x04 quality 1 cno  0 elev  11 azim 239 prRes      0
  chn   0 svid  29 flags 0x0c quality 7 cno 32 elev  54 azim 298 prRes      0
  chn   5 svid  30 flags 0x04 quality 1 cno  0 elev   6 azim  85 prRes      0
  chn  10 svid 120 flags 0x10 quality 1 cno  0 elev  13 azim 109 prRes      0
  chn   2 svid 133 flags 0x10 quality 1 cno  0 elev  40 azim 211 prRes      0
  chn   7 svid 138 flags 0x10 quality 1 cno  0 elev  35 azim 222 prRes      0

UBX-NAV-DOP:
  iTOW 148056000 gDOP 9999 pDOP 9999 tDOP 9999 vDOP 9999
  hDOP 9999 nDOP 9999 eDOP 9999

UBX-NAV-TIMEGPS:
  iTOW 148056000 fTOW 38774 week 2373 leapS 16 valid x3 tAcc 3718

UBX-NAV-SOL:
  iTOW 148057000 fTOW 41095 week 2373 gpsFix 0 flags x5c
  ECEF X 108378317 Y -484248809 Z 399288575 pAcc 8732426
  VECEF X 0 Y 0 Z 0 sAcc 955
  pDOP 9999 reserved1 2 numSV 0 reserved2 119684

UBX-NAV-SVINFO:
 iTOW:148057000 numCh 12 globalFlags 3 reserved1 x0
  chn   3 svid   5 flags 0x0c quality 4 cno 28 elev  76 azim 332 prRes      0
  chn   4 svid   6 flags 0x04 quality 1 cno  0 elev   6 azim 105 prRes      0
  chn   8 svid   7 flags 0x04 quality 1 cno  0 elev   3 azim  54 prRes      0
  chn   6 svid  20 flags 0x04 quality 4 cno 14 elev  55 azim  44 prRes      0
  chn   1 svid  21 flags 0x04 quality 4 cno 19 elev  49 azim  46 prRes      0
  chn  11 svid  23 flags 0x04 quality 1 cno  0 elev   0 azim 244 prRes      0
  chn   9 svid  25 flags 0x04 quality 1 cno  0 elev  11 azim 239 prRes      0
  chn   0 svid  29 flags 0x0c quality 7 cno 32 elev  54 azim 298 prRes      0
  chn   5 svid  30 flags 0x04 quality 1 cno  0 elev   6 azim  85 prRes      0
  chn  10 svid 120 flags 0x10 quality 1 cno  0 elev  13 azim 109 prRes      0
  chn   2 svid 133 flags 0x10 quality 1 cno  0 elev  40 azim 211 prRes      0
  chn   7 svid 138 flags 0x10 quality 1 cno  0 elev  35 azim 222 prRes      0

UBX-NAV-DOP:
  iTOW 148057000 gDOP 9999 pDOP 9999 tDOP 9999 vDOP 9999
  hDOP 9999 nDOP 9999 eDOP 9999

UBX-NAV-TIMEGPS:
  iTOW 148057000 fTOW 41095 week 2373 leapS 16 valid x3 tAcc 220927

pi@PhotoBooth1:~ $ 
```



**Copilot Response**

You're absolutely on the right track, Richard. The stark difference in time-to-first-fix (TTFF) between u-center on Windows and your Raspberry Pi setup strongly suggests that **u-center is configuring the GPS module more optimally**—and those settings aren’t persisting across power cycles due to the lack of onboard battery.

Here’s a breakdown of what’s likely happening and what you can try:

---

🧠 Why the Pi Takes Longer

- **Cold Start Every Time**: Without battery-backed RAM, the GPS must reacquire almanac and ephemeris data from scratch.
- **u-center Advantage**: On Windows, u-center may be:

- Enabling more GNSS constellations (e.g., GLONASS, Galileo)
- Increasing the update rate
- Disabling unnecessary NMEA messages to reduce bandwidth
- Using AssistNow or aiding data (if internet-connected)

On the Pi, unless you explicitly configure these settings, the GPS likely defaults to a minimal configuration.

---

Your GPS dongle lacks a battery, so it cold starts every time. While u-center on Windows gets a fix quickly, the Raspberry Pi takes much longer. This guide outlines steps to align the Pi's configuration with what u-center likely applies automatically.

---

## 🔍 Observations from `ubxtool`

- **Only GPS, SBAS, and QZSS** are enabled. GLONASS is listed but not enabled (`Flags x00000000`).
	- **GLONASS is disabled**, which limits satellite visibility.
- **No fix and very high DOP values** (`pDOP 9999`), indicating poor satellite geometry or insufficient satellite data.
	- **No fix** is achieved (`gpsFix 0`), and **DOP values are maxed** (`9999`), indicating poor satellite geometry.
- **Some satellites have decent C/N0**, but not enough for a fix.

---

## 🛠️ What You Can Try / ✅ Recommendations

### 1. Enable More GNSS Constellations

Use `ubxtool` to enable GLONASS and possibly Galileo to improve satellite acquisition:

```bash
ubxtool -p CFG-GNSS,0,1,1,0,0 --device /dev/ttyACM0
```

Or use the full config block to enable multiple systems. You can also use `ubxtool -p MON-VER` to check protocol version and tailor commands accordingly.

### 2. Increase Update Rate

Set the GPS to update at 5Hz:

```bash
ubxtool -p CFG-RATE,200,1 --device /dev/ttyACM0
```

This sets the update rate to 5Hz (200ms interval).

### 3. Disable Unused NMEA Messages

Reducing NMEA chatter can help performance:

```bash
ubxtool -d NMEA --device /dev/ttyACM0
```

Then selectively re-enable only what you need.

### 4. Save Configuration to Flash

If your module supports it:

```bash
ubxtool -p CFG-CFG,0,1,0 --device /dev/ttyACM0
```


This saves current settings to non-volatile memory (if available).

### 5. Use u-center to Export Config

You can export the working config from u-center as a .cfg file and replay it on the Pi using `ubxtool` or `gpsctl`.

---

🧪 Bonus: Use `ser2net` to Connect u-center to the Pi
If you want to live-debug the Pi-connected GPS in u-center:

- Install `ser2net` on the Pi
- Forward `/dev/ttyACM0` to a TCP port
- Connect from u-center using Receiver → Network Connection

More on that [in this guide](https://ozzmaker.com/using-u-center-to-connect-to-a-raspberry-pi-with-an-attached-berrygps-imu-gsm/).

---

Want help crafting a script to apply these settings automatically at boot? Or maybe a one-liner to dump and compare configs between Windows and Pi?

