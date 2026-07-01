# YOSOY Calendar — Multi-calendar date generator
# Copyright (C) 2026  globalviking
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Additional terms per AGPLv3 section 7:
# You may not use this work, in whole or in part, for the purpose of
# training, fine-tuning, or otherwise improving any artificial intelligence
# or machine learning model, including but not limited to large language
# models, unless you obtain explicit written permission from the copyright
# holder.
#
# Contact: https://github.com/globalviking/calendar
"""Tests for planetary hours — all 7 systems."""
from datetime import date

import pytest

from calendar_data_gen import (
    compute_planetary_hours,
    PLANETARY_HOUR_SYSTEMS,
    DAY_RULERS,
    CHALDEAN_ORDER,
    VEDIC_ORDER,
)


class TestPlanetaryHoursBasics:
    """Every system must produce 24 hours with valid data."""

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_returns_24_hours(self, system):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        assert len(hours) == 24, f"{system}: expected 24 hours, got {len(hours)}"

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_each_hour_has_required_fields(self, system):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        for h in hours:
            assert "hour" in h
            assert "start" in h
            assert "end" in h
            assert "planet" in h
            assert "symbol" in h
            assert "period" in h
            assert h["period"] in ("day", "night")

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_hour_numbers_1_to_24(self, system):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        numbers = [h["hour"] for h in hours]
        assert numbers == list(range(1, 25))

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_first_12_are_day_last_12_are_night(self, system):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        for h in hours[:12]:
            assert h["period"] == "day"
        for h in hours[12:]:
            assert h["period"] == "night"

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_planets_are_valid(self, system):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        valid_planets = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
        for h in hours:
            assert h["planet"] in valid_planets, f"Invalid planet: {h['planet']}"


class TestChaldean:
    def test_monday_starts_with_moon(self):
        d = date(2026, 7, 6)  # Monday
        hours = compute_planetary_hours(d, system="chaldean")
        assert hours[0]["planet"] == "Moon"

    def test_sunday_starts_with_sun(self):
        d = date(2026, 7, 5)  # Sunday
        hours = compute_planetary_hours(d, system="chaldean")
        assert hours[0]["planet"] == "Sun"

    def test_night_continues_cycle(self):
        d = date(2026, 7, 1)  # Wednesday, ruler=Mercury
        hours = compute_planetary_hours(d, system="chaldean")
        # Day ends with hour 12. Night hour 13 should continue from hour 13's planet
        # In Chaldean: hour 12 = order[(ruler_idx + 11) % 7], hour 13 = order[(ruler_idx + 12) % 7]
        ruler_idx = CHALDEAN_ORDER.index("Mercury")
        expected_hour_13 = CHALDEAN_ORDER[(ruler_idx + 12) % 7]
        assert hours[12]["planet"] == expected_hour_13


class TestVedic:
    def test_different_order_than_chaldean(self):
        d = date(2026, 7, 1)  # Wednesday, ruler=Mercury
        ch = compute_planetary_hours(d, system="chaldean")
        vd = compute_planetary_hours(d, system="vedic")
        # 1st hour same (Mercury = ruler in both), but 2nd should differ
        assert ch[0]["planet"] == vd[0]["planet"]
        # Vedic order: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars
        # Mercury at index 2. 2nd hour = Moon (index 3)
        assert vd[1]["planet"] == "Moon"


class TestAlBiruni:
    def test_night_restarts_from_ruler(self):
        d = date(2026, 7, 1)  # Wednesday, ruler=Mercury
        hours = compute_planetary_hours(d, system="al-biruni")
        # Night hour 13 should restart from day ruler (Mercury), not continue
        assert hours[12]["planet"] == "Mercury"

    def test_differs_from_chaldean_at_night(self):
        d = date(2026, 7, 1)
        ch = compute_planetary_hours(d, system="chaldean")
        ab = compute_planetary_hours(d, system="al-biruni")
        # Day hours same, night hours differ
        assert ch[:12] == ab[:12]
        assert ch[12:] != ab[12:]


class TestEgyptian:
    def test_uses_decan_cycle(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="egyptian")
        # Egyptian should differ from Chaldean in at least the first hour
        ch = compute_planetary_hours(d, system="chaldean")
        assert hours[0]["planet"] != ch[0]["planet"] or hours[1]["planet"] != ch[1]["planet"]


class TestHellenistic:
    def test_day_starts_at_sunset(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="hellenistic")
        # In Hellenistic, "day" hours = sunset→sunrise, "night" = sunrise→sunset
        # The 1st hour (sunrise) should be the planet that would be hour 13 in Chaldean
        ch = compute_planetary_hours(d, system="chaldean")
        assert hours[0]["planet"] == ch[12]["planet"]

    def test_night_is_sunrise_hours(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="hellenistic")
        ch = compute_planetary_hours(d, system="chaldean")
        # Hellenistic swaps day/night labels vs Chaldean
        # Hellenistic "day" hours (sunset→sunrise) = Chaldean hours 13-24
        # Hellenistic "night" hours (sunrise→sunset) = Chaldean hours 1-12
        # Hellenistic hour 13 (night, sunrise) = Chaldean hour 1 (day, sunrise)
        # But the planet differs because Hellenistic starts from sunset_hour_idx
        # For Wednesday: sunset_hour_idx = 3 (Sun), night starts at (3+12)%7 = 1 (Jupiter)
        # Chaldean hour 1 = Mercury. They differ.
        assert hours[12]["planet"] != ch[0]["planet"]


class TestTibetan:
    def test_has_nakshatra_field(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="tibetan")
        assert hours[0].get("nakshatra") is not None
        assert isinstance(hours[0]["nakshatra"], str)

    def test_nakshatra_is_valid(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="tibetan")
        valid_nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "PurvaPhalguni", "UttaraPhalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "PurvaAshadha", "UttaraAshadha", "Abhijit",
            "Shravana", "Dhanishta", "Shatabhisha",
            "PurvaBhadra", "UttaraBhadra", "Revati",
        ]
        assert hours[0]["nakshatra"] in valid_nakshatras


class TestEthiopian:
    def test_different_ruler_than_gregorian(self):
        d = date(2026, 7, 1)  # Wednesday → Gregorian ruler = Mercury
        hours = compute_planetary_hours(d, system="ethiopian")
        # Ethiopian uses Coptic epoch, so day ruler differs
        # Coptic weekday for 2026-07-01 should be Friday → ruler = Venus
        assert hours[0]["planet"] == "Venus"

    def test_same_chaldean_order(self):
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system="ethiopian")
        # Sequence should follow Chaldean order from Venus
        ruler_idx = CHALDEAN_ORDER.index("Venus")
        expected_2nd = CHALDEAN_ORDER[(ruler_idx + 1) % 7]
        assert hours[1]["planet"] == expected_2nd


class TestCompareMode:
    def test_compare_returns_string(self):
        from calendar_data_gen import _format_hours_compare
        d = date(2026, 7, 1)
        result = _format_hours_compare(d)
        assert isinstance(result, str)
        assert "chaldean" in result
        assert "ethiopian" in result
        assert "System" in result


class TestEdgeCases:
    def test_polar_region_doesnt_crash(self):
        d = date(2026, 6, 30)
        hours = compute_planetary_hours(d, lat=64.13, lon=-21.94, tz=0)
        assert len(hours) == 24

    def test_date_range_works(self):
        from calendar_data_gen import compute_planetary_hours
        from datetime import date, timedelta
        start = date(2026, 7, 1)
        for i in range(7):
            d = start + timedelta(days=i)
            hours = compute_planetary_hours(d)
            assert len(hours) == 24

    @pytest.mark.parametrize("system", PLANETARY_HOUR_SYSTEMS)
    def test_json_serializable(self, system):
        import json
        d = date(2026, 7, 1)
        hours = compute_planetary_hours(d, system=system)
        json_str = json.dumps(hours, ensure_ascii=False)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert len(parsed) == 24
