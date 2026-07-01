# YOSOY Calendar

A multi-calendar date generator that computes **26+ calendar systems** and **7 planetary hour systems** for any date. Output as pipe-delimited, JSON, or human-readable format.

## Installation

```bash
# Required
pip install convertdate

# Optional (for --astro and accurate --hours)
pip install skyfield
```

## Quick Start

```bash
# Today — unified default view (Alkhemia, Atlantean, Moon, planets, etc.)
python3 calendar_data_gen.py --today

# Planetary hours for today
python3 calendar_data_gen.py --today --hours

# All 7 planetary hour systems side by side
python3 calendar_data_gen.py --today --hours compare

# A specific system
python3 calendar_data_gen.py --today --hours vedic

# Full 26+ calendar systems
python3 calendar_data_gen.py --today --full

# Astrology mode (planetary positions, retrogrades, conjunctions)
python3 calendar_data_gen.py --today --astro

# JSON output
python3 calendar_data_gen.py --today --json

# Human-readable output
python3 calendar_data_gen.py --today -H

# Date range
python3 calendar_data_gen.py --start 2026-01-01 --end 2026-12-31

# Filter specific calendar systems
python3 calendar_data_gen.py --today --full --systems vedic,mayan,hebrew

# Custom location (for sunrise/sunset in --hours mode)
python3 calendar_data_gen.py --today --hours --lat 40.71 --lon -74.00 --tz -4
```

## Output Modes

| Mode | Flag | Description |
|------|------|-------------|
| **Unified** (default) | *(none)* | Alkhemia, Atlantean, Moon, Eclipse, 13-Moon, Celtic, 7-Day, Decan, Wavespell, 7 planets, Aspects, 9SK, Sexagenary, Gregorian, Flags |
| **Full** | `--full` | All 26+ calendar systems |
| **Main Cycles** | `--main-cycles` | 7-day, 10-day, 13-day, 12-month, 13-month, 28-day cycles + Moon |
| **Astrology** | `--astro` | Planetary zodiac signs, retrogrades, conjunctions |
| **Planetary Hours** | `--hours` | 7 planetary hour systems (see below) |

### Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Pipe-delimited | *(default)* | Compact, one line per day |
| Human-readable | `-H` / `--human` | Labeled multi-line blocks |
| JSON | `--json` | Structured JSON array |

## Planetary Hours (`--hours`)

Computes the 24 planetary hours of the day based on actual sunrise/sunset times. Supports **7 systems**:

| System | Flag | Description |
|--------|------|-------------|
| **Chaldean** | `--hours chaldean` | Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon, night continues cycle |
| **Vedic (Hora)** | `--hours vedic` | Sun→Venus→Mercury→Moon→Saturn→Jupiter→Mars, Jyotish tradition |
| **Al-Biruni** | `--hours al-biruni` | Same Chaldean order, but night **restarts** from day ruler |
| **Egyptian** | `--hours egyptian` | Hour ruler from 36-decan cycle, not 7-planet cycle |
| **Hellenistic** | `--hours hellenistic` | Day starts at sunset (Vettius Valens tradition) |
| **Tibetan** | `--hours tibetan` | Day ruler from current Nakshatra (lunar mansion) |
| **Ethiopian** | `--hours ethiopian` | Coptic epoch week cycle (Thoth 1 = Aug 29, 284 CE) |

```bash
# All 7 systems
python3 calendar_data_gen.py --today --hours

# Compact comparison table
python3 calendar_data_gen.py --today --hours compare

# Single system with custom location
python3 calendar_data_gen.py --today --hours tibetan --lat 27.98 --lon 86.93 --tz 5.75
```

Each hour shows: ordinal, start/end time, planet name, symbol, and activity recommendation (day/night specific).

## Calendar Systems

### Astronomical / Astrological

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **Zodiac** (tropical) | `Zod:` | Tropical zodiac sign, element, modality |
| **Vedic** (sidereal) | `Ved:` | Sidereal rashi, nakshatra, tithi, vara |
| **Moon Phase** | `Moon:` | Lunar phase and illumination percentage |
| **Moon Zodiac** | *(appended to Moon)* | Tropical zodiac sign of the Moon |
| **Decan** | `Dec:` | 36 Egyptian/Hellenistic decans with Chaldean + triplicity rulers |
| **Wavespell** | `Wav:` | Dreamspell 13-tone wavespell + Tzolkin trecena |
| **7-Day Planet** | `7D:` | Daily planetary ruler (Chaldean week) |
| **Astro Planets** | *(per planet)* | 7 planets with zodiac sign, degree, retrograde status |
| **Aspects** | `Asp:` | Conjunctions and retrogrades |

### Solar / Seasonal

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **Gregorian** | `Sunday/Sun` | Weekday + planetary ruler + date |
| **Seasons** | `Sea:` | Season based on solstices/equinoxes (north/south/both) |
| **Persian** (Solar Hijri) | `Per:` | Jalali calendar via convertdate |

### Lunar / Luni-Solar

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **13-Moon** (Dreamspell) | `13M:` | Mayan Dreamspell 13×28 + Day Out of Time |
| **Chinese Lunar** | `Chi:` | Chinese lunar calendar with leap months |
| **Hebrew** | `Heb:` | Hebrew luni-solar calendar via convertdate |
| **Islamic** (Hijri) | `Isl:` | Tabular Islamic calendar via convertdate |
| **Hindu** (Vikram Samvat) | `Hin:` | VS year + luni-solar month + Panchanga (paksha/tithi/nakshatra) |
| **Javanese** | `Jav:` | Anno Javanico + Pasaran 5-day cycle + Wetonan 35-day cycle |

### Mesoamerican

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **Mayan** | `May:` | Tzolkin (260-day) + Haab (365-day) via convertdate |
| **Aztec** | `Azt:` | Tonalpohualli (260-day) + Xiuhpohualli (365-day) |

### Esoteric / Cultural

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **Atlantean** | `Atl:` | 360-day calendar + Hol seasonal cycle |
| **Alkhemia** | `Alk:` | 13-day elemental cycles + eclipse detection |
| **Celtic Tree** | `Cel:` | Ogham tree calendar (13 months × 28 days) |
| **9 Star Ki** | `9SK:` | Flying Stars (Lo Shu square) |
| **Sexagenary** | `Sex:` | Chinese stems & branches |

### Ancient / National

| Calendar | Prefix | Description |
|----------|--------|-------------|
| **Ancient Egyptian** | `Eg:` | 365-day civil calendar (3 seasons + epagomenal days) |
| **Indian National Saka** | `SakI:` | Official Indian National Calendar (solar months) |
| **Balinese Saka** | `SakB:` | Pawukon 210-day cycle with 10 concurrent week systems |

## Flags

Special markers appended to each day's output:

- `DOT` — Day Out of Time (13-Moon calendar)
- `ECLIPSE:` — Solar/lunar eclipse (Alkhemia cycle)
- `HoliNada(...)` — Atlantean holiday markers

## Location

Default location: **Caraguatatuba, SP, Brazil** (23.62°S, 45.41°W, UTC-3).

Override with `--lat`, `--lon`, `--tz`:

```bash
python3 calendar_data_gen.py --today --hours --lat 51.50 --lon -0.12 --tz 0
```

## Dependencies

- **Required:** `convertdate` (Hebrew, Islamic, Mayan, Persian calendars)
- **Optional:** `skyfield` (accurate planetary positions, sunrise/sunset, moon phase)

Without Skyfield, astronomical functions fall back to mathematical approximations (good to ~2° for planets, ~2 min for sunrise).

## License

MIT
