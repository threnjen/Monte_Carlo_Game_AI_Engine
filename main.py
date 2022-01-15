master_tile_dictionary = {'red': 0, "green": 0,
                          "orange": 0, "yellow": 0, "blue": 0, "purple": 0}


class tower(object):
    __init__(self, tile_count=0):
        self.tile_count = tile_count
        self.tile_dictionary = master_tile_dictionary.copy()

    def add_tiles(self, new_tiles):

        for key in new_tiles.keys():
            if key in self.tile_dictionary:
                self.tile_dictionary[key] += new_tiles[key]
            else:
                raise "Error:  invalid tilename passed to tower"

    def remove_tiles(self):

        dump_tiles = self.tile_dictionary.copy()
        self.tile_dictionary = master_tile_dictionary.copy()
        return dump_tiles
