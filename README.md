# YOSOY Calendar

A multi-calendar date generator that computes **21 calendar systems** for any date, output as pipe-delimited data. Pure Python 3 standard library — no dependencies.

## Usage

```bash
# Today only (compact mode)
python3 calendar_data_gen.py --today

# Today only (all 21 calendar systems)
python3 calendar_data_gen.py --today --full

# Date range
python3 calendar_data_gen.py --start 2026-01-01 --end 2026-12-31

# Save to file
python3 calendar_data_gen.py --today --full -o calendar_output.txt

# Hemisphere (north/south/both, default: south)
python3 calendar_data_gen.py --today --hemisphere north
```

## Output Format

### Compact mode (7 systems)
```
Gregorian(Full/Planet date) | Atlantean(+Hol) | Zodiac | Season | 13Moon | Moon | Flags
```

### Full mode (`--full`, 21 systems)
```
Gregorian(Full/Planet date) | Atlantean(+Hol) | Zodiac | Season | 13Moon | Moon | 9SK | Sexagenary | Alkhemia | Vedic | ChineseLunar | Hebrew | Mayan | Celtic | Islamic | Aztec | Persian | Egyptian | Hindu | Javanese | SakaIndia | SakaBali | Flags
```

## Calendar Systems

### Astronomical / Astrological
| Calendar | Prefix | Description |
|---|---|---|
| **Zodiac** (tropical) | `Zod:` | Tropical zodiac sign, element, modality |
| **Vedic** (sidereal) | `Ved:` | Sidereal rashi, nakshatra, tithi, vara |
| **Moon Phase** | `Moon:` | Lunar phase and illumination percentage |

### Solar / Seasonal
| Calendar | Prefix | Description |
|---|---|---|
| **Gregorian** | `Sunday/Sun` | Weekday + planetary ruler + date |
| **Seasons** | `Sea:` | Season based on solstices/equinoxes |
| **Persian** (Solar Hijri) | `Per:` | Jalali calendar with 33-year intercalation |

### Lunar / Luni-Solar
| Calendar | Prefix | Description |
|---|---|---|
| **13-Moon** (Dreamspell) | `13M:` | Mayan Dreamspell 13×28 + Day Out of Time |
| **Chinese Lunar** | `Chi:` | Chinese lunar calendar with leap months |
| **Hebrew** | `Heb:` | Hebrew luni-solar calendar |
| **Islamic** (Hijri) | `Isl:` | Tabular Islamic calendar |
| **Hindu** (Vikram Samvat) | `Hin:` | VS year + luni-solar month + Panchanga (paksha/tithi/nakshatra) |
| **Javanese** | `Jav:` | Anno Javanico + Pasaran 5-day cycle + Wetonan 35-day cycle |

### Mesoamerican
| Calendar | Prefix | Description |
|---|---|---|
| **Mayan** | `May:` | Tzolkin (260-day) + Haab (365-day) |
| **Aztec** | `Azt:` | Tonalpohualli (260-day) + Xiuhpohualli (365-day) |

### Esoteric / Cultural
| Calendar | Prefix | Description |
|---|---|---|
| **Atlantean** | `Atl:` | 360-day calendar + Hol seasonal cycle |
| **Alkhemia** | `Alk:` | 13-day elemental cycles + eclipse detection |
| **Celtic Tree** | `Cel:` | Ogham tree calendar |
| **9 Star Ki** | `9SK:` | Flying Stars (Lo Shu square) |
| **Sexagenary** | `Sex:` | Chinese stems & branches |

### Ancient / National
| Calendar | Prefix | Description |
|---|---|---|
| **Ancient Egyptian** | `Eg:` | 365-day civil calendar (3 seasons + epagomenal days) |
| **Indian National Saka** | `SakI:` | Official Indian National Calendar (solar months) |
| **Balinese Saka** | `SakB:` | Pawukon 210-day cycle with 10 concurrent week systems |

## Flags

Special markers appended to each day's output:
- `DOT` — Day Out of Time (13-Moon calendar)
- `ECLIPSE:` — Solar/lunar eclipse (Alkhemia cycle)
- Nada/Holi — Atlantean holiday markers

## License

MIT