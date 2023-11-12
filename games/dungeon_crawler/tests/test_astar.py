from games.dungeon_crawler.actor import astar


class TestAStar:
    @classmethod
    def setup_class(cls):
        # Example map
        cls.map = [
            [0, 0, 0, 0, 1],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

    def test_valid_path(self):
        start_node = (0, 0)
        end_node = (4, 4)
        path = astar(self.map, start_node, end_node)
        expected_paths = [
            [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 4), (2, 4), (3, 4), (4, 4)],
            [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (3, 3), (3, 4), (4, 4)],
            [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2), (4, 3), (4, 4)],
            [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4)],
        ]
        assert path in expected_paths

    def test_no_path(self):
        start_node = (0, 0)
        end_node = (1, 1)
        path = astar(self.map, start_node, end_node)
        assert path is None

    def test_start_equals_end(self):
        start_node = (2, 2)
        end_node = (2, 2)
        path = astar(self.map, start_node, end_node)
        assert path == [(2, 2)]

    def test_invalid_start(self):
        start_node = (-1, 0)
        end_node = (4, 4)
        path = astar(self.map, start_node, end_node)
        assert path is None

    def test_invalid_end(self):
        start_node = (0, 0)
        end_node = (5, 4)
        path = astar(self.map, start_node, end_node)
        assert path is None
