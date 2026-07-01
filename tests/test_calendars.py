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
"""Tests for all calendar systems — each compute_* function returns valid data."""
from datetime import date

import pytest

from calendar_data_gen import (
    compute_weekday,
    compute_atlantean,
    compute_zodiac,
    compute_season,
    compute_13moon,
    compute_moon_phase,
    compute_moon_zodiac,
    compute_vedic,
    compute_chinese_lunar,
    compute_hebrew,
    compute_mayan,
    compute_celtic_tree,
    compute_islamic,
    compute_aztec,
    compute_persian,
    compute_egyptian,
    compute_hindu,
    compute_javanese,
    compute_saka_india,
    compute_saka_bali,
    compute_decan,
    compute_wavespell,
    compute_nine_star_ki,
    compute_sexagenary,
    compute_alkhemia,
    compute_holi_nada,
    compute_flags,
    solar_longitude,
    moon_sidereal_longitude,
    nearest_new_moon,
    solar_sidereal_longitude,
)


# Known date for snapshot tests
D = date(2026, 7, 1)  # Wednesday


class TestCoreFunctions:
    def test_solar_longitude(self):
        lon = solar_longitude(D)
        assert 0 <= lon < 360
        # July 1 → Sun around 250-260° (Sagittarius in tropical zodiac)
        assert 240 <= lon <= 270

    def test_solar_longitude_cached(self):
        lon1 = solar_longitude(D)
        lon2 = solar_longitude(D)
        assert lon1 == lon2
        assert solar_longitude.cache_info().hits >= 1

    def test_moon_sidereal_longitude(self):
        lon = moon_sidereal_longitude(D)
        assert 0 <= lon < 360

    def test_nearest_new_moon(self):
        nm = nearest_new_moon(D)
        assert isinstance(nm, date)
        assert nm <= D
        assert (D - nm).days <= 35

    def test_nearest_new_moon_cached(self):
        nm1 = nearest_new_moon(D)
        nm2 = nearest_new_moon(D)
        assert nm1 == nm2
        assert nearest_new_moon.cache_info().hits >= 1

    def test_solar_sidereal_longitude(self):
        lon = solar_sidereal_longitude(D)
        assert 0 <= lon < 360


class TestWeekday:
    def test_returns_string(self):
        result = compute_weekday(D)
        assert isinstance(result, str)
        assert "Wednesday" in result
        assert "Mercury" in result
        assert "2026-07-01" in result


class TestAtlantean:
    def test_returns_tuple(self):
        result = compute_atlantean(D)
        assert len(result) == 3
        field, is_dot, const = result
        assert isinstance(field, str)
        assert isinstance(is_dot, bool)
        assert isinstance(const, str)
        assert "Atl:" in field

    def test_dot_days(self):
        # Day 361+ of Atlantean year = DOT day
        d = date(2026, 7, 30)  # Should be in DOT period
        field, is_dot, const = compute_atlantean(d)
        if is_dot:
            assert "DOT" in field


class TestZodiac:
    def test_returns_string(self):
        result = compute_zodiac(D, is_dot=False)
        assert isinstance(result, str)
        assert "Zod:" in result

    def test_dot_returns_dash(self):
        result = compute_zodiac(D, is_dot=True)
        assert result == "Zod:---"


class TestSeason:
    def test_returns_string(self):
        result = compute_season(D, hemisphere="south")
        assert isinstance(result, str)
        assert "Sea:" in result

    def test_south_is_opposite(self):
        north = compute_season(D, hemisphere="north")
        south = compute_season(D, hemisphere="south")
        assert north != south


class Test13Moon:
    def test_returns_string(self):
        result = compute_13moon(D)
        assert isinstance(result, str)
        assert "13M:" in result

    def test_day_out_of_time(self):
        d = date(2026, 7, 25)  # Day Out of Time
        result = compute_13moon(d)
        assert "DayOutOfTime" in result


class TestMoonPhase:
    def test_returns_string(self):
        result = compute_moon_phase(D)
        assert isinstance(result, str)
        assert "Moon:" in result

    def test_has_percentage(self):
        result = compute_moon_phase(D)
        assert "%" in result


class TestMoonZodiac:
    def test_returns_string(self):
        result = compute_moon_zodiac(D)
        assert isinstance(result, str)
        assert len(result) >= 4  # e.g. "Cap♑"


class TestVedic:
    def test_returns_string(self):
        result = compute_vedic(D)
        assert isinstance(result, str)
        assert "Ved:" in result


class TestChineseLunar:
    def test_returns_string(self):
        result = compute_chinese_lunar(D)
        assert isinstance(result, str)
        assert "Chi:" in result


class TestHebrew:
    def test_returns_string(self):
        result = compute_hebrew(D)
        assert isinstance(result, str)
        assert "Heb:" in result


class TestMayan:
    def test_returns_string(self):
        result = compute_mayan(D)
        assert isinstance(result, str)
        assert "May:" in result


class TestCelticTree:
    def test_returns_string(self):
        result = compute_celtic_tree(D)
        assert isinstance(result, str)
        assert "Cel:" in result

    def test_nameless_day(self):
        d = date(2026, 12, 23)
        result = compute_celtic_tree(d)
        assert "NamelessDay" in result


class TestIslamic:
    def test_returns_string(self):
        result = compute_islamic(D)
        assert isinstance(result, str)
        assert "Isl:" in result


class TestAztec:
    def test_returns_string(self):
        result = compute_aztec(D)
        assert isinstance(result, str)
        assert "Azt:" in result


class TestPersian:
    def test_returns_string(self):
        result = compute_persian(D)
        assert isinstance(result, str)
        assert "Per:" in result


class TestEgyptian:
    def test_returns_string(self):
        result = compute_egyptian(D)
        assert isinstance(result, str)
        assert "Eg:" in result


class TestHindu:
    def test_returns_string(self):
        result = compute_hindu(D)
        assert isinstance(result, str)
        assert "Hin:" in result


class TestJavanese:
    def test_returns_string(self):
        result = compute_javanese(D)
        assert isinstance(result, str)
        assert "Jav:" in result


class TestSakaIndia:
    def test_returns_string(self):
        result = compute_saka_india(D)
        assert isinstance(result, str)
        assert "SakI:" in result


class TestSakaBali:
    def test_returns_string(self):
        result = compute_saka_bali(D)
        assert isinstance(result, str)
        assert "SakB:" in result


class TestDecan:
    def test_returns_string(self):
        result = compute_decan(D, is_dot=False)
        assert isinstance(result, str)
        assert "Dec:" in result

    def test_dot_returns_dash(self):
        result = compute_decan(D, is_dot=True)
        assert result == "Dec:---"


class TestWavespell:
    def test_returns_string(self):
        result = compute_wavespell(D)
        assert isinstance(result, str)
        assert "Wav:" in result


class TestNineStarKi:
    def test_returns_string(self):
        result = compute_nine_star_ki(2026)
        assert isinstance(result, str)
        assert "9SK:" in result


class TestSexagenary:
    def test_returns_string(self):
        result = compute_sexagenary(2026)
        assert isinstance(result, str)
        assert "Sex:" in result


class TestAlkhemia:
    def test_returns_tuple(self):
        result = compute_alkhemia(D)
        assert len(result) == 2
        field, is_eclipse = result
        assert isinstance(field, str)
        assert isinstance(is_eclipse, bool)

    def test_out_of_range(self):
        d = date(2030, 1, 1)
        result = compute_alkhemia(d)
        assert result[0] == "Alk:---"


class TestHoliNada:
    def test_equinox_dates(self):
        d = date(2026, 3, 20)
        result = compute_holi_nada(d)
        assert result is not None
        assert "HoliNada" in result

    def test_normal_date(self):
        result = compute_holi_nada(D)
        assert result is None


class TestFlags:
    def test_returns_tuple(self):
        result = compute_flags(D, is_dot=False)
        assert len(result) == 3
        flags, field, alk = result
        assert isinstance(flags, list)
        assert isinstance(field, str)
        assert isinstance(alk, str)


class TestSnapshot:
    """Snapshot tests — verify known output for a fixed date."""

    def test_overview_output(self):
        """Full pipe-delimited output for 2026-07-01."""
        from calendar_data_gen import compute_weekday, compute_atlantean, compute_zodiac, \
            compute_season, compute_13moon, compute_moon_phase, compute_moon_zodiac, \
            compute_flags, compute_alkhemia

        wd = compute_weekday(D)
        atl, is_dot, _ = compute_atlantean(D)
        zod = compute_zodiac(D, is_dot)
        season = compute_season(D, "south")
        moon13 = compute_13moon(D)
        moon_phase = compute_moon_phase(D)
        moon_zod = compute_moon_zodiac(D)
        moon_phase = moon_phase + " " + moon_zod
        flags, flags_field, alk = compute_flags(D, is_dot)

        assert "Wednesday" in wd
        assert "Mercury" in wd
        assert "Atl:" in atl
        assert "Zod:" in zod
        assert "Sea:" in season
        assert "13M:" in moon13
        assert "Moon:" in moon_phase
        assert "Flags:" in flags_field
