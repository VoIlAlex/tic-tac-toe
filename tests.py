from tic_tac_toe import Board


class TestBoard:
    def test_free(self):
        board = Board()
        board.update((0, 0), circle=True)
        assert board.is_free((0, 0)) == False
        assert board.is_free((1, 0)) == True

    def test_state(self):
        board = Board()
        board.update((0, 0), circle=True)
        board.update((0, 1), circle=True)
        board.update((0, 2), circle=True)
        assert board.game_state == board.CIRCLE_WON
