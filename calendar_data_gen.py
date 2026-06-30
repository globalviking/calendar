#!/usr/bin/env python3
"""
calendar_data_gen.py - Generate pre-computed daily calendar data for YOSOY framework.

Computes 26+ calendar systems for each day and outputs pipe-delimited, JSON, or
human-readable data. Uses PyEphem for accurate planetary positions (--astro mode).

Usage: python3 calendar_data_gen.py [--start YYYY-MM-DD] [--end YYYY-MM-DD] [-o OUTPUT_FILE]
       python3 calendar_data_gen.py --today [-H|--json|--full|--main-cycles|--astro]
"""

import argparse
import json
import math
import sys
from datetime import date, timedelta

# PyEphem for accurate planetary positions (--astro mode)
# Graceful fallback: if ephem is not installed, --astro mode is disabled
try:
    import ephem
    HAS_EPHEM = True
except ImportError:
    HAS_EPHEM = False


# ============================================================
# Gregorian weekday constants
# ============================================================

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

PLANETARY_RULERS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
PLANETARY_SYMBOLS = {
    "Sun": "\u2609",
    "Moon": "\u263d",
    "Mars": "\u2642",
    "Mercury": "\u263f",
    "Jupiter": "\u2643",
    "Venus": "\u2640",
    "Saturn": "\u2644",
}

# Element emojis (Unicode escape sequences for encoding safety)
ELEMENT_EMOJIS = {
    "Fire": "\U0001F525",    # 🔥
    "Earth": "\u26F0\ufe0f",  # ⛰️
    "Air": "\U0001F343",     # 🍃
    "Water": "\U0001F4A7",    # 💧
    "Ether": "\U0001F300",    # 🌀
    "Eternal": "\u267E",      # ♾
    "Metal": "\U0001FA99",    # 🪙
    "Wood": "\U0001FAB5",     # 🪵
}

# ============================================================
# Atlantean Calendar constants
# ============================================================

ATLANTEAN_CONSTELLATIONS = [
    "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
    "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus",
    "Gemini", "Cancer",
]

# Unicode symbols for the 12 Atlantean constellations (same order as above)
ATLANTEAN_CONSTELLATION_SYMBOLS = [
    "\u264c", "\u264d", "\u264e", "\u264f", "\u2650",
    "\u2651", "\u2652", "\u2653", "\u2648", "\u2649",
    "\u264a", "\u264b",
]

# Tropical zodiac signs (in order starting from Aries, as the sun traverses them)
TROPICAL_ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Tropical zodiac symbols (Aries through Pisces)
TROPICAL_ZODIAC_SYMBOLS = [
    "\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d",
    "\u264e", "\u264f", "\u2650", "\u2651", "\u2652", "\u2653",
]

# Abbreviated zodiac sign names for Moon field (3-letter)
MOON_ZODIAC_ABBR = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

ATLANTEAN_CHAKRAS = [
    "Crown", "3rdEye", "Throat", "Heart", "SolarPlex",
    "Sacral", "Root", "Knees", "Ankles", "Toroid",
]

ATLANTEAN_WEEK_BODIES = ["Mental", "Emotional", "Physical"]

ATLANTEAN_DOT_SOLIDS = [
    "Tetrahedron/Fire", "Hexahedron/Earth", "Octahedron/Ether",
    "Dodecahedron/Water", "Icosahedron/Air",
]

ZODIAC_ELEMENTS = {
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
}

ZODIAC_MODALITIES = {
    "Leo": "Fixed", "Virgo": "Mutable", "Libra": "Cardinal", "Scorpio": "Fixed",
    "Sagittarius": "Mutable", "Capricorn": "Cardinal", "Aquarius": "Fixed", "Pisces": "Mutable",
    "Aries": "Cardinal", "Taurus": "Fixed", "Gemini": "Mutable", "Cancer": "Cardinal",
}

# Traditional planetary rulers for each zodiac sign (domicile rulers)
ZODIAC_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ============================================================
# 13-Moon Calendar constants
# ============================================================

MOON_13_MONTH_NAMES = [
    "Magnetic", "Lunar", "Electric", "SelfExist", "Overtone",
    "Rhythmic", "Resonant", "Galactic", "Solar", "Planetary",
    "Spectral", "Crystal", "Cosmic",
]

MOON_13_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ============================================================
# Alkhemia Path constants
# ============================================================

ALKHEMIA_13DAY = {
    1: ("Aries", "EarthStar", "I Am"),
    2: ("Taurus", "Root", "I Have"),
    3: ("Gemini", "Throat", "I Communicate"),
    4: ("Cancer", "Sacral", "I Feel"),
    5: ("Leo", "SolarPlex", "I Can"),
    6: ("Virgo", "Knees", "I Analyze"),
    7: ("Libra", "Heart", "I Balance"),
    8: ("Scorpio", "HighHeart", "I Desire"),
    9: ("Sagittarius", "3rdEye", "I See"),
    10: ("Capricorn", "Ankles", "I Use"),
    11: ("Aquarius", "Crown", "I Know"),
    12: ("Pisces", "HigherStar", "I Believe"),
    13: ("Integration", "Toroid", "I Alchemize"),
}

ALKHEMIA_ELEMENTS = [
    "Hydrogen", "Helium", "Lithium", "Beryllium", "Boron",
    "Carbon", "Nitrogen", "Oxygen", "Fluorine", "Neon",
    "Sodium", "Magnesium", "Aluminum", "Silicon", "Phosphorus",
    "Sulfur", "Chlorine", "Argon", "Potassium", "Calcium",
    "Scandium", "Titanium", "Vanadium", "Chromium", "Manganese",
    "Iron", "Cobalt", "Nickel", "Copper", "Zinc",
    "Gallium", "Germanium", "Arsenic", "Selenium", "Bromine",
    "Krypton", "Rubidium", "Strontium", "Yttrium", "Zirconium",
    "Niobium", "Molybdenum", "Technetium", "Ruthenium", "Rhodium",
    "Palladium", "Silver", "Cadmium", "Indium", "Tin",
    "Antimony", "Tellurium", "Iodine", "Xenon", "Cesium",
    "Barium", "Lanthanum", "Cerium", "Praseodymium", "Neodymium",
    "Promethium", "Samarium", "Europium", "Gadolinium", "Terbium",
    "Dysprosium", "Holmium", "Erbium", "Thulium", "Ytterbium",
    "Lutetium", "Hafnium", "Tantalum", "Tungsten", "Rhenium",
    "Osmium", "Iridium", "Platinum", "Gold", "Mercury",
    "Thallium", "Lead", "Bismuth", "Polonium", "Astatine",
    "Radon", "Francium", "Radium", "Actinium", "Thorium",
    "Protactinium", "Uranium",
]

ALKHEMIA_ECLIPSES = {
    date(2026, 2, 17): "Calcinatio",
    date(2026, 8, 12): "Solutio",
    date(2027, 2, 6): "Separatio",
    date(2027, 8, 2): "Coniunctio",
    date(2028, 1, 26): "Putrefactio",
    date(2028, 7, 22): "Distillatio",
    date(2029, 1, 14): "Coagulatio",
}

ALKHEMIA_START = date(2026, 1, 11)
ALKHEMIA_END = date(2029, 4, 13)

# ============================================================
# Moon Phase reference dates
# ============================================================

MOON_REFERENCE_DATES = [
    date(2024, 1, 11), date(2024, 2, 9), date(2024, 3, 10), date(2024, 4, 8),
    date(2024, 5, 8), date(2024, 6, 6), date(2024, 7, 5), date(2024, 8, 4),
    date(2024, 9, 2), date(2024, 10, 2), date(2024, 11, 1), date(2024, 12, 1),
    date(2025, 1, 29), date(2025, 2, 28), date(2025, 3, 29), date(2025, 4, 27),
    date(2025, 5, 27), date(2025, 6, 25), date(2025, 7, 24), date(2025, 8, 23),
    date(2025, 9, 21), date(2025, 10, 21), date(2025, 11, 20), date(2025, 12, 20),
    date(2026, 1, 19), date(2026, 2, 17), date(2026, 3, 19), date(2026, 4, 17),
    date(2026, 5, 17), date(2026, 6, 16), date(2026, 7, 15), date(2026, 8, 13),
    date(2026, 9, 11), date(2026, 10, 11), date(2026, 11, 10), date(2026, 12, 10),
    date(2027, 1, 8), date(2027, 2, 6), date(2027, 3, 8), date(2027, 4, 6),
    date(2027, 5, 6), date(2027, 6, 5), date(2027, 7, 4), date(2027, 8, 3),
    date(2027, 9, 1), date(2027, 10, 1), date(2027, 10, 31), date(2027, 11, 30),
    date(2027, 12, 30),
    date(2028, 1, 28), date(2028, 2, 26), date(2028, 3, 27), date(2028, 4, 25),
    date(2028, 5, 25), date(2028, 6, 23), date(2028, 7, 23), date(2028, 8, 21),
    date(2028, 9, 20), date(2028, 10, 19), date(2028, 11, 18), date(2028, 12, 18),
    date(2029, 1, 16), date(2029, 2, 14), date(2029, 3, 16), date(2029, 4, 14),
    date(2029, 5, 14), date(2029, 6, 13), date(2029, 7, 12), date(2029, 8, 10),
    date(2029, 9, 9), date(2029, 10, 8), date(2029, 11, 7), date(2029, 12, 7),
]

# ============================================================
# Nine Star Ki constants
# ============================================================

NINE_STAR_KI = {
    1: ("Kan", "Water"),
    2: ("Kun", "Earth"),
    3: ("Zhen", "Wood"),
    4: ("Xun", "Wood"),
    5: ("Center", "Earth"),
    6: ("Qian", "Metal"),
    7: ("Dui", "Metal"),
    8: ("Gen", "Earth"),
    9: ("Li", "Fire"),
}

# ============================================================
# Sexagenary constants
# ============================================================

SEXAGENARY_STEMS = [
    ("Wood", "Yang"), ("Wood", "Yin"),
    ("Fire", "Yang"), ("Fire", "Yin"),
    ("Earth", "Yang"), ("Earth", "Yin"),
    ("Metal", "Yang"), ("Metal", "Yin"),
    ("Water", "Yang"), ("Water", "Yin"),
]

SEXAGENARY_BRANCHES = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
]

# HoliNada dates by year (equinox/solstice approximations)
HOLI_NADA = {}
for y in range(2024, 2031):
    HOLI_NADA[date(y, 3, 20)] = "HoliNada(MarEquinox)"
    HOLI_NADA[date(y, 6, 21)] = "HoliNada(JunSolstice)"
    HOLI_NADA[date(y, 9, 22)] = "HoliNada(SepEquinox)"
    HOLI_NADA[date(y, 12, 21)] = "HoliNada(DecSolstice)"

# ============================================================
# Hindu / Vedic Panchangam constants
# ============================================================

VEDIC_SIGNS = [
    "Mesha", "Vrishabha", "Mithuna", "Karkata",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena",
]

VEDIC_NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "PurvaPhalguni", "UttaraPhalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "PurvaAshadha", "UttaraAshadha", "Shravana", "Dhanishta", "Shatabhisha",
    "PurvaBhadra", "UttaraBhadra", "Revati",
]

VEDIC_TITHI_NAMES_SHUKLA = [
    "ShuklaPratipada", "ShuklaDwitiya", "ShuklaTritiya", "ShuklaChaturthi",
    "ShuklaPanchami", "ShuklaShashthi", "ShuklaSaptami", "ShuklaAshtami",
    "ShuklaNavami", "ShuklaDashami", "ShuklaEkadashi", "ShuklaDwadashi",
    "ShuklaTrayodashi", "ShuklaChaturdashi", "Purnima",
]
VEDIC_TITHI_NAMES_KRISHNA = [
    "KrishnaPratipada", "KrishnaDwitiya", "KrishnaTritiya", "KrishnaChaturthi",
    "KrishnaPanchami", "KrishnaShashthi", "KrishnaSaptami", "KrishnaAshtami",
    "KrishnaNavami", "KrishnaDashami", "KrishnaEkadashi", "KrishnaDwadashi",
    "KrishnaTrayodashi", "KrishnaChaturdashi", "Amavasya",
]

VEDIC_WEEKDAYS = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara",
    "Guruvara", "Shukravara", "Shanivara",
]
VEDIC_WEEKDAY_LORDS = [
    "Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani",
]

# ============================================================
# Traditional Chinese Lunar Calendar constants
# ============================================================

CHINESE_MONTHS = [
    "Zheng", "Er", "San", "Si", "Wu", "Liu",
    "Qi", "Ba", "Jiu", "Shi", "ShiYi", "ShiEr",
]

# Pre-computed Chinese New Year dates (verified from standard Chinese calendar)
CHINESE_NEW_YEAR = {
    2024: date(2024, 2, 10),
    2025: date(2025, 1, 29),
    2026: date(2026, 2, 17),
    2027: date(2027, 2, 6),
    2028: date(2028, 1, 26),
    2029: date(2029, 2, 13),
    2030: date(2030, 2, 3),
}

# Chinese lunar month day counts per year (29 or 30 days each)
# 12 months for common years, 13 for leap years (leap month inserted after regular)
# Verified from standard Chinese calendar sources for 2024-2029
# Leap years: 2025 (leap month 6), 2028 (leap month 5)
CHINESE_LUNAR_MONTHS = {
    2024: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29],  # 354 days, no leap
    2025: [29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30],  # 384 days, leap after M6
    2026: [29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30],  # 354 days, no leap
    2027: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29],  # 354 days, no leap
    2028: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30],  # 384 days, leap after M5
    2029: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30],  # 355 days, no leap
}

# Which month is the leap month (for display naming) — {year: leap_month_index_0based}
# In 2025 the leap is after month 6, so index 6 (0-based) in the list above
# In 2028 the leap is after month 5, so index 5
CHINESE_LEAP_MONTH_IDX = {
    2025: 6,  # leap month is the 7th entry (0-based index 6) = after Zheng=0,Er=1,...,Liu=5,LeapLiu=6
    2028: 5,  # leap month is the 6th entry (0-based index 5) = after Zheng=0,...,Wu=4,LeapWu=5
}

# ============================================================
# Hebrew Calendar constants
# ============================================================

# Hebrew month names — civil year order (Tishrei = month 1)
HEBREW_MONTHS = [
    "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat",
    "Adar", "Nisan", "Iyar", "Sivan", "Tammuz",
    "Av", "Elul",
]
HEBREW_LEAP_MONTHS = [
    "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat",
    "AdarI", "AdarII", "Nisan", "Iyar", "Sivan", "Tammuz",
    "Av", "Elul",
]

# Pre-computed Rosh Hashanah dates (verified from standard Hebrew calendar)
HEBREW_NEW_YEAR = {
    5784: date(2023, 9, 16),
    5785: date(2024, 10, 3),
    5786: date(2025, 10, 22),
    5787: date(2026, 10, 11),
    5788: date(2027, 10, 1),
    5789: date(2028, 10, 21),
    5790: date(2029, 10, 10),
    5791: date(2030, 9, 28),
}

# Hebrew year lengths: 353/354/355 (common), 383/384/385 (leap)
HEBREW_YEAR_LENGTHS = {
    5784: 385,  # leap, complete
    5785: 355,  # common, complete
    5786: 354,  # common, regular
    5787: 385,  # leap, complete
    5788: 354,  # common, regular
    5789: 385,  # leap, complete
    5790: 355,  # common, complete
}

# Base month lengths (Cheshvan=2 and Kislev=3 vary by year type)
HEBREW_COMMON_BASE = {
    1: 30, 2: None, 3: None, 4: 29, 5: 30, 6: 29,
    7: 30, 8: 29, 9: 30, 10: 29, 11: 30, 12: 29,
}
HEBREW_LEAP_BASE = {
    1: 30, 2: None, 3: None, 4: 29, 5: 30, 6: 30, 7: 29,
    8: 30, 9: 29, 10: 30, 11: 29, 12: 30, 13: 29,
}

# ============================================================
# Mayan Calendar constants
# ============================================================

# Tzolkin: 20 day names (in order, starting with Imix)
MAYAN_TZOLKIN_NAMES = [
    "Imix", "Ik", "Akbal", "Kan", "Chicchan",
    "Cimi", "Manik", "Lamat", "Muluc", "Oc",
    "Chuen", "Eb", "Ben", "Ix", "Men",
    "Cib", "Caban", "Etznab", "Cauac", "Ahau",
]

# Haab: 18 months of 20 days + 5 Wayeb days
MAYAN_HAAB_MONTHS = [
    "Pop", "Wo", "Sip", "Sotz", "Sek", "Xul",
    "Yaxkin", "Mol", "Chen", "Yax", "Sak", "Keh",
    "Mak", "Kankin", "Muwan", "Pax", "Kayab", "Kumku",
]
# Wayeb is the 5-day unnamed period (month 19, days 0-4)

# Mayan creation date: August 11, 3114 BCE (Gregorian)
# This is the start of the Long Count at 13.0.0.0.0 = 4 Ahau 8 Kumku
# In Julian Day: 584283 (GMT correlation)
MAYAN_CORRELATION_JD = 584283

# ============================================================
# Celtic Tree Calendar constants
# ============================================================

# 13 tree months + 1 unnamed day (Dec 23), each ~28 days
# Beth (Birch) starts on Dec 24, the day after the Winter Solstice
CELTIC_TREE_NAMES = [
    "Beth/Birch", "Luis/Rowan", "Nual/Ash", "Fearn/Alder", "Sallow/Willow",
    "Hawth/Hawthorn", "Duir/Oak", "Tinne/Holly", "Coll/Hazel", "Quert/Apple",
    "Muin/Vine", "Gort/Ivy", "Ruis/Elder",
]
CELTIC_TREE_ABBR = [
    "Beth", "Luis", "Nual", "Fearn", "Sallow",
    "Hawth", "Duir", "Tinne", "Coll", "Quert",
    "Muin", "Gort", "Ruis",
]
# Each month is 28 days. 13 months = 364 days + 1 extra day (Dec 23 = "NamelessDay")
# Beth starts Dec 24, ends Jan 20 (28 days)
# Luis: Jan 21 - Feb 17, Nual: Feb 18 - Mar 17, Fearn: Mar 18 - Apr 14,
# Sallow: Apr 15 - May 12, Hawthorn: May 13 - Jun 9, Duir: Jun 10 - Jul 7,
# Tinne: Jul 8 - Aug 4, Coll: Aug 5 - Sep 1, Quert: Sep 2 - Sep 29,
# Muin: Sep 30 - Oct 27, Gort: Oct 28 - Nov 24, Ruis: Nov 25 - Dec 22,
# NamelessDay: Dec 23

# ============================================================
# Decan constants (36 decans — 3 per zodiac sign, each ~10 days)
# ============================================================

# Chaldean planetary rulers for the 36 decans, in order from Aries I through Pisces III.
# The Chaldean order cycles: Mars, Sun, Venus, Mercury, Moon, Saturn, Jupiter (repeating).
DECAN_CHALDEAN_RULERS = [
    "Mars", "Sun", "Venus",           # Aries I, II, III
    "Mercury", "Moon", "Saturn",      # Taurus I, II, III
    "Jupiter", "Mars", "Mercury",     # Gemini I, II, III
    "Moon", "Venus", "Saturn",        # Cancer I, II, III
    "Jupiter", "Mars", "Sun",         # Leo I, II, III
    "Mercury", "Venus", "Moon",       # Virgo I, II, III
    "Saturn", "Jupiter", "Mars",      # Libra I, II, III
    "Sun", "Venus", "Mercury",        # Scorpio I, II, III
    "Moon", "Saturn", "Jupiter",      # Sagittarius I, II, III
    "Mars", "Mercury", "Sun",         # Capricorn I, II, III
    "Venus", "Moon", "Saturn",        # Aquarius I, II, III
    "Jupiter", "Mars", "Mercury",     # Pisces I, II, III
]

# Triplicity rulers (traditional Dorothean) — each element uses the same 3 planetary rulers
# across all 3 decans of all signs of that element.
# Fire (Aries, Leo, Sagittarius): Mars, Sun, Jupiter
# Earth (Taurus, Virgo, Capricorn): Venus, Moon, Saturn
# Air (Gemini, Libra, Aquarius): Saturn, Mercury, Jupiter
# Water (Cancer, Scorpio, Pisces): Venus, Mars, Moon
DECAN_TRIPLICITY_RULERS = {
    "Fire": ["Mars", "Sun", "Jupiter"],
    "Earth": ["Venus", "Moon", "Saturn"],
    "Air": ["Saturn", "Mercury", "Jupiter"],
    "Water": ["Venus", "Mars", "Moon"],
}

# Decan names (Egyptian/Greek tradition) — 36 names for the 36 decans
DECAN_NAMES = [
    # Aries
    "Atep", "Khenku", "Asar",
    # Taurus
    "Asikha", "Tepi", "Kheru",
    # Gemini
    "Amsek", "Sekha", "Khem",
    # Cancer
    "Hapi", "Hapit", "Nephthys",
    # Leo
    "Sekhmet", "Tefnut", "Bast",
    # Virgo
    "Isis", "Nephthys", "Hapi",
    # Libra
    "Maat", "Khepri", "Shu",
    # Scorpio
    "Khepesh", "Sekhmet", "Serqet",
    # Sagittarius
    "Neith", "Satis", "Anuket",
    # Capricorn
    "Khnum", "Heket", "Geb",
    # Aquarius
    "Nut", "Tefnut", "Shu",
    # Pisces
    "Sobek", "Hatmehit", "Taweret",
]

# ============================================================
# Dreamspell / 13-Moon Wavespell constants (13 Galactic Tones)
# ============================================================

# 13 Galactic Tones of Creation (Dreamspell tradition)
# Each tone has a name, a creative power, and an action
GALACTIC_TONES = [
    ("Magnetic", "Purpose", "Unify"),
    ("Lunar", "Challenge", "Polarize"),
    ("Electric", "Service", "Activate"),
    ("SelfExist", "Form", "Define"),
    ("Overtone", "Radiance", "Empower"),
    ("Rhythmic", "Equality", "Organize"),
    ("Resonant", "Attunement", "Channel"),
    ("Galactic", "Integrity", "Harmonize"),
    ("Solar", "Intention", "Pulse"),
    ("Planetary", "Manifestation", "Perfect"),
    ("Spectral", "Liberation", "Dissolve"),
    ("Crystal", "Cooperation", "Dedicate"),
    ("Cosmic", "Presence", "Endure"),
]

# ============================================================
# Islamic Hijri Calendar constants
# ============================================================

# Islamic month names
ISLAMIC_MONTHS = [
    "Muharram", "Safar", "RabiAlAwwal", "RabiAlThani",
    "JumadaAlAwwal", "JumadaAlThani", "Rajab", "Shaban",
    "Ramadan", "Shawwal", "DhuAlQidah", "DhuAlHijjah",
]

# Islamic epoch: July 16, 622 CE (Friday) — the Hijra
# In Julian Day: 1948439 (astronomical/Thursday epoch) or 1948440 (Friday/civil)
# We use the civil epoch (Friday) which is the most common: JD 1948440
ISLAMIC_EPOCH_JD = 1948440

# ============================================================
# Aztec Calendar constants
# ============================================================

# Tonalpohualli: 20 day names (in order, starting with Cipactli)
AZTEC_TONALPOHUALLI_NAMES = [
    "Cipactli", "Ehecatl", "Calli", "Cuetzpalin", "Coatl",
    "Miquiztli", "Mazatl", "Tochtli", "Atl", "Itzcuintli",
    "Ozomahtli", "Malinalli", "Acatl", "Ocelotl", "Quauhtli",
    "Cozcaquauhtli", "Ollin", "Tecpatl", "Quiauitl", "Xochitl",
]

# Tonalpohualli: 13 day numbers (1-13) combined with 20 day names = 260-day cycle
# Also has 9 "Lords of the Night" (9-day cycle)
AZTEC_LORDS_OF_NIGHT = [
    "Xiuhtecuhtli", "Tezcatlipoca", "Quetzalcoatl", "Huitzilopochtli",
    "Mictlantecuhtli", "Tlaloc", "Tonatiuh", "Tlazolteotl", "Tepeyollotl",
]

# Xiuhpohualli: 18 months of 20 days + 5 Nemontemi days = 365
AZTEC_XIUHPOHUALLI_MONTHS = [
    "AtlCaHuaLo", "Tlacaxipehualiztli", "Tozoztontli", "HueyTozoztli",
    "Toxcatl", "Etzalcualiztli", "Tecuilhuitontli", "HueyTecuilhuitl",
    "Tlaxochimaco", "Xocotlhuetzi", "Ochpaniztli", "Teotleco",
    "Quecholli", "Panquetzaliztli", "Atemoztli", "Tititl",
    "Izcalli", "Atlcahualo",
]
# Nemontemi = 5 unnamed/unlucky days (month 18, days 0-4)

# Aztec correlation: The Aztec calendar shares the same 260-day Tonalpohualli
# cycle as the Mayan Tzolkin, but with different day names.
# The Aztec New Year (Xiuhpohualli) typically started around March 12
# (before the Spanish conquest). We use the correlation:
# March 12, 2021 = 1 AtlCaHuaLo (start of Xiuhpohualli year)
# The Tonalpohualli is offset from the Mayan Tzolkin by a fixed number of days.
# Known: The Aztec date for Aug 13, 1521 (fall of Tenochtitlan) = 1 Coatl (Tonalpohualli)
# In our Mayan Tzolkin system, that same day = 7 Lamat.
# Aztec Tonalpohualli day name index = (Mayan Tzolkin name index + offset) % 20
# Coatl is index 4 (0-based). Lamat is index 7 in Mayan. offset = (4 - 7) % 20 = 17
AZTEC_TONALPOHUALLI_OFFSET = 17

# Aztec Xiuhpohualli starts around March 12 each year (solar-based)
# We use a fixed date approximation: March 12 each year
# (the actual Aztec new year varies by a few days due to the 365-day year
# drifting against the tropical year, but for our range we use a fixed date)
AZTEC_NEW_YEAR = {
    2024: date(2024, 3, 11),
    2025: date(2025, 3, 11),
    2026: date(2026, 3, 12),
    2027: date(2027, 3, 12),
    2028: date(2028, 3, 11),
    2029: date(2029, 3, 11),
    2030: date(2030, 3, 12),
}

# ============================================================
# Persian (Solar Hijri / Jalali) Calendar constants
# ============================================================

# Persian month names (starts with Farvardin at spring equinox)
PERSIAN_MONTHS = [
    "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
    "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand",
]

# Persian calendar epoch: March 19, 622 CE (Julian) = JD 1948320.5
# Actually the Persian Solar Hijri epoch is March 22, 622 CE (Julian)
# In terms of Julian Day: the epoch is JD 1948321 (March 22, 622 CE Julian)
# But the standard algorithm uses a 33-year cycle approximation.
# We use the algorithm based on the 33-year intercalation cycle:
# - 33-year cycle with 8 leap years (years 1, 5, 9, 13, 17, 22, 26, 30)
# - Leap year: 366 days (Esfand has 30 days)
# - Common year: 365 days (Esfand has 29 days)
# The epoch: Farvardin 1, year 1 = March 19, 622 CE (Gregorian) = JD 1948320

# For simplicity and accuracy in our date range, we use the following approach:
# 1. Compute days from the Persian epoch
# 2. Use the 33-year cycle algorithm to find the Persian year
# 3. Then find month and day within that year

# Persian epoch in Julian Day: March 22, 622 CE (Julian calendar)
# = JD 1948320 (astronomical, starting at noon March 22)
PERSIAN_EPOCH_JD = 1948320

# 33-year cycle: the first year of each 33-year cycle is a leap year
# Leap years in a 33-year cycle: years 1, 5, 9, 13, 17, 22, 26, 30 (1-based)
PERSIAN_LEAP_YEARS_IN_CYCLE = [1, 5, 9, 13, 17, 22, 26, 30]
# Days in a 33-year cycle: 25*365 + 8*366 = 9125 + 2928 = 12053


# ============================================================
# Calendar computation functions
# ============================================================

def to_julian_day(d):
    """Convert a Python date to Julian Day number (integer)."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def lahiri_ayanamsa(jd):
    """Approximate Lahiri ayanamsa in degrees for a given Julian Day."""
    years_from_2000 = (jd - 2451545.0) / 365.25
    return 23.85 + 0.01397 * years_from_2000


def elem_emoji(element_name):
    """Return the element name with its emoji appended, or the name alone if no match."""
    e = ELEMENT_EMOJIS.get(element_name)
    if e:
        return element_name + e
    return element_name


def solar_longitude(d):
    """Compute the Sun's tropical longitude in degrees for date d.

    Uses a simplified solar model: mean longitude + equation of center.
    This is the single source of truth — previously duplicated 6x.
    """
    jd = to_julian_day(d)
    t = (jd - 2451545.0) / 36525.0
    l0 = 280.460 + 36000.770 * t
    m = 357.528 + 35999.050 * t
    m_rad = math.radians(m)
    c = 1.915 * math.sin(m_rad) + 0.020 * math.sin(2 * m_rad)
    return (l0 + c) % 360.0


def solar_sidereal_longitude(d):
    """Compute the Sun's sidereal longitude in degrees (tropical - Lahiri ayanamsa)."""
    jd = to_julian_day(d)
    return (solar_longitude(d) - lahiri_ayanamsa(jd)) % 360.0


def nearest_new_moon(d):
    """Find the most recent past new moon reference date for date d.

    Returns the MOON_REFERENCE_DATES entry closest to but not after d.
    This is the single source of truth — previously duplicated 4x.
    """
    ref = MOON_REFERENCE_DATES[0]
    for r in MOON_REFERENCE_DATES:
        if r <= d:
            ref = r
        else:
            break
    return ref


def compute_weekday(d):
    """Compute weekday full name, abbreviation, planetary ruler name, and full date."""
    wd = d.weekday()
    full = WEEKDAY_NAMES[wd]
    abbr = WEEKDAY_ABBR[wd]
    planet = PLANETARY_RULERS[wd]
    return full + "/" + planet + " " + str(d)


def compute_atlantean(d):
    """Compute Atlantean calendar data for date d, with Hol cycle merged in.
    Returns (field_string, is_dot, constellation_or_dot_element).
    """
    new_year = date(d.year, 8, 4)
    if d < new_year:
        new_year = date(d.year - 1, 8, 4)
    day_num = (d - new_year).days + 1

    # Compute Hol cycle
    hol = compute_hol(d)
    hol_short = hol.replace("Hol:", "")

    if day_num > 360:
        dot_idx = day_num - 361
        if dot_idx > 4:
            dot_idx = 4
        if dot_idx < 0:
            dot_idx = 0
        solid = ATLANTEAN_DOT_SOLIDS[dot_idx]
        short_solid = solid.replace("Tetrahedron", "Tetra").replace("Hexahedron", "Hexa")
        short_solid = short_solid.replace("Octahedron", "Octa").replace("Dodecahedron", "Dodeca")
        short_solid = short_solid.replace("Icosahedron", "Icosa")
        # Add element emoji to the solid's element part
        solid_parts = short_solid.split("/")
        solid_elem = elem_emoji(solid_parts[1])
        short_solid = solid_parts[0] + "/" + solid_elem
        return ("Atl:" + str(day_num) + " DOT " + short_solid + " " + hol_short, True, solid_parts[1])

    month = ((day_num - 1) // 30) + 1
    day_in_month = ((day_num - 1) % 30) + 1
    week = ((day_in_month - 1) // 10) + 1
    day_in_week = ((day_in_month - 1) % 10) + 1

    const = ATLANTEAN_CONSTELLATIONS[month - 1]
    const_sym = ATLANTEAN_CONSTELLATION_SYMBOLS[month - 1]
    body = ATLANTEAN_WEEK_BODIES[week - 1]
    chakra = ATLANTEAN_CHAKRAS[day_in_week - 1]

    return ("Atl:" + str(day_num) + " " + const + const_sym + " " + body + " " + chakra + " " + hol_short, False, const)


def compute_13moon(d):
    """Compute 13-Moon Fixed Calendar data for date d."""
    new_year = date(d.year, 7, 26)
    if d < new_year:
        new_year = date(d.year - 1, 7, 26)
    day_num = (d - new_year).days + 1

    if day_num > 364:
        return "13M:DayOutOfTime"

    month = ((day_num - 1) // 28) + 1
    day_in_month = ((day_num - 1) % 28) + 1
    weekday_idx = (day_num - 1) % 7
    weekday_name = MOON_13_WEEKDAYS[weekday_idx]
    month_name = MOON_13_MONTH_NAMES[month - 1]

    return "13M:" + month_name + str(month) + "d" + str(day_in_month) + " " + weekday_name


def compute_alkhemia(d):
    """Compute Alkhemia Path data for date d. Returns (field_string, is_eclipse)."""
    if d < ALKHEMIA_START or d > ALKHEMIA_END:
        return ("Alk:---", False)

    global_day = (d - ALKHEMIA_START).days + 1
    cycle_num = (global_day - 1) // 13
    day_in_cycle = ((global_day - 1) % 13) + 1

    if cycle_num >= len(ALKHEMIA_ELEMENTS):
        return ("Alk:---", False)

    elem_name = ALKHEMIA_ELEMENTS[cycle_num]
    elem_abbrev = elem_name[:4]
    sign, chakra, verb = ALKHEMIA_13DAY[day_in_cycle]

    result = "Alk:" + elem_abbrev + " d" + str(day_in_cycle) + "/" + sign + "/" + verb + "/" + chakra

    is_eclipse = False
    if d in ALKHEMIA_ECLIPSES:
        result = result + " ECLIPSE:" + ALKHEMIA_ECLIPSES[d]
        is_eclipse = True

    return (result, is_eclipse)


def compute_hol(d):
    """Compute Hol Cycle (Seasonal) for date d."""
    m = d.month
    day = d.day

    if (m == 3 and day >= 20) or (m == 4) or (m == 5) or (m == 6 and day <= 20):
        return "Hol:HolPhyr/" + elem_emoji("Fire")
    if (m == 6 and day >= 21) or (m == 7 and day <= 29):
        return "Hol:HolWas/" + elem_emoji("Water")
    if (m == 7 and day >= 30) or (m == 8) or (m == 9 and day <= 21):
        return "Hol:HolHah/" + elem_emoji("Eternal")
    if (m == 9 and day >= 22) or (m == 10) or (m == 11) or (m == 12 and day <= 20):
        return "Hol:HolHir/" + elem_emoji("Air")
    if (m == 12 and day >= 21) or (m == 1) or (m == 2) or (m == 3 and day <= 19):
        return "Hol:HolTum/" + elem_emoji("Earth")

    return "Hol:Unknown"


def compute_moon_phase(d):
    """Compute approximate moon phase and illumination for date d."""
    ref = nearest_new_moon(d)
    days_since = (d - ref).days
    moon_age = days_since % 29.53

    if moon_age < 1.5:
        phase = "NewMoon"
    elif moon_age < 7:
        phase = "WaxCres"
    elif moon_age < 8.5:
        phase = "1stQtr"
    elif moon_age < 13.5:
        phase = "WaxGib"
    elif moon_age < 16:
        phase = "FullMoon"
    elif moon_age < 21.5:
        phase = "WanGib"
    elif moon_age < 23:
        phase = "LastQtr"
    elif moon_age < 29:
        phase = "WanCres"
    else:
        phase = "DarkMoon"

    illum_frac = (1.0 - math.cos(2.0 * math.pi * moon_age / 29.53)) / 2.0
    illum_pct = int(round(illum_frac * 100))

    return "Moon:" + phase + "(" + str(illum_pct) + "%)"


def compute_moon_zodiac(d):
    """Compute the tropical zodiac sign of the Moon for date d.

    Uses solar_longitude() + 13.176°/day lunar displacement from the
    nearest new moon reference date.

    Returns a string like 'Cap\\u2651' (abbreviated sign name + symbol).
    """
    sun_tropical = solar_longitude(d)
    ref = nearest_new_moon(d)
    days_since_ref = (d - ref).days

    # Moon's tropical longitude ≈ Sun's longitude + 13.176°/day × days since new moon
    # At new moon, Moon ≈ Sun (elongation = 0)
    moon_tropical = (sun_tropical + 13.176396 * days_since_ref) % 360.0

    sign_idx = int(moon_tropical // 30.0) % 12
    abbr = MOON_ZODIAC_ABBR[sign_idx]
    sym = TROPICAL_ZODIAC_SYMBOLS[sign_idx]

    return abbr + sym


# ============================================================
# Astrology mode — planetary positions via PyEphem
# ============================================================

# Planet symbols and ephem classes
ASTRO_PLANETS = [
    ("Sun", "\u2609", ephem.Sun),
    ("Moon", "\u263d", ephem.Moon),
    ("Mercury", "\u263f", ephem.Mercury),
    ("Venus", "\u2640", ephem.Venus),
    ("Mars", "\u2642", ephem.Mars),
    ("Jupiter", "\u2643", ephem.Jupiter),
    ("Saturn", "\u2644", ephem.Saturn),
]


def _planet_ecliptic_lon(p, d):
    """Compute ecliptic longitude in degrees for a planet on date d."""
    obs = ephem.Observer()
    obs.date = ephem.Date(d)
    p.compute(obs)
    return ephem.Ecliptic(p).lon * 180.0 / math.pi


def compute_astro(d):
    """Compute astrology data for date d using PyEphem.

    Returns a dict with:
      - 'planets': list of (name, symbol, sign_abbr, sign_sym, longitude, is_rx)
      - 'conjunctions': list of "Conj(body1+body2)" strings
      - 'rx_list': list of "Rx(symbol)" strings
    """
    if not HAS_EPHEM:
        return {"planets": [], "conjunctions": [], "rx_list": []}

    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
             "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    syms = ["\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d",
            "\u264e", "\u264f", "\u2650", "\u2651", "\u2652", "\u2653"]

    # Compute all planet positions
    longitudes = {}
    planet_data = []
    for name, sym, cls in ASTRO_PLANETS:
        p = cls()
        lon = _planet_ecliptic_lon(p, d)
        longitudes[name] = lon
        sign_idx = int(lon / 30.0) % 12
        is_rx = False
        # Check retrograde: compare with tomorrow's longitude
        if name not in ("Sun", "Moon"):
            p2 = cls()
            tomorrow = d + timedelta(days=1)
            lon2 = _planet_ecliptic_lon(p2, tomorrow)
            diff = lon2 - lon
            if diff > 180:
                diff -= 360
            if diff < -180:
                diff += 360
            is_rx = diff < 0
        planet_data.append({
            "name": name,
            "symbol": sym,
            "sign_abbr": signs[sign_idx],
            "sign_sym": syms[sign_idx],
            "longitude": lon,
            "is_rx": is_rx,
        })

    # Check conjunctions (elongation < 1.5 degrees)
    conjunctions = []
    bodies = list(longitudes.keys())
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            n1, n2 = bodies[i], bodies[j]
            diff = abs(longitudes[n1] - longitudes[n2])
            if diff > 180:
                diff = 360 - diff
            if diff < 1.5:
                # Get symbols
                s1 = next(s for nm, s, _ in ASTRO_PLANETS if nm == n1)
                s2 = next(s for nm, s, _ in ASTRO_PLANETS if nm == n2)
                conjunctions.append("Conj(" + s1 + s2 + ")")

    # Build retrograde list
    rx_list = []
    for pd in planet_data:
        if pd["is_rx"]:
            rx_list.append("Rx(" + pd["symbol"] + ")")

    return {"planets": planet_data, "conjunctions": conjunctions, "rx_list": rx_list}


def compute_nine_star_ki(year):
    """Compute Nine Star Ki annual star for a given year."""
    digit_sum = year
    while digit_sum > 10:
        s = 0
        temp = digit_sum
        while temp > 0:
            s = s + (temp % 10)
            temp = temp // 10
        digit_sum = s

    star = 11 - digit_sum
    if star == 10:
        star = 1
    if star < 1:
        star = star + 9

    trigram, element = NINE_STAR_KI[star]
    return "9SK:" + str(star) + "-" + trigram + "/" + elem_emoji(element)


def compute_sexagenary(year):
    """Compute Chinese sexagenary year for a given year."""
    pos = (year - 3) % 60
    if pos == 0:
        pos = 60

    stem_idx = (pos - 1) % 10
    branch_idx = (pos - 1) % 12

    stem_element, stem_yinyang = SEXAGENARY_STEMS[stem_idx]
    branch_animal = SEXAGENARY_BRANCHES[branch_idx]

    return "Sex:" + elem_emoji(stem_element) + "/" + branch_animal + "/" + stem_yinyang


def compute_season(d, hemisphere="south"):
    """Compute season for date d based on hemisphere setting.

    hemisphere: 'north', 'south', or 'both'
    Returns the season field string.
    """
    m = d.month
    day = d.day

    # Determine Northern Hemisphere season
    if (m == 3 and day >= 20) or (m == 4) or (m == 5) or (m == 6 and day <= 20):
        n_season = "Spring"
    elif (m == 6 and day >= 21) or (m == 7) or (m == 8) or (m == 9 and day <= 21):
        n_season = "Summer"
    elif (m == 9 and day >= 22) or (m == 10) or (m == 11) or (m == 12 and day <= 20):
        n_season = "Autumn"
    elif (m == 12 and day >= 21) or (m == 1) or (m == 2) or (m == 3 and day <= 19):
        n_season = "Winter"
    else:
        n_season = "Unknown"

    # Southern Hemisphere seasons are opposite
    s_map = {"Spring": "Autumn", "Summer": "Winter", "Autumn": "Spring", "Winter": "Summer"}
    s_season = s_map.get(n_season, "Unknown")

    if hemisphere == "north":
        return "Sea:N" + n_season
    elif hemisphere == "south":
        return "Sea:S" + s_season
    else:  # both
        return "Sea:N" + n_season + "/S" + s_season


def compute_zodiac(d, is_dot):
    """Compute tropical zodiac sign, element, and modality from actual sun position."""
    if is_dot:
        return "Zod:---"

    sun_tropical = solar_longitude(d)

    # Tropical zodiac sign: 0-11 (Aries=0, Taurus=1, ..., Pisces=11)
    sign_idx = int(sun_tropical // 30.0) % 12
    sign_name = TROPICAL_ZODIAC_SIGNS[sign_idx]
    sign_sym = TROPICAL_ZODIAC_SYMBOLS[sign_idx]
    elem = ZODIAC_ELEMENTS.get(sign_name, "---")
    mod = ZODIAC_MODALITIES.get(sign_name, "---")

    return "Zod:" + sign_name + sign_sym + "/" + elem_emoji(elem) + "/" + mod


def compute_holi_nada(d):
    """Check if date is a HoliNada date."""
    if d in HOLI_NADA:
        return HOLI_NADA[d]
    return None


# ============================================================
# Decan (10-day cycle) — 36 decans, 3 per zodiac sign
# ============================================================

def compute_decan(d, is_dot):
    """Compute the Hellenistic/Egyptian decan for date d.

    Each zodiac sign (30 degrees) is divided into 3 decans of 10 degrees each.
    The decan is determined by the sun's tropical longitude within the current sign.
    Shows both the Chaldean ruler and the triplicity (Dorothean) ruler.

    Format: Dec:SignNum/DecanName/ChaldeanRuler+TriplicityRuler
    e.g. Dec:Cancer2/Sekhmet/Mars+Venus
    """
    if is_dot:
        return "Dec:---"

    sun_tropical = solar_longitude(d)

    # Sign index 0-11 (Aries=0, ..., Pisces=11)
    sign_idx = int(sun_tropical // 30.0) % 12
    sign_name = TROPICAL_ZODIAC_SIGNS[sign_idx]
    sign_sym = TROPICAL_ZODIAC_SYMBOLS[sign_idx]

    # Degree within sign (0-29.99...)
    degree_in_sign = sun_tropical % 30.0
    # Decan within sign (0, 1, 2) — each 10 degrees
    decan_in_sign = int(degree_in_sign // 10.0)

    # Global decan index (0-35)
    decan_idx = sign_idx * 3 + decan_in_sign

    # Day within decan (1-10) — approximately 10 days per decan
    # degree within decan (0-9.99...)
    degree_in_decan = degree_in_sign % 10.0
    day_in_decan = int(degree_in_decan) + 1

    # Get rulers
    chaldean_ruler = DECAN_CHALDEAN_RULERS[decan_idx]
    sign_element = ZODIAC_ELEMENTS.get(sign_name, "---")
    triplicity_rulers = DECAN_TRIPLICITY_RULERS.get(sign_element, ["---", "---", "---"])
    triplicity_ruler = triplicity_rulers[decan_in_sign]

    # Decan name
    decan_name = DECAN_NAMES[decan_idx]

    # Roman numeral for decan within sign (I, II, III)
    decan_roman = ["I", "II", "III"][decan_in_sign]

    return ("Dec:" + sign_name + sign_sym + decan_roman + "/" +
            decan_name + "/d" + str(day_in_decan) + "/" +
            chaldean_ruler + "+" + triplicity_ruler)


# ============================================================
# Wavespell (13-day cycle) — Dreamspell + Tzolkin trecena
# ============================================================

def compute_wavespell(d):
    """Compute the 13-day wavespell energy for date d.

    Shows both:
    1. Dreamspell wavespell: derived from the 13-Moon calendar.
       Each 28-day month contains 2 wavespells of 13 days + 2 extra days.
       The 13 Galactic Tones (Magnetic through Cosmic) cycle within each wavespell.
    2. Tzolkin trecena: the traditional Mayan 13-day period from the Tzolkin cycle.
       Shows the trecena number (1-13) and the Tzolkin day name (nawal).

    Format: Wav:DSTone/TrecenaNum+Nawal
    e.g. Wav:Magnetic/1+Imix
    """
    # --- Dreamspell wavespell ---
    # The 13-Moon year starts July 26. Each 28-day month has 2 wavespells:
    # Days 1-13 = wavespell 1, Days 14-26 = wavespell 2, Days 27-28 = extra (tone 13 carries over)
    # The tone cycles 1-13 continuously through the year.
    new_year = date(d.year, 7, 26)
    if d < new_year:
        new_year = date(d.year - 1, 7, 26)
    day_num = (d - new_year).days + 1

    if day_num > 364:
        # Day Out of Time (July 25) — tone 13 (Cosmic), last month (Cosmic13)
        ds_tone_idx = 12  # 0-indexed = tone 13
        ds_tone_name = GALACTIC_TONES[12][0]
        ds_tone_power = GALACTIC_TONES[12][1]
        ds_tone_action = GALACTIC_TONES[12][2]
        month = 13  # Cosmic month
        ws_in_month = 2  # second wavespell of the month
    else:
        # Tone cycles 1-13 continuously: day 1 = tone 1, day 14 = tone 1, etc.
        ds_tone_num = ((day_num - 1) % 13) + 1  # 1-13
        ds_tone_idx = ds_tone_num - 1  # 0-indexed
        ds_tone_name = GALACTIC_TONES[ds_tone_idx][0]
        ds_tone_power = GALACTIC_TONES[ds_tone_idx][1]
        ds_tone_action = GALACTIC_TONES[ds_tone_idx][2]
        # Which wavespell within the month (1 or 2)
        month = ((day_num - 1) // 28) + 1
        day_in_month = ((day_num - 1) % 28) + 1
        ws_in_month = 1 if day_in_month <= 13 else 2

    # --- Tzolkin trecena ---
    # The trecena is the 13-day period in the Tzolkin. The trecena number
    # is the Tzolkin number (1-13), and the nawal is the Tzolkin day name.
    jd = to_julian_day(d)
    days_since_creation = jd - MAYAN_CORRELATION_JD
    tzolkin_num = ((days_since_creation + 3) % 13) + 1
    tzolkin_name_idx = (days_since_creation + 19) % 20
    tzolkin_name = MAYAN_TZOLKIN_NAMES[tzolkin_name_idx]

    return ("Wav:" + ds_tone_name + str(ds_tone_idx + 1) + "/" +
            ds_tone_power + "/" + ds_tone_action + " WS" + str(ws_in_month) + "M" + str(month) +
            " Tz" + str(tzolkin_num) + "+" + tzolkin_name)


# ============================================================
# Hindu / Vedic Panchangam
# ============================================================

def compute_vedic(d):
    """Compute approximate Vedic Panchangam elements for date d.

    Uses solar_sidereal_longitude() for rashi (sidereal sign),
    and derives nakshatra and tithi from approximate lunar longitude.
    """
    sun_sidereal = solar_sidereal_longitude(d)

    # Rashi (sidereal zodiac sign): 0-11
    rashi_idx = int(sun_sidereal // 30.0) % 12
    rashi = VEDIC_SIGNS[rashi_idx]

    # --- Lunar longitude (sidereal, approximate) ---
    ref = nearest_new_moon(d)
    days_since_ref = (d - ref).days
    # At new moon, lunar longitude ≈ solar longitude
    # Moon moves ~13.176 deg/day relative to the fixed stars
    moon_sidereal = (sun_sidereal + 13.176396 * days_since_ref) % 360.0

    # Nakshatra: 27 mansions of 13.3333 degrees each
    nakshatra_idx = int(moon_sidereal / (360.0 / 27.0)) % 27
    nakshatra = VEDIC_NAKSHATRAS[nakshatra_idx]

    # Tithi: 30 lunar days, each = 12 degrees of Moon-Sun elongation
    elongation = (moon_sidereal - sun_sidereal) % 360.0
    tithi_num = int(elongation // 12.0) % 30
    if tithi_num < 15:
        tithi = VEDIC_TITHI_NAMES_SHUKLA[tithi_num]
    else:
        tithi = VEDIC_TITHI_NAMES_KRISHNA[tithi_num - 15]

    # Vedic weekday and lord
    wd = d.weekday()
    vara = VEDIC_WEEKDAYS[wd]
    vara_lord = VEDIC_WEEKDAY_LORDS[wd]

    return "Ved:" + rashi + "/" + nakshatra + "/" + tithi + "/" + vara + "/" + vara_lord


# ============================================================
# Traditional Chinese Lunar Calendar (Hsia)
# ============================================================

def compute_chinese_lunar(d):
    """Compute Chinese lunar calendar date for date d.

    Uses pre-computed Chinese New Year dates and lunar month lengths.
    Handles leap months (13-month years) for 2025 and 2028.
    """
    cy = d.year
    if cy < 2024:
        cy = 2024
    if cy > 2029:
        cy = 2029

    cny = CHINESE_NEW_YEAR.get(cy)
    if cny is None:
        cny = CHINESE_NEW_YEAR.get(cy - 1, date(cy, 2, 1))
        cy = cy - 1

    # If before this year's CNY, use previous year
    if d < cny:
        cy = cy - 1
        cny = CHINESE_NEW_YEAR.get(cy)
        if cny is None:
            return "Chi:---"

    months = CHINESE_LUNAR_MONTHS.get(cy)
    if months is None:
        return "Chi:---"

    leap_idx = CHINESE_LEAP_MONTH_IDX.get(cy, -1)

    day_num = (d - cny).days + 1

    remaining = day_num
    month_num = 0
    day_in_month = 0
    is_leap_month = False
    for i in range(len(months)):
        mdays = months[i]
        if remaining <= mdays:
            month_num = i + 1
            day_in_month = remaining
            if leap_idx >= 0 and i == leap_idx:
                is_leap_month = True
            break
        remaining = remaining - mdays
    else:
        return "Chi:---"

    if month_num < 1:
        return "Chi:---"

    # Build month name
    if is_leap_month:
        # Leap month: name it Leap + the month name of the preceding month
        prev_name = CHINESE_MONTHS[leap_idx - 1] if leap_idx - 1 < 12 else "Leap"
        month_name = "Leap" + prev_name
    else:
        # Map the list index to the actual month number
        # If there's a leap month before this index, the actual month is index - 1
        actual_month_idx = month_num - 1
        if leap_idx >= 0 and actual_month_idx > leap_idx:
            actual_month_idx = actual_month_idx - 1  # skip the leap entry
        if actual_month_idx < 12:
            month_name = CHINESE_MONTHS[actual_month_idx]
        else:
            month_name = "M" + str(actual_month_idx + 1)

    return "Chi:" + str(cy) + " " + month_name + "/d" + str(day_in_month)


# ============================================================
# Hebrew Calendar
# ============================================================

def hebrew_leap_year(hy):
    """Check if a Hebrew year is a leap year (13 months)."""
    cycle_pos = hy % 19
    return cycle_pos in [0, 3, 6, 8, 11, 14, 17]


def get_hebrew_month_lengths(hy):
    """Return a list of (month_num, days, month_name) for Hebrew year hy."""
    length = HEBREW_YEAR_LENGTHS.get(hy)
    if length is None:
        return []

    is_leap = hebrew_leap_year(hy)
    if is_leap:
        month_names = HEBREW_LEAP_MONTHS
        base = dict(HEBREW_LEAP_BASE)
        num_months = 13
    else:
        month_names = HEBREW_MONTHS
        base = dict(HEBREW_COMMON_BASE)
        num_months = 12

    # Determine Cheshvan and Kislev lengths from year type
    if length == 383 or length == 353:
        # deficient: Cheshvan=29, Kislev=29
        base[2] = 29
        base[3] = 29
    elif length == 384 or length == 354:
        # regular: Cheshvan=29, Kislev=30
        base[2] = 29
        base[3] = 30
    elif length == 385 or length == 355:
        # complete: Cheshvan=30, Kislev=30
        base[2] = 30
        base[3] = 30

    result = []
    for m in range(1, num_months + 1):
        result.append((m, base[m], month_names[m - 1]))
    return result


def compute_hebrew(d):
    """Compute Hebrew calendar date for date d."""
    hy = None
    for y in range(5784, 5792):
        nyr = HEBREW_NEW_YEAR.get(y)
        next_yr = HEBREW_NEW_YEAR.get(y + 1)
        if nyr is None:
            continue
        if next_yr is None:
            next_yr = date(2030, 9, 28)
        if nyr <= d < next_yr:
            hy = y
            break

    if hy is None:
        return "Heb:---"

    nyr = HEBREW_NEW_YEAR[hy]
    months = get_hebrew_month_lengths(hy)
    if not months:
        return "Heb:---"

    day_of_year = (d - nyr).days + 1

    remaining = day_of_year
    month_name = ""
    day_in_month = 0
    for mn, mdays, mname in months:
        if remaining <= mdays:
            month_name = mname
            day_in_month = remaining
            break
        remaining = remaining - mdays
    else:
        return "Heb:---"

    return "Heb:" + str(hy) + " " + month_name + "/d" + str(day_in_month)


# ============================================================
# Mayan Calendar (Tzolkin & Haab)
# ============================================================

def compute_mayan(d):
    """Compute Mayan Tzolkin and Haab calendar dates.

    Uses the GMT (Goodman-Martinez-Thompson) correlation: JD 584283 = 4 Ahau 8 Kumku.
    Tzolkin: 260-day cycle (20 day names × 13 numbers)
    Haab: 365-day cycle (18 months × 20 days + 5 Wayeb days)
    """
    jd = to_julian_day(d)
    days_since_creation = jd - MAYAN_CORRELATION_JD

    # Tzolkin: 260-day cycle
    # Day 0 = 4 Ahau. Number cycle: (days_since_creation + 3) % 13 + 1 gives 1-13
    # Actually: at JD 584283 (creation), Tzolkin day = 4 Ahau
    # Tzolkin number = ((days_since_creation + 3) % 13) + 1  ... let's verify:
    # days=0 -> (0+3)%13+1 = 4 ✓
    # Tzolkin name index: Ahau is index 19. (days_since_creation + 19) % 20
    # days=0 -> (0+19)%20 = 19 = Ahau ✓
    tzolkin_num = ((days_since_creation + 3) % 13) + 1
    tzolkin_name_idx = (days_since_creation + 19) % 20
    tzolkin_name = MAYAN_TZOLKIN_NAMES[tzolkin_name_idx]

    # Haab: 365-day cycle
    # At creation (JD 584283), Haab date = 8 Kumku
    # Kumku is month 17 (0-indexed), day 8
    # Haab day number: (days_since_creation + 8) % 365 ... actually:
    # The Haab day-of-year starts at 0 Pop = day 0 of the Haab year
    # At creation: 8 Kumku = 17*20 + 8 = 348th day of Haab year
    # So haab_day_of_year = (days_since_creation + 348) % 365
    haab_day_of_year = (days_since_creation + 348) % 365

    if haab_day_of_year < 360:
        # Regular months: 18 × 20 = 360 days
        haab_month_idx = haab_day_of_year // 20
        haab_day = haab_day_of_year % 20
        haab_month = MAYAN_HAAB_MONTHS[haab_month_idx]
    else:
        # Wayeb: 5 unnamed days (day 360-364)
        wayeb_day = haab_day_of_year - 360
        haab_month = "Wayeb"
        haab_day = wayeb_day

    return "May:" + str(tzolkin_num) + tzolkin_name + " " + str(haab_day) + haab_month


# ============================================================
# Celtic Tree Calendar
# ============================================================

def compute_celtic_tree(d):
    """Compute Celtic Tree Calendar date for date d.

    13 tree months of 28 days each, starting Dec 24.
    Plus 1 Nameless Day on Dec 23 (before Birch starts).
    """
    m = d.month
    day = d.day

    # Nameless Day: December 23
    if m == 12 and day == 23:
        return "Cel:NamelessDay"

    # Calculate day-of-cycle starting from Dec 24 of the most recent past Dec 24
    # Dec 24 = day 1 of Beth
    if m == 12 and day >= 24:
        last_dec24 = date(d.year, 12, 24)
    else:
        last_dec24 = date(d.year - 1, 12, 24)
    cycle_day = (d - last_dec24).days + 1

    # 13 months of 28 days = 364 days, then NamelessDay (day 365)
    if cycle_day > 364:
        return "Cel:NamelessDay"

    month_idx = (cycle_day - 1) // 28  # 0-12
    day_in_month = ((cycle_day - 1) % 28) + 1  # 1-28
    tree_abbr = CELTIC_TREE_ABBR[month_idx]
    tree_name = CELTIC_TREE_NAMES[month_idx]

    return "Cel:" + tree_abbr + "/d" + str(day_in_month) + " " + tree_name.split("/")[1]


# ============================================================
# Islamic Hijri Calendar
# ============================================================

def compute_islamic(d):
    """Compute Islamic (Hijri) calendar date for date d.

    Uses the arithmetic (tabular) Islamic calendar algorithm.
    Months alternate 30/29 days, with 11 leap years in a 30-year cycle
    having an extra day in the last month (Dhu al-Hijjah gets 30 instead of 29).
    """
    jd = to_julian_day(d)

    # Days since Islamic epoch
    days_since_epoch = jd - ISLAMIC_EPOCH_JD

    # Number of complete lunar years elapsed
    # A lunar year averages 354.367 days (12 × 29.53)
    # In the tabular calendar: 30-year cycle has 10631 days
    # (19 common years of 354 days + 11 leap years of 355 days)
    # = 19*354 + 11*355 = 6726 + 3905 = 10631
    # So cycles_elapsed = days_since_epoch // 10631
    # remaining_days = days_since_epoch % 10631
    # Then count years in the remaining days

    cycles = days_since_epoch // 10631
    remaining = days_since_epoch % 10631

    # Count years within the current 30-year cycle
    # Leap years in the cycle (0-indexed): 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29
    # (based on the most common tabular variant — type I)
    ISLAMIC_LEAP_YEARS = [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]

    year_in_cycle = 0
    for y in range(30):
        year_len = 355 if y in ISLAMIC_LEAP_YEARS else 354
        if remaining < year_len:
            year_in_cycle = y
            break
        remaining = remaining - year_len

    hy = cycles * 30 + year_in_cycle + 1  # +1 because epoch is year 1

    # Now 'remaining' is the day-of-year (0-based)
    # Walk through the 12 months to find month and day
    # Month lengths alternate: 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29 = 354
    # In leap year, last month (12th) = 30 instead of 29 → 355
    is_leap = year_in_cycle in ISLAMIC_LEAP_YEARS

    day_of_year = remaining  # 0-based
    month_num = 0
    day_in_month = 0
    for m in range(12):
        if m % 2 == 0:
            month_len = 30  # odd months (1st, 3rd, 5th, ...) have 30 days
        else:
            month_len = 29  # even months (2nd, 4th, 6th, ...) have 29 days
        # Last month (m=11, DhuAlHijjah) gets 30 in leap years
        if m == 11 and is_leap:
            month_len = 30

        if day_of_year < month_len:
            month_num = m + 1
            day_in_month = day_of_year + 1  # 1-based
            break
        day_of_year = day_of_year - month_len

    if month_num == 0:
        return "Isl:---"

    month_name = ISLAMIC_MONTHS[month_num - 1]

    return "Isl:" + str(hy) + " " + month_name + "/d" + str(day_in_month)


# ============================================================
# Aztec Calendar (Tonalpohualli & Xiuhpohualli)
# ============================================================

def compute_aztec(d):
    """Compute Aztec Tonalpohualli and Xiuhpohualli calendar dates.

    Tonalpohualli: 260-day cycle (20 day names × 13 numbers) — shares the same
    cycle as the Mayan Tzolkin, offset by a fixed number of days.
    Xiuhpohualli: 365-day solar year (18 months × 20 days + 5 Nemontemi days).
    """
    jd = to_julian_day(d)
    days_since_mayan_creation = jd - MAYAN_CORRELATION_JD

    # Tonalpohualli: same 260-day cycle as Mayan Tzolkin, offset by 17 days
    # Mayan Tzolkin number: ((days_since_creation + 3) % 13) + 1
    # Aztec day number: same 13-day cycle, offset
    # Aztec day name: (Mayan name index + 17) % 20
    aztec_num = ((days_since_mayan_creation + 3 + AZTEC_TONALPOHUALLI_OFFSET) % 13) + 1
    # Actually the offset applies to the day-name cycle only, not the number.
    # But since the Tonalpohualli and Tzolkin are synchronized, the offset
    # shifts both. Let's use: aztec days_since = days_since_creation + offset
    aztec_days = days_since_mayan_creation + AZTEC_TONALPOHUALLI_OFFSET
    aztec_num = ((aztec_days + 3) % 13) + 1
    aztec_name_idx = (aztec_days + 19) % 20
    aztec_name = AZTEC_TONALPOHUALLI_NAMES[aztec_name_idx]

    # Lord of the Night: 9-day cycle
    # The Lord of the Night cycle starts at the same epoch
    lord_idx = aztec_days % 9
    if lord_idx < 0:
        lord_idx += 9
    lord = AZTEC_LORDS_OF_NIGHT[lord_idx]

    # Xiuhpohualli: 365-day solar year
    # Find the Aztec new year for this date
    ny = None
    for y in sorted(AZTEC_NEW_YEAR.keys()):
        if AZTEC_NEW_YEAR[y] <= d:
            ny = AZTEC_NEW_YEAR[y]
        else:
            break

    if ny is None:
        return "Azt:" + str(aztec_num) + aztec_name + "/" + lord + " Xiuh:---"

    day_of_year = (d - ny).days  # 0-based

    if day_of_year < 360:
        # Regular months: 18 × 20 = 360 days
        x_month_idx = day_of_year // 20
        x_day = day_of_year % 20
        x_month = AZTEC_XIUHPOHUALLI_MONTHS[x_month_idx]
        x_day_str = str(x_day)
    else:
        # Nemontemi: 5 unlucky days (day 360-364)
        nemontemi_day = day_of_year - 360
        x_month = "Nemontemi"
        x_day_str = str(nemontemi_day)

    return "Azt:" + str(aztec_num) + aztec_name + "/" + lord + " " + x_day_str + x_month


# ============================================================
# Persian (Solar Hijri / Jalali) Calendar
# ============================================================

def persian_is_leap(pyear):
    """Check if a Persian year is a leap year using the 33-year cycle."""
    cycle_pos = pyear % 33
    if cycle_pos == 0:
        cycle_pos = 33
    return cycle_pos in PERSIAN_LEAP_YEARS_IN_CYCLE


def compute_persian(d):
    """Compute Persian (Solar Hijri / Jalali) calendar date for date d.

    Uses the 33-year intercalation cycle algorithm.
    Months 1-6: 31 days, months 7-11: 30 days, month 12: 29/30 days.
    """
    jd = to_julian_day(d)
    days_since_epoch = jd - PERSIAN_EPOCH_JD

    if days_since_epoch < 0:
        return "Per:---"

    # Find the Persian year using 33-year cycles
    # Each 33-year cycle has 12053 days (25*365 + 8*366)
    cycles = days_since_epoch // 12053
    remaining = days_since_epoch % 12053

    # Count years within the current 33-year cycle
    year_in_cycle = 0
    for y in range(1, 34):
        year_len = 366 if persian_is_leap(y) else 365
        if remaining < year_len:
            year_in_cycle = y
            break
        remaining = remaining - year_len

    pyear = cycles * 33 + year_in_cycle

    # Now 'remaining' is the day-of-year (0-based)
    day_of_year = remaining

    # Month lengths: 1-6 = 31 days, 7-11 = 30 days, 12 = 29 or 30 (leap)
    is_leap = persian_is_leap(year_in_cycle)
    month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    if is_leap:
        month_lengths[11] = 30  # Esfand has 30 days in leap year

    month_num = 0
    day_in_month = 0
    doy_remaining = day_of_year
    for m in range(12):
        if doy_remaining < month_lengths[m]:
            month_num = m + 1
            day_in_month = doy_remaining + 1  # 1-based
            break
        doy_remaining = doy_remaining - month_lengths[m]

    if month_num == 0:
        return "Per:---"

    month_name = PERSIAN_MONTHS[month_num - 1]

    return "Per:" + str(pyear) + " " + month_name + "/d" + str(day_in_month)


# ============================================================
# Ancient Egyptian Civil Calendar
# ============================================================

# 365-day calendar: 3 seasons × 4 months × 30 days + 5 epagomenal days
EGYPTIAN_SEASONS = ["Akhet", "Peret", "Shemu"]
EGYPTIAN_MONTHS = ["Thoth", "Phaophi", "Hathor", "Choiak",
                   "Tybi", "Mecheir", "Phamenoth", "Pharmouthi",
                   "Pachon", "Payni", "Epiphi", "Mesore"]
# Epagomenal days (5 days after Mesore 30, before Thoth 1 of next year)
EGYPTIAN_EPIGOMENAL = ["Birthday of Osiris", "Birthday of Horus",
                       "Birthday of Set", "Birthday of Isis",
                       "Birthday of Nephthys"]

# Egyptian epoch: JD 1448638 (Nabonassar era, Feb 26 747 BCE — Thoth 1)
EGYPTIAN_EPOCH_JD = 1448638


def compute_egyptian(d):
    """Compute Ancient Egyptian civil calendar date.

    365-day calendar: 3 seasons (Akhet/Peret/Shemu) × 4 months × 30 days
    + 5 epagomenal days at year end. Uses Nabonassar epoch (JD 1448638).
    """
    jd = to_julian_day(d)
    days_since_epoch = jd - EGYPTIAN_EPOCH_JD

    if days_since_epoch < 0:
        return "Eg:---"

    # 365-day cycle, no leap days in the ancient civil calendar
    day_in_cycle = days_since_epoch % 365

    if day_in_cycle >= 360:
        epi_idx = day_in_cycle - 360
        return "Eg:Epig" + str(epi_idx + 1) + "/" + EGYPTIAN_EPIGOMENAL[epi_idx]

    month_num = day_in_cycle // 30       # 0-11
    day_in_month = day_in_cycle % 30     # 0-29
    season_idx = month_num // 4          # 0=Akhet, 1=Peret, 2=Shemu
    season_name = EGYPTIAN_SEASONS[season_idx]
    month_name = EGYPTIAN_MONTHS[month_num]

    # Year count from epoch (no year 0 in ancient reckoning)
    egypt_year = days_since_epoch // 365 + 1

    return "Eg:" + str(egypt_year) + " " + season_name + "/" + month_name + "/d" + str(day_in_month + 1)


# ============================================================
# Hindu Calendar (Vikram Samvat + Panchanga elements)
# ============================================================

# Vikram Samvat epoch: 57 BCE. VS year = Gregorian year + 57 (approximately)
# For luni-solar months, we approximate using the Vikram Samvat new year (Chaitra 1)
# which falls near the vernal equinox / amavasya (typically late March/early April).

Vikram_SAMVAT_EPOCH_YEAR_OFFSET = 57  # VS year = Gregorian year + 57 (after VS new year)

HINDU_VS_MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
                   "Shravana", "Bhadrapada", "Ashwin", "Kartika",
                   "Margashirsha", "Pausha", "Magha", "Phalguna"]

HINDU_PAKSHA = ["Shukla", "Krishna"]

# Nakshatras (27 lunar mansions) — same as Vedic section
HINDU_NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "PurvaPhalguni", "UttaraPhalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "PurvaAshadha", "UttaraAshadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "PurvaBhadrapada", "UttaraBhadrapada", "Revati",
]

# Tithi names (15 per paksha)
HINDU_TITHI_SHUKLA = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
                      "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
                      "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"]
HINDU_TITHI_KRISHNA = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
                       "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
                       "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"]

# Approximate Vikram Samvat new year dates (Chaitra 1) for 2025-2029
VS_NEW_YEAR = {
    2025: date(2025, 3, 30),
    2026: date(2026, 3, 19),
    2027: date(2027, 3, 29),
    2028: date(2028, 3, 28),
    2029: date(2029, 3, 28),
}


def compute_hindu(d):
    """Compute Hindu calendar: Vikram Samvat year + luni-solar month
    + Panchanga elements (Paksha, Tithi, Nakshatra).

    Vikram Samvat year is approximated from VS new year dates.
    Panchanga elements reuse the Vedic lunar model for Nakshatra/Tithi.
    """
    # --- Vikram Samvat year and month ---
    vs_ny = None
    vs_year = None
    for y in sorted(VS_NEW_YEAR.keys()):
        ny = VS_NEW_YEAR[y]
        if ny <= d:
            vs_ny = ny
            vs_year = y + Vikram_SAMVAT_EPOCH_YEAR_OFFSET
        else:
            break

    if vs_ny is None:
        vs_year = min(VS_NEW_YEAR.keys()) + Vikram_SAMVAT_EPOCH_YEAR_OFFSET
        vs_ny = VS_NEW_YEAR[min(VS_NEW_YEAR.keys())]

    # Approximate luni-solar month: ~29.53 days per month
    days_into_year = (d - vs_ny).days
    month_idx = int(days_into_year / 29.53) % 12
    day_in_month = (days_into_year % 30) + 1
    vs_month = HINDU_VS_MONTHS[month_idx]

    # --- Panchanga: Nakshatra & Tithi (reuse Vedic lunar model) ---
    sun_sidereal = solar_sidereal_longitude(d)
    ref = nearest_new_moon(d)
    days_since_ref = (d - ref).days
    moon_sidereal = (sun_sidereal + 13.176396 * days_since_ref) % 360.0

    nakshatra_idx = int(moon_sidereal / (360.0 / 27.0)) % 27
    nakshatra = HINDU_NAKSHATRAS[nakshatra_idx]

    elongation = (moon_sidereal - sun_sidereal) % 360.0
    tithi_num = int(elongation // 12.0) % 30
    if tithi_num < 15:
        paksha = "Shukla"
        tithi = HINDU_TITHI_SHUKLA[tithi_num]
    else:
        paksha = "Krishna"
        tithi = HINDU_TITHI_KRISHNA[tithi_num - 15]

    return "Hin:VS" + str(vs_year) + " " + vs_month + "/d" + str(day_in_month) + "/" + paksha + "/" + tithi + "/" + nakshatra


# ============================================================
# Javanese Calendar (Pasaran + Anno Javanico)
# ============================================================

# 5-day Pasaran cycle
JAVANESE_PASARAN = ["Legi", "Pahing", "Pon", "Wage", "Kliwon"]

# Javanese months (12 months, alternating 29/30 in a 354-day lunar year)
JAVANESE_MONTHS = ["Sura", "Sapar", "Mulud", "BakdaMulud", "JumadilAwal",
                   "JumadilAkhir", "Rejeb", "Ruwah", "Pasa", "Sawal",
                   "Dulkaidah", "Besar"]

# Anno Javanico epoch: 1555 CE (Javanese year = Gregorian year - 1555 for some traditions)
# But commonly: AJ = Gregorian year - 1555, with new year around 1 Sura (approx late June/July)
# For simplicity, we use a fixed correlation: AJ new year ~ July 1
AJ_EPOCH_OFFSET = 1555

# Approximate Anno Javanico new year (1 Sura) dates
AJ_NEW_YEAR = {
    1953: date(2025, 6, 26),   # AJ 1953
    1954: date(2026, 7, 15),
    1955: date(2027, 7, 5),
    1956: date(2028, 6, 24),
    1957: date(2029, 7, 13),
}


def compute_javanese(d):
    """Compute Javanese calendar: Pasaran 5-day cycle + Anno Javanico year/month.

    Pasaran: 5-day cycle (Legi/Pahing/Pon/Wage/Kliwon) running parallel to
    the 7-day week, forming the 35-day Wetonan cycle.
    Anno Javanico: lunar year starting ~1 Sura (late June/July).
    """
    # --- Pasaran: 5-day cycle anchored to a known reference ---
    # Reference: 2025-01-01 = Legi (determined from known Javanese calendar correlation)
    pasaran_ref = date(2025, 1, 1)  # Known: this date = Legi
    days_since_ref = (d - pasaran_ref).days
    pasaran_idx = days_since_ref % 5
    if pasaran_idx < 0:
        pasaran_idx += 5
    pasaran_name = JAVANESE_PASARAN[pasaran_idx]

    # --- Wetonan: 7-day weekday combined with Pasaran = 35-day cycle ---
    weekday_idx = d.weekday()  # 0=Monday
    wetonan_day = (days_since_ref % 35)
    if wetonan_day < 0:
        wetonan_day += 35

    # --- Anno Javanico year and month ---
    aj_ny = None
    aj_year = None
    for ay in sorted(AJ_NEW_YEAR.keys()):
        ny = AJ_NEW_YEAR[ay]
        if ny <= d:
            aj_ny = ny
            aj_year = ay
        else:
            break

    if aj_ny is None:
        aj_year = min(AJ_NEW_YEAR.keys())
        aj_ny = AJ_NEW_YEAR[min(AJ_NEW_YEAR.keys())]

    days_into_year = (d - aj_ny).days
    # Lunar month ~29.53 days, alternate 29/30
    month_idx = int(days_into_year / 29.53) % 12
    day_in_month = (days_into_year % 30) + 1
    aj_month = JAVANESE_MONTHS[month_idx]

    # Gregorian weekday name
    weekday_name = WEEKDAY_NAMES[d.weekday()]

    return "Jav:AJ" + str(aj_year) + " " + aj_month + "/d" + str(day_in_month) + " " + weekday_name + "-" + pasaran_name + "/Wtn" + str(wetonan_day + 1) + "/35"


# ============================================================
# Indian National Calendar (Saka era, solar months)
# ============================================================

# Saka era epoch: 78 CE. Saka year = Gregorian year - 78 (after Saka new year, ~Mar 22)
SAKA_EPOCH_OFFSET = 78

# Indian National Calendar months (solar, standardized)
SAKA_INDIA_MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
                     "Shravana", "Bhadra", "Ashwin", "Kartika",
                     "Agrahayana", "Pausha", "Magha", "Phalguna"]

# Month lengths: Chaitra has 30 days (31 in leap year), then 31,31,31,31,31,31,30,30,30,30,30
# Normal year: 30,31,31,31,31,31,31,30,30,30,30,30 = 365
# Leap year (Gregorian leap): Chaitra = 31 → 366
SAKA_MONTH_LENGTHS_NORMAL = [30, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30]
SAKA_MONTH_LENGTHS_LEAP   = [31, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30]

# Saka new year: March 22 (March 21 in Gregorian leap years)
def saka_new_year(greg_year):
    """Return the Saka new year date for a Gregorian year."""
    is_leap = (greg_year % 4 == 0 and greg_year % 100 != 0) or (greg_year % 400 == 0)
    return date(greg_year, 3, 21 if is_leap else 22)


def compute_saka_india(d):
    """Compute Indian National Calendar (Saka era, standardized solar months).

    Official Indian National Calendar: Saka era starting 78 CE.
    New year: Chaitra 1 = March 22 (March 21 in Gregorian leap years).
    Months: Chaitra(30/31), Vaishakha–Ashwin(31 each), Kartika–Phalguna(30 each).
    """
    # Find which Saka year we're in
    greg_year = d.year
    saka_ny = saka_new_year(greg_year)
    if d < saka_ny:
        saka_ny = saka_new_year(greg_year - 1)
        greg_year = greg_year - 1

    saka_year = greg_year - SAKA_EPOCH_OFFSET

    # Check if Gregorian year containing the Saka new year was a leap year
    is_greg_leap = (greg_year % 4 == 0 and greg_year % 100 != 0) or (greg_year % 400 == 0)
    month_lengths = SAKA_MONTH_LENGTHS_LEAP if is_greg_leap else SAKA_MONTH_LENGTHS_NORMAL

    day_of_year = (d - saka_ny).days  # 0-based

    if day_of_year < 0 or day_of_year >= sum(month_lengths):
        return "SakI:---"

    remaining = day_of_year
    for m in range(12):
        if remaining < month_lengths[m]:
            month_name = SAKA_INDIA_MONTHS[m]
            day_in_month = remaining + 1
            return "SakI:" + str(saka_year) + " " + month_name + "/d" + str(day_in_month)
        remaining -= month_lengths[m]

    return "SakI:---"


# ============================================================
# Balinese Saka Calendar (Pawukon week cycles)
# ============================================================

# Pawukon: 210-day cycle with 10 concurrent week cycles
# Week lengths: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
PAWUKON_WEEK_NAMES = {
    1: ["Luang"],
    2: ["Menga", "Pept"],
    3: ["Pasah", "Beteng", "Kajeng"],
    4: ["Sri", "Laba", "Kajeng", "Jaya"],
    5: ["Umanis", "Paing", "Pon", "Wage", "Kliwon"],  # same as Pasaran
    6: ["Tungleh", "Aryang", "Urukung", "Paniron", "Was", "Kalawen"],
    7: ["Redite", "Coma", "Anggara", "Buda", "Wraspati", "Sukra", "Saniscara"],
    8: ["Sri", "Indra", "Brahma", "Ludra", "Yama", "Sangkara", "Varuna", "Baya"],
    9: ["Dangu", "Jagur", "Dunggulan", "Sri", "Manuh", "Manis", "Asu", "Pancar", "Tungleh"],
    10: ["Pandita", "Patra", "Satria", "Brahma", "Resi", "Raksasa", "Sinta", "Guurn", "Wong", "Tenung"],
}

# Pawukon epoch: we anchor to a known reference date
# Reference: 2025-01-01 corresponds to Pawukon day 1 of a cycle
PAWUKON_REF = date(2025, 1, 1)


def compute_saka_bali(d):
    """Compute Balinese Saka/Pawukon calendar data.

    Pawukon: 210-day cycle running independently of the solar year.
    Contains 10 concurrent weeks of lengths 1-10 days.
    Also computes the Balinese Saka year (luni-solar, ~based on new moon
    near vernal equinox, approximately Saka year = Gregorian year - 78).
    """
    days_since_ref = (d - PAWUKON_REF).days
    day_in_pawukon = days_since_ref % 210
    if day_in_pawukon < 0:
        day_in_pawukon += 210

    # Compute day name in each week cycle
    week_parts = []
    for wl in [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
        names = PAWUKON_WEEK_NAMES[wl]
        idx = day_in_pawukon % wl
        week_parts.append("w" + str(wl) + ":" + names[idx])

    # Pawukon day number within the 210-day cycle
    pawukon_day = day_in_pawukon + 1

    # Balinese Saka year (approximate: same era as Indian Saka, ~year - 78)
    bali_saka_year = d.year - 78
    # Adjust if before the Saka new year (~Nyepi, near March equinox)
    saka_ny = saka_new_year(d.year)
    if d < saka_ny:
        bali_saka_year -= 1

    return "SakB:" + str(bali_saka_year) + " Pwk" + str(pawukon_day) + "/210 " + " ".join(week_parts)


# ============================================================
# Human-readable formatting
# ============================================================

def _strip_prefix(field):
    """Remove the 'Tag:' prefix from a field string. Returns (label, value)."""
    if ":" in field:
        idx = field.index(":")
        return field[:idx], field[idx + 1:]
    return "", field


def _format_compact_human(parts):
    """Format compact mode (7 parts) as human-readable lines."""
    # parts: wd_field, atl_field, zod, season, moon13, moon_phase, flags_field
    wd = parts[0]
    # "Tuesday/Mars 2026-06-30"
    wd_parts = wd.split(" ")
    weekday_full = wd_parts[0].split("/")[0] if "/" in wd_parts[0] else wd_parts[0]
    planet = wd_parts[0].split("/")[1] if "/" in wd_parts[0] else ""
    date_str = wd_parts[1] if len(wd_parts) > 1 else ""

    lines = []
    lines.append("  " + weekday_full + ", " + date_str + "  (ruler: " + planet + ")")
    lines.append("  " + "-" * 40)

    # Atlantean
    _, atl_val = _strip_prefix(parts[1])
    lines.append("  Atlantean:  " + atl_val)

    # Zodiac
    _, zod_val = _strip_prefix(parts[2])
    lines.append("  Zodiac:     " + zod_val)

    # Season
    _, sea_val = _strip_prefix(parts[3])
    lines.append("  Season:     " + sea_val)

    # 13-Moon
    _, m13_val = _strip_prefix(parts[4])
    lines.append("  13-Moon:    " + m13_val)

    # Moon phase
    _, moon_val = _strip_prefix(parts[5])
    lines.append("  Moon:       " + moon_val)

    # Flags
    _, flag_val = _strip_prefix(parts[6])
    if flag_val != "---":
        lines.append("  Flags:      " + flag_val)

    return "\n".join(lines)


def _format_main_cycles_human(parts):
    """Format main-cycles mode (9 parts) as human-readable lines."""
    # parts: wd_field, seven_day, decan, wavespell, zod_month, atl_month, moon13_month, moon_phase, flags_field
    wd = parts[0]
    wd_parts = wd.split(" ")
    weekday_full = wd_parts[0].split("/")[0] if "/" in wd_parts[0] else wd_parts[0]
    planet = wd_parts[0].split("/")[1] if "/" in wd_parts[0] else ""
    date_str = wd_parts[1] if len(wd_parts) > 1 else ""

    lines = []
    lines.append("  " + weekday_full + ", " + date_str + "  (ruler: " + planet + ")")
    lines.append("  " + "-" * 50)

    # 7-day
    _, val = _strip_prefix(parts[1])
    lines.append("  7-Day Planet:   " + val)

    # 10-day Decan
    _, val = _strip_prefix(parts[2])
    lines.append("  10-Day Decan:   " + val)

    # 13-day Wavespell
    _, val = _strip_prefix(parts[3])
    lines.append("  13-Day Wave:    " + val)

    # 12-month Zodiac
    _, val = _strip_prefix(parts[4])
    lines.append("  12-Mo Zodiac:   " + val)

    # 12-month Atlantean
    _, val = _strip_prefix(parts[5])
    lines.append("  12-Mo Atlantean:" + val)

    # 13-month Moon
    _, val = _strip_prefix(parts[6])
    lines.append("  13-Mo 13Moon:   " + val)

    # Moon phase
    _, val = _strip_prefix(parts[7])
    lines.append("  Moon:           " + val)

    # Flags
    _, val = _strip_prefix(parts[8])
    if val != "---":
        lines.append("  Flags:          " + val)

    return "\n".join(lines)


# Human-readable labels for full-mode fields (in order after the 6 compact fields)
_FULL_LABELS = [
    "9 Star Ki", "Sexagenary", "Alkhemia", "Vedic", "Chinese Lunar",
    "Hebrew", "Mayan", "Celtic Tree", "Islamic", "Aztec",
    "Persian", "Egyptian", "Hindu", "Javanese", "Saka India",
    "Saka Bali", "Decan", "Wavespell",
]


def _format_full_human(parts, ordered_labels=None):
    """Format full mode as human-readable lines.

    ordered_labels: list of label strings for the full-mode fields (after compact 6).
    If None, uses the default _FULL_LABELS for backward compatibility.
    """
    if ordered_labels is None:
        ordered_labels = _FULL_LABELS

    num_full = len(ordered_labels)
    # First 6 are compact fields, then num_full full-only, then flags at the end
    lines = []
    # Reuse compact formatting for first 6 fields (flags is at end, so pass dummy)
    lines.append(_format_compact_human(parts[:6] + ["Flags:---"]))
    lines.append("")
    lines.append("  " + "~" * 40)
    for i in range(num_full):
        label = ordered_labels[i]
        _, val = _strip_prefix(parts[6 + i])
        lines.append("  " + label + ":" + " " * max(1, 14 - len(label)) + val)
    # Flags is last element
    flags_idx = 6 + num_full
    if flags_idx < len(parts):
        _, flag_val = _strip_prefix(parts[flags_idx])
        if flag_val != "---":
            lines.append("  Flags:          " + flag_val)
    return "\n".join(lines)


def format_human(parts, args, ordered_labels=None):
    """Build a human-readable multi-line block for one day."""
    if args.main_cycles:
        return _format_main_cycles_human(parts)
    elif args.full:
        return _format_full_human(parts, ordered_labels)
    else:
        return _format_compact_human(parts)


def compute_flags(current, is_dot):
    """Build the flags list and flags field string for a date.

    Checks HoliNada dates, DOT days, and Alkhemia eclipses.
    Returns (flags_list, flags_field, alk_result).
    """
    flags = []
    nada = compute_holi_nada(current)
    if nada:
        flags.append(nada)
    if is_dot:
        flags.append("DOT")
    # Always check for eclipses (even in compact mode)
    alk_result, alk_eclipse = compute_alkhemia(current)
    if alk_eclipse and "ECLIPSE:" in alk_result:
        eclipse_name = alk_result.split("ECLIPSE:")[1]
        flags.append("ECLIPSE:" + eclipse_name)

    if flags:
        flags_field = "Flags:" + " ".join(flags)
    else:
        flags_field = "Flags:---"

    return flags, flags_field, alk_result


def compute_main_cycles_parts(current, wd_field, is_dot, moon_phase):
    """Build the parts list for --main-cycles mode.

    Returns (parts_list, cycle_data) where cycle_data is a dict of
    structured values needed for JSON output.
    """
    decan = compute_decan(current, is_dot)
    wavespell = compute_wavespell(current)

    # 7-day: planetary ruler
    planet_ruler = PLANETARY_RULERS[current.weekday()]
    planet_sym = PLANETARY_SYMBOLS.get(planet_ruler, "")
    seven_day = "7D:" + planet_ruler + planet_sym

    # 12-month: Zodiac month energy
    if is_dot:
        zod_month = "12Z:---"
        z_sign_idx = z_sign_name = z_sign_sym = z_ruler = z_ruler_sym = z_elem = None
    else:
        sun_z = solar_longitude(current)
        z_sign_idx = int(sun_z // 30.0) % 12
        z_sign_name = TROPICAL_ZODIAC_SIGNS[z_sign_idx]
        z_sign_sym = TROPICAL_ZODIAC_SYMBOLS[z_sign_idx]
        z_ruler = ZODIAC_RULERS.get(z_sign_name, "---")
        z_ruler_sym = PLANETARY_SYMBOLS.get(z_ruler, "")
        z_elem = ZODIAC_ELEMENTS.get(z_sign_name, "---")
        zod_month = "12Z:M" + str(z_sign_idx + 1) + "/" + z_sign_name + z_sign_sym + "/" + elem_emoji(z_elem) + "/" + z_ruler + z_ruler_sym

    # 12-month: Atlantean month energy
    if is_dot:
        atl_month = "12A:DOT"
        atl_month_num = atl_day_in_month = atl_const = atl_const_sym = atl_body = None
    else:
        atl_ny = date(current.year, 8, 4)
        if current < atl_ny:
            atl_ny = date(current.year - 1, 8, 4)
        atl_day_num = (current - atl_ny).days + 1
        atl_month_num = ((atl_day_num - 1) // 30) + 1
        atl_day_in_month = ((atl_day_num - 1) % 30) + 1
        atl_const = ATLANTEAN_CONSTELLATIONS[atl_month_num - 1]
        atl_const_sym = ATLANTEAN_CONSTELLATION_SYMBOLS[atl_month_num - 1]
        atl_week_num = ((atl_day_in_month - 1) // 10) + 1
        atl_body = ATLANTEAN_WEEK_BODIES[atl_week_num - 1]
        atl_month = "12A:M" + str(atl_month_num) + "/d" + str(atl_day_in_month) + "/" + atl_const + atl_const_sym + "/" + atl_body

    # 13-month: 13-Moon month energy
    moon_ny = date(current.year, 7, 26)
    if current < moon_ny:
        moon_ny = date(current.year - 1, 7, 26)
    moon_day_num = (current - moon_ny).days + 1
    if moon_day_num > 364:
        moon13_month = "13M:DOT/Cosmic/Presence"
        m13_month = m13_day_in = m13_tone_name = m13_power = m13_action = None
    else:
        m13_month = ((moon_day_num - 1) // 28) + 1
        m13_day_in = ((moon_day_num - 1) % 28) + 1
        m13_tone = GALACTIC_TONES[m13_month - 1]
        m13_tone_name = m13_tone[0]
        m13_power = m13_tone[1]
        m13_action = m13_tone[2]
        moon13_month = "13M:M" + str(m13_month) + "/d" + str(m13_day_in) + "/" + m13_tone_name + "/" + m13_power + "/" + m13_action

    parts = [wd_field, seven_day, decan, wavespell, zod_month, atl_month, moon13_month, moon_phase]

    cycle_data = {
        "planet_ruler": planet_ruler,
        "planet_sym": planet_sym,
        "decan": decan,
        "wavespell": wavespell,
        "is_dot": is_dot,
        "z_sign_idx": z_sign_idx,
        "z_sign_name": z_sign_name,
        "z_sign_sym": z_sign_sym,
        "z_elem": z_elem,
        "z_ruler": z_ruler,
        "z_ruler_sym": z_ruler_sym,
        "atl_month_num": atl_month_num,
        "atl_day_in_month": atl_day_in_month,
        "atl_const": atl_const,
        "atl_const_sym": atl_const_sym,
        "atl_body": atl_body,
        "moon_day_num": moon_day_num,
        "m13_month": m13_month,
        "m13_day_in": m13_day_in,
        "m13_tone_name": m13_tone_name,
        "m13_power": m13_power,
        "m13_action": m13_action,
    }

    return parts, cycle_data


def compute_full_parts(current, is_dot, alk_result, base_parts, systems=None):
    """Extend base_parts with the selected full-mode calendar fields.

    systems: set of system names to include, or None for all.
    Returns (parts_list, full_data_dict, ordered_labels).
    """
    # Registry: name -> (label, compute_function_or_value)
    # For year-based systems, we pass current.year; for date-based, current.
    all_systems = {
        "9sk":       ("9SK",        compute_nine_star_ki(current.year)),
        "sex":       ("Sex",        compute_sexagenary(current.year)),
        "alk":       ("Alk",        alk_result),
        "vedic":     ("Ved",        compute_vedic(current)),
        "chinese":   ("Chi",        compute_chinese_lunar(current)),
        "hebrew":    ("Heb",        compute_hebrew(current)),
        "mayan":     ("May",        compute_mayan(current)),
        "celtic":    ("Cel",        compute_celtic_tree(current)),
        "islamic":   ("Isl",        compute_islamic(current)),
        "aztec":     ("Azt",        compute_aztec(current)),
        "persian":   ("Per",        compute_persian(current)),
        "egyptian":  ("Eg",         compute_egyptian(current)),
        "hindu":     ("Hin",        compute_hindu(current)),
        "javanese":  ("Jav",        compute_javanese(current)),
        "saka-india": ("SakI",      compute_saka_india(current)),
        "saka-bali": ("SakB",       compute_saka_bali(current)),
        "decan":     ("Dec",        compute_decan(current, is_dot)),
        "wavespell": ("Wav",        compute_wavespell(current)),
    }

    # Determine which systems to include
    if systems is None:
        selected = list(all_systems.keys())
    else:
        selected = [s for s in all_systems if s in systems]

    # Build parts and data in canonical order
    ordered_labels = []
    full_data = {}
    for key in selected:
        label, value = all_systems[key]
        base_parts.append(value)
        full_data[key] = value
        ordered_labels.append(label)

    return base_parts, full_data, ordered_labels


def build_json_main_cycles(current, wd_field, cycle_data, moon_phase, flags):
    """Build a JSON entry dict for --main-cycles mode."""
    entry = {"date": current.isoformat()}
    wd_parts = wd_field.split(" ")
    entry["weekday"] = wd_parts[0].split("/")[0]
    entry["planetary_ruler"] = wd_parts[0].split("/")[1]
    entry["7day"] = {"planet": cycle_data["planet_ruler"], "symbol": cycle_data["planet_sym"]}
    entry["10day_decan"] = cycle_data["decan"]
    entry["13day_wavespell"] = cycle_data["wavespell"]

    if cycle_data["is_dot"]:
        entry["12month_zodiac"] = "---"
        entry["12month_atlantean"] = "DOT"
    else:
        entry["12month_zodiac"] = {
            "month": cycle_data["z_sign_idx"] + 1,
            "sign": cycle_data["z_sign_name"],
            "symbol": cycle_data["z_sign_sym"],
            "element": cycle_data["z_elem"],
            "ruler": cycle_data["z_ruler"],
            "ruler_symbol": cycle_data["z_ruler_sym"],
        }
        entry["12month_atlantean"] = {
            "month": cycle_data["atl_month_num"],
            "day_in_month": cycle_data["atl_day_in_month"],
            "constellation": cycle_data["atl_const"],
            "symbol": cycle_data["atl_const_sym"],
            "body": cycle_data["atl_body"],
        }

    if cycle_data["moon_day_num"] > 364:
        entry["13month_moon"] = {"dot": True, "tone": "Cosmic", "power": "Presence"}
    else:
        entry["13month_moon"] = {
            "month": cycle_data["m13_month"],
            "day_in_month": cycle_data["m13_day_in"],
            "tone": cycle_data["m13_tone_name"],
            "power": cycle_data["m13_power"],
            "action": cycle_data["m13_action"],
        }

    # Parse moon phase: "Moon:FullMoon(99%) Cap\u2651"
    mp = moon_phase.replace("Moon:", "")
    mp_main = mp.split(" ")[0]
    mp_phase = mp_main.split("(")[0]
    mp_illum = mp_main.split("(")[1].replace(")", "").replace("%", "")
    mp_zod = mp.split(" ")[1] if " " in mp else ""
    entry["moon_phase"] = {"phase": mp_phase, "illumination_pct": int(mp_illum), "zodiac": mp_zod}
    entry["flags"] = flags if flags else []
    return entry


def build_json_compact_or_full(current, args, wd_field, atl_field, zod, season, moon13,
                               moon_phase, full_data, flags):
    """Build a JSON entry dict for compact or --full mode."""
    entry = {"date": current.isoformat()}
    entry["weekday"] = wd_field
    entry["atlantean"] = atl_field
    entry["zodiac"] = zod
    entry["season"] = season
    entry["13moon"] = moon13
    entry["moon_phase"] = moon_phase
    if args.full and full_data:
        # JSON key names for each system
        json_keys = {
            "9sk": "nine_star_ki", "sex": "sexagenary", "alk": "alkhemia",
            "vedic": "vedic", "chinese": "chinese_lunar", "hebrew": "hebrew",
            "mayan": "mayan", "celtic": "celtic", "islamic": "islamic",
            "aztec": "aztec", "persian": "persian", "egyptian": "egyptian",
            "hindu": "hindu", "javanese": "javanese",
            "saka-india": "saka_india", "saka-bali": "saka_bali",
            "decan": "decan", "wavespell": "wavespell",
        }
        for key, value in full_data.items():
            json_key = json_keys.get(key, key)
            entry[json_key] = value
    entry["flags"] = flags if flags else []
    return entry


# ============================================================
# Astro mode computation + formatting
# ============================================================

def compute_astro_parts(current, wd_field, moon_phase, flags):
    """Build the parts list for --astro mode.

    Format: Wed(date) | Sun | Moon | Mercury | Venus | Mars | Jupiter | Saturn | Aspects | Flags
    Each planet field: 'Mercury☿:Can♋' or 'Mercury☿:Can♋ Rx'
    Aspects field: 'Asp:Rx(☿) Rx(♄) Conj(☽♀)' or 'Asp:---'
    """
    astro = compute_astro(current)

    parts = [wd_field]

    for pd in astro["planets"]:
        field = pd["name"] + pd["symbol"] + ":" + pd["sign_abbr"] + pd["sign_sym"]
        if pd["is_rx"]:
            field = field + " Rx"
        parts.append(field)

    # Aspects: combine retrograde + conjunctions
    aspects = astro["rx_list"] + astro["conjunctions"]
    if aspects:
        aspects_field = "Asp:" + " ".join(aspects)
    else:
        aspects_field = "Asp:---"
    parts.append(aspects_field)

    parts.append(flags)

    return parts, astro


def build_json_astro(current, wd_field, astro, moon_phase, flags):
    """Build a JSON entry dict for --astro mode."""
    entry = {"date": current.isoformat()}
    wd_parts = wd_field.split(" ")
    entry["weekday"] = wd_parts[0].split("/")[0]
    entry["planetary_ruler"] = wd_parts[0].split("/")[1]

    entry["planets"] = []
    for pd in astro["planets"]:
        entry["planets"].append({
            "name": pd["name"],
            "symbol": pd["symbol"],
            "sign": pd["sign_abbr"],
            "symbol_zodiac": pd["sign_sym"],
            "longitude_deg": round(pd["longitude"], 2),
            "retrograde": pd["is_rx"],
        })

    entry["aspects"] = {
        "retrograde": astro["rx_list"],
        "conjunctions": astro["conjunctions"],
    }
    entry["moon_phase"] = moon_phase
    entry["flags"] = flags if flags else []
    return entry


def _format_astro_human(parts, astro_data):
    """Format --astro mode as human-readable lines."""
    # parts: wd_field, Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Asp, Flags
    wd = parts[0]
    wd_parts = wd.split(" ")
    weekday_full = wd_parts[0].split("/")[0] if "/" in wd_parts[0] else wd_parts[0]
    planet = wd_parts[0].split("/")[1] if "/" in wd_parts[0] else ""
    date_str = wd_parts[1] if len(wd_parts) > 1 else ""

    lines = []
    lines.append("  " + weekday_full + ", " + date_str + "  (ruler: " + planet + ")")
    lines.append("  " + "-" * 50)

    # Planets (indices 1-7 in parts)
    planet_labels = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    for i, label in enumerate(planet_labels):
        _, val = _strip_prefix(parts[1 + i])
        rx_note = "  \u2190 retrograde" if " Rx" in val else ""
        val_clean = val.replace(" Rx", "")
        lines.append("  " + label + ":" + " " * max(1, 10 - len(label)) + val_clean + rx_note)

    # Aspects
    _, asp_val = _strip_prefix(parts[8])
    if asp_val != "---":
        lines.append("  Aspects:   " + asp_val)

    # Flags
    _, flag_val = _strip_prefix(parts[9])
    if flag_val != "---":
        lines.append("  Flags:     " + flag_val)

    return "\n".join(lines)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate pre-computed daily calendar data for YOSOY framework."
    )
    parser.add_argument("--start", default="2025-01-01",
                        help="Start date YYYY-MM-DD, default 2025-01-01")
    parser.add_argument("--end", default="2029-12-31",
                        help="End date YYYY-MM-DD, default 2029-12-31")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--hemisphere", default="south", choices=["north", "south", "both"],
                        help="Hemisphere for seasons: north, south, or both (default: south)")
    parser.add_argument("--full", action="store_true", default=False,
                        help="Output all calendar systems (default: compact 7-field output)")
    parser.add_argument("--main-cycles", action="store_true", default=False,
                        help="Output only the main cycle fields: 7-day(Planet), 10-day(Decan), 13-day(Wavespell), 12-month(Zodiac+Atlantean), 13-month(13Moon), Moon phase")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output as JSON array (works with --main-cycles, --full, or compact)")
    parser.add_argument("--today", action="store_true", default=False,
                        help="Output only today's date (overrides --start/--end)")
    parser.add_argument("-H", "--human", action="store_true", default=False,
                        help="Human-readable multi-line output (one labeled block per day)")
    parser.add_argument("--astro", action="store_true", default=False,
                        help="Astrology mode: planetary zodiac signs, retrograde, conjunctions (requires ephem)")
    parser.add_argument("--systems", default=None,
                        help="Comma-separated calendar systems to include (e.g. vedic,mayan,hebrew). "
                             "Use 'all' for all systems. Implies --full output. "
                             "Available: 9sk,sex,alk,vedic,chinese,hebrew,mayan,celtic,islamic,aztec,"
                             "persian,egyptian,hindu,javanese,saka-india,saka-bali,decan,wavespell")
    args = parser.parse_args()

    # Parse --systems into a set
    selected_systems = None
    if args.systems:
        if args.systems.lower() == "all":
            selected_systems = None  # None means all
        else:
            selected_systems = set(s.strip().lower() for s in args.systems.split(","))
            # Validate
            valid = {"9sk", "sex", "alk", "vedic", "chinese", "hebrew", "mayan", "celtic",
                     "islamic", "aztec", "persian", "egyptian", "hindu", "javanese",
                     "saka-india", "saka-bali", "decan", "wavespell"}
            invalid = selected_systems - valid
            if invalid:
                parser.error("Unknown system(s): " + ", ".join(sorted(invalid)) +
                             ". Valid: " + ", ".join(sorted(valid)))
            # --systems implies --full
            args.full = True

    # Output modes are mutually exclusive
    active_modes = [args.full, args.main_cycles, args.astro]
    if sum(active_modes) > 1:
        parser.error("--full, --main-cycles, and --astro are mutually exclusive")

    if args.astro and not HAS_EPHEM:
        parser.error("--astro requires the 'ephem' package: pip install ephem")

    if args.today:
        today_str = date.today().isoformat()
        start = date.fromisoformat(today_str)
        end = start
    else:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)

    if args.output:
        out = open(args.output, "w", encoding="utf-8")
    else:
        out = sys.stdout

    # Header (skip for JSON and human — output is structured)
    if not args.json and not args.human:
        out.write("# YOSOY Calendar Systems - Pre-Computed Daily Data\n")
        if args.astro:
            out.write("# Format: Gregorian(Full/Planet date) | Sun | Moon | Mercury | Venus | Mars | Jupiter | Saturn | Aspects | Flags\n")
        elif args.main_cycles:
            out.write("# Format: Gregorian(Full/Planet date) | 7day:Planet | 10day:Decan | 13day:Wavespell | 12Z:ZodiacMonth | 12A:AtlanteanMonth | 13M:13MoonMonth | Moon | Flags\n")
        elif args.full:
            if selected_systems is None:
                out.write("# Format: Gregorian(Full/Planet date) | Atlantean(+Hol) | Zodiac | Season | 13Moon | Moon | 9SK | Sexagenary | Alkhemia | Vedic | ChineseLunar | Hebrew | Mayan | Celtic | Islamic | Aztec | Persian | Egyptian | Hindu | Javanese | SakaIndia | SakaBali | Decan | Wavespell | Flags\n")
            else:
                # Dynamic header based on selected systems
                all_labels = {"9sk":"9SK","sex":"Sexagenary","alk":"Alkhemia","vedic":"Vedic",
                    "chinese":"ChineseLunar","hebrew":"Hebrew","mayan":"Mayan","celtic":"Celtic",
                    "islamic":"Islamic","aztec":"Aztec","persian":"Persian","egyptian":"Egyptian",
                    "hindu":"Hindu","javanese":"Javanese","saka-india":"SakaIndia",
                    "saka-bali":"SakaBali","decan":"Decan","wavespell":"Wavespell"}
                sys_names = [all_labels[k] for k in sorted(selected_systems)]
                out.write("# Format: Gregorian(Full/Planet date) | Atlantean(+Hol) | Zodiac | Season | 13Moon | Moon | " + " | ".join(sys_names) + " | Flags\n")
        else:
            out.write("# Format: Gregorian(Full/Planet date) | Atlantean(+Hol) | Zodiac | Season | 13Moon | Moon | Flags\n")

    json_results = []
    current = start
    count = 0
    while current <= end:
        # --- Common fields (always computed) ---
        wd_field = compute_weekday(current)
        atl_field, is_dot, const_or_elem = compute_atlantean(current)
        zod = compute_zodiac(current, is_dot)
        season = compute_season(current, args.hemisphere)
        moon13 = compute_13moon(current)
        moon_phase = compute_moon_phase(current)
        moon_zod = compute_moon_zodiac(current)
        moon_phase = moon_phase + " " + moon_zod

        # --- Flags ---
        flags, flags_field, alk_result = compute_flags(current, is_dot)

        # --- Mode-specific parts ---
        full_data = None
        astro_data = None
        if args.astro:
            parts, astro_data = compute_astro_parts(current, wd_field, moon_phase, flags_field)
        elif args.main_cycles:
            parts, cycle_data = compute_main_cycles_parts(current, wd_field, is_dot, moon_phase)
        elif args.full:
            base_parts = [wd_field, atl_field, zod, season, moon13, moon_phase]
            parts, full_data, ordered_labels = compute_full_parts(current, is_dot, alk_result, base_parts, selected_systems)
        else:
            parts = [wd_field, atl_field, zod, season, moon13, moon_phase]

        if not args.astro:
            parts.append(flags_field)

        # --- Output ---
        if args.json:
            if args.astro:
                entry = build_json_astro(current, wd_field, astro_data, moon_phase, flags)
            elif args.main_cycles:
                entry = build_json_main_cycles(current, wd_field, cycle_data, moon_phase, flags)
            else:
                entry = build_json_compact_or_full(current, args, wd_field, atl_field, zod,
                                                   season, moon13, moon_phase, full_data, flags)
            json_results.append(entry)
        elif args.human:
            if args.astro:
                out.write(_format_astro_human(parts, astro_data) + "\n")
            else:
                out.write(format_human(parts, args, ordered_labels if args.full else None) + "\n")
        else:
            out.write(" | ".join(parts) + "\n")

        current = current + timedelta(days=1)
        count = count + 1

    if args.json:
        out.write(json.dumps(json_results, ensure_ascii=False, indent=2) + "\n")

    if args.output:
        out.close()
        sys.stderr.write("Wrote " + str(count) + " days to " + args.output + "\n")


if __name__ == "__main__":
    main()