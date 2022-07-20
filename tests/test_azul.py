import pytest
import games.azul as azul

MASTER_TILE_DICTIONARY = {
    'red': 0,
    "orange": 0,
    "yellow": 0,
    "green": 0,
    "blue": 0,
    "purple": 0
}


@pytest.fixture
def tile_dictionary_rybp():
    return {
        'red': 1,
        "orange": 0,
        "yellow": 3,
        "green": 0,
        "blue": 5,
        "purple": 3
    }


@pytest.fixture
def tile_dictionary_rybp_avail():
    return {'red': 1, 'yellow': 3, 'blue': 5, 'purple': 3}


@pytest.fixture
def tile_dictionary_ro():
    return {'red': 3, "orange": 1}


@pytest.fixture
def tile_dictionary_ro_full():
    return {
        'red': 3,
        "orange": 1,
        "yellow": 0,
        "green": 0,
        "blue": 0,
        "purple": 0
    }


@pytest.fixture
def tile_dictionary_both():
    return {'red': 4, "orange": 1, "yellow": 3, "blue": 5, "purple": 3}


@pytest.fixture
def printed_dictionary():
    return """red: 1\norange: 0\nyellow: 3\ngreen: 0\nblue: 5\npurple: 3"""


@pytest.fixture
def tower_w_tiles(tile_dictionary_rybp: dict):
    return azul.Tower(15, tile_dictionary_rybp)


@pytest.fixture
def fact_display(tile_dictionary_ro_full: dict):
    return azul.FactoryDisplay(4, tile_dictionary_ro_full)


@pytest.fixture
def tower_empty():
    return azul.Tower()


@pytest.fixture
def empty_center_of_table():
    return azul.CenterOfTable()


@pytest.fixture
def center_w_ro(tile_dictionary_ro_full:dict):
    return azul.CenterOfTable(4, tile_dictionary_ro_full)


@pytest.fixture
def supply_empty():
    return azul.Supply()

@pytest.fixture
def factory_w_displays(tile_dictionary_ro: dict):
    factory= azul.Factory(2)
    factory.populate_display(0, tile_dictionary_ro)
    factory.populate_display(1, tile_dictionary_ro)
    return factory

def test_print_dictionary(tile_dictionary_rybp:dict, printed_dictionary:str):
    assert azul.print_dict(tile_dictionary_rybp) == printed_dictionary


def test_dump_full_tower(tower_w_tiles:azul.Tower, tile_dictionary_rybp:dict):
    assert tower_w_tiles.dump_all_tiles() == tile_dictionary_rybp
    assert tower_w_tiles.get_available_tiles() == {}


def test_dump_empty_tower(tower_empty:azul.Tower):
    assert tower_empty.dump_all_tiles() == {}
    assert tower_empty.get_available_tiles() == {}


def test_tower_avail(tower_w_tiles: azul.Tower, tile_dictionary_rybp_avail:azul.Tower):
    assert tower_w_tiles.get_available_tiles() == tile_dictionary_rybp_avail


def test_add_tiles(tower_w_tiles:azul.Tower, tile_dictionary_ro: dict, tile_dictionary_both: dict):
    tower_w_tiles.add_tiles(tile_dictionary_ro)
    assert tower_w_tiles.get_available_tiles() == tile_dictionary_both


def test_get_available_no_wild(fact_display: azul.FactoryDisplay, tile_dictionary_ro:dict):
    assert fact_display.get_available_tiles('purple') == tile_dictionary_ro


def test_get_available_wild(fact_display: azul.FactoryDisplay):
    assert fact_display.get_available_tiles('orange') == {'red': 3}


def test_choose_tiles_no_wild(fact_display: azul.FactoryDisplay):
    assert fact_display.take_chosen_tiles('red', 'purple') == ({
        'red': 3
    }, {
        'red': 0,
        'orange': 1,
        'yellow': 0,
        'green': 0,
        'blue': 0,
        'purple': 0
    })
    assert fact_display.get_available_tiles('purple') == {}


def test_choose_tiles_wild(fact_display: azul.FactoryDisplay):
    assert fact_display.take_chosen_tiles('red', 'orange') == ({
        'red': 3,
        'orange': 1
    }, {
        'red': 0,
        'orange': 0,
        'yellow': 0,
        'green': 0,
        'blue': 0,
        'purple': 0
    })
    assert fact_display.get_available_tiles('orange') == {}


def test_take_center_tiles_no_wild(center_w_ro: azul.CenterOfTable):
    assert center_w_ro.take_center_tiles('red', 'purple') == ({'red': 3}, True)
    assert ~center_w_ro.get_first_player_avail()
    assert center_w_ro.get_available_tiles('purple') == {'orange': 1}


def test_take_center_tiles_w_wild(center_w_ro:azul.CenterOfTable):
    assert center_w_ro.take_center_tiles('red', 'orange') == ({
        'red': 3,
        'orange': 1
    }, True)
    assert ~center_w_ro.get_first_player_avail()
    assert center_w_ro.get_available_tiles('orange') == {}


def test_take_center_tiles_no_wild_no_fp(center_w_ro: azul.CenterOfTable):
    center_w_ro.first_player_avail = False
    assert center_w_ro.take_center_tiles('red', 'purple') == ({
        'red': 3
    }, False)
    assert ~center_w_ro.get_first_player_avail()
    assert center_w_ro.get_available_tiles('orange') == {'orange': 1}


def test_reset_first_player(center_w_ro: azul.CenterOfTable):
    center_w_ro.reset_first_player()
    assert center_w_ro.get_first_player_avail()


def test_fill_supply(supply_empty: azul.Supply, tile_dictionary_rybp: dict):
    supply_empty.fill_supply(tile_dictionary_rybp)
    assert supply_empty.get_tile_positions() == [
        'red', 'yellow', 'yellow', 'yellow', 'blue', 'blue', 'blue', 'blue',
        'blue', 'purple', 'purple', 'purple'
    ]
    assert supply_empty.get_tile_count() == 12


def test_legal_actions(supply_empty: azul.Supply, tile_dictionary_rybp: dict):
    supply_empty.fill_supply(tile_dictionary_rybp)
    assert supply_empty.get_legal_actions() == {
        0: ['red', 'supply_red'],
        1: ["yellow", 'supply_yellow'],
        2: ["yellow", 'supply_yellow'],
        3: ["yellow", 'supply_yellow'],
        4: ['blue', 'supply_blue'],
        5: ['blue', 'supply_blue'],
        6: ['blue', 'supply_blue'],
        7: ['blue', 'supply_blue'],
        8: ['blue', 'supply_blue'],
        9: ['purple', 'supply_purple'],
        10: ['purple', 'supply_purple'],
        11: ['purple', 'supply_purple']
    } 

def test_take_from_display_no_wild(factory_w_displays: azul.Factory):
    assert factory_w_displays.take_from_display(0, 'red', 'purple') == ({'red': 3}, False)
    assert factory_w_displays.get_center_tiles('purple') == {'orange': 1}

def test_take_from_display_wild(factory_w_displays: azul.Factory):
    assert factory_w_displays.take_from_display(0, 'red', 'orange') == ({'red': 3, 'orange': 1}, False)
    assert factory_w_displays.get_center_tiles('orange') == {}

