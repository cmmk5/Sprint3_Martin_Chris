import unittest

from solitaire import (
    DiamondBoard,
    EnglishBoard,
    HexagonBoard,
    IllegalMoveError,
    Move,
    SolitaireGame,
)


class ManualGameTests(unittest.TestCase):
    def test_all_board_types_and_sizes_start_with_empty_center(self):
        configurations = {
            "English": (EnglishBoard, (9, 33, 45)),
            "Hexagon": (HexagonBoard, (19, 37, 61)),
            "Diamond": (DiamondBoard, (13, 25, 41)),
        }
        for name, (board_class, hole_counts) in configurations.items():
            for size, hole_count in zip((5, 7, 9), hole_counts):
                with self.subTest(board=name, size=size):
                    game = SolitaireGame(name, size)
                    center = (size // 2, size // 2)
                    self.assertIsInstance(game.board, board_class)
                    self.assertEqual(len(game.holes), hole_count)
                    self.assertIn(center, game.holes)
                    self.assertEqual(game.pegs, game.holes - {center})

    def test_unsupported_board_configuration_is_rejected(self):
        for board_type, size in (("Triangle", 7), ("English", 6)):
            with self.subTest(board=board_type, size=size):
                with self.assertRaises(ValueError):
                    SolitaireGame(board_type, size)

    def test_illegal_jump_leaves_peg_state_unchanged(self):
        game = SolitaireGame()
        before = game.pegs
        with self.assertRaises(IllegalMoveError):
            game.move((3, 0), (3, 3))
        self.assertEqual(game.pegs, before)
        self.assertFalse(game.undo())

    def test_jump_directions_depend_on_board_type(self):
        for board_type in ("English", "Diamond", "Hexagon"):
            with self.subTest(board=board_type):
                game = SolitaireGame(board_type, pegs={(2, 2), (3, 3)})
                self.assertIn((4, 4), game.holes)
                jump = Move((2, 2), (4, 4))
                if board_type == "Hexagon":
                    self.assertNotIn(jump, game.legal_moves())
                else:
                    game.move(jump.start, jump.end)
                    self.assertEqual(game.pegs, {(4, 4)})

        hexagon = SolitaireGame("Hexagon", pegs={(2, 4), (3, 3)})
        hexagon.move((2, 4), (4, 2))
        self.assertEqual(hexagon.pegs, {(4, 2)})

    def test_rating_appears_after_final_manual_jump(self):
        game = SolitaireGame(pegs={(1, 3), (2, 3)})
        self.assertIsNone(game.rating())
        game.move((1, 3), (3, 3))
        self.assertEqual(game.remaining, 1)
        self.assertEqual(game.legal_moves(), [])
        self.assertEqual(game.rating(), "Outstanding")

    def test_terminal_ratings_for_two_or_more_pegs(self):
        isolated = [(0, 3), (3, 0), (3, 6), (6, 3)]
        for count, rating in ((2, "Very Good"), (3, "Good"), (4, "Average")):
            with self.subTest(count=count):
                game = SolitaireGame(pegs=set(isolated[:count]))
                self.assertEqual(game.legal_moves(), [])
                self.assertEqual(game.rating(), rating)

    def test_undo_final_jump_reopens_play(self):
        original = {(1, 3), (2, 3)}
        game = SolitaireGame(pegs=original)
        game.move((1, 3), (3, 3))
        self.assertTrue(game.undo())
        self.assertEqual(game.pegs, original)
        self.assertIsNone(game.rating())

    def test_new_model_does_not_inherit_move_history(self):
        previous = SolitaireGame()
        previous.move((1, 3), (3, 3))
        game = SolitaireGame(previous.board_type, previous.size)
        self.assertEqual(game.remaining, 32)
        self.assertNotIn((3, 3), game.pegs)
        self.assertFalse(game.undo())
