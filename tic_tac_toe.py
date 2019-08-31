import cv2
import numpy as np
import time
import imutils


__all__ = ['Game']


class Board:
    NO_ONE = 0
    CIRCLE_WON = 1
    CROSS_WON = 2
    WINDOW_NAME = 'Game'
    CIRCLE = 1
    CROSS = 2
    EMPTY = 0
    H, W = 500, 500

    def __init__(self):
        # here we paint
        self.CROSS_COLOR = (0, 0, 0)
        self.CIRCLE_COLOR = (0, 0, 0)
        self.area = np.ones(shape=(Board.H, Board.W), dtype='uint8') * 255
        self._paint_borders()
        # this is logical state of our board
        # circle    = 1
        # cross     = 2
        # empty     = 0
        self.board_state = np.zeros(shape=(3, 3), dtype='int')
        self.game_state = None

    def is_free(self, pos: tuple) -> bool:
        if self.board_state[pos[0], pos[1]]:
            return False
        else:
            return True

    def _update_game_state(self):
        '''
        Here I want to update self.game_state
        It's going to get value: None, Board.NO_ONE, Board.PLAYER_WON, Board.BOT_WON
        :return:
        '''
        # horizontal
        for i in range(3):
            winner = self.board_state[i, 0]
            if winner == 0:
                continue
            for j in range(3):
                if self.board_state[i, j] != winner:
                    break
            else:
                self.game_state = winner

        # vertical
        for j in range(3):
            winner = self.board_state[0, j]
            if winner == 0:
                continue
            for i in range(3):
                if self.board_state[i, j] != winner:
                    break
            else:
                self.game_state = winner

        # first diagonal
        if self.board_state[0, 0] == self.board_state[1, 1] == self.board_state[2, 2] != 0:
            self.game_state = self.board_state[1, 1]

        # second diagonal
        if self.board_state[2, 0] == self.board_state[1, 1] == self.board_state[0, 2] != 0:
            self.game_state = self.board_state[1, 1]

        if self.board_state.all():
            self.game_state = Board.NO_ONE

    def _paint_borders(self):
        cv2.line(self.area, (Board.W // 3, 0),
                 (Board.W // 3, Board.H), (0, 0, 0), 3)
        cv2.line(self.area, (2 * Board.W // 3, 0),
                 (2 * Board.W // 3, Board.H), (0, 0, 0), 3)

        cv2.line(self.area, (0, Board.H // 3),
                 (Board.W, Board.H // 3), (0, 0, 0), 3)
        cv2.line(self.area, (0, 2 * Board.H // 3),
                 (Board.W, 2 * Board.H // 3), (0, 0, 0), 3)

    def update(self, pos: tuple, circle: bool) -> bool:
        if self.board_state.all():
            return False

        # board cell is occupied
        if self.board_state[pos[0], pos[1]]:
            return False

        cell_size = self.area.shape[0] // 3
        x1, y1 = pos[0] * cell_size, pos[1] * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size

        if circle:
            self.board_state[pos[0], pos[1]] = 1
            center = ((x2 + x1) // 2, (y1 + y2) // 2)
            cv2.circle(self.area, center, cell_size // 2, self.CIRCLE_COLOR, 3)

        else:
            self.board_state[pos[0], pos[1]] = 2
            cv2.line(self.area, (x1, y1), (x2, y2), self.CROSS_COLOR, 3)
            cv2.line(self.area, (x1, y2), (x2, y1), self.CROSS_COLOR, 3)

        self._update_game_state()
        return True

    def update_by_coordinates(self, real_pos: tuple, circle: bool) -> bool:
        cell_size = self.area.shape[0] // 3
        pos = real_pos[0] // cell_size, real_pos[1] // cell_size
        return self.update(pos, circle)

    def display(self):
        cv2.imshow(Board.WINDOW_NAME, self.area)

    def display_game_over_message(self):
        self.area = np.ones_like(self.area) * 255
        text_coord = (self.area.shape[0] // 2 - 100, self.area.shape[1] // 2)
        if self.game_state == Board.CROSS_WON:
            cv2.putText(self.area, 'Cross won', text_coord,
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        elif self.game_state == Board.NO_ONE:
            cv2.putText(self.area, 'No one won', text_coord,
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        elif self.game_state == Board.CIRCLE_WON:
            cv2.putText(self.area, 'Circles won', text_coord,
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

    def reload(self):
        self.area = np.ones_like(self.area) * 255
        self.board_state = np.zeros_like(self.board_state)
        self.game_state = None
        self._paint_borders()

    def get_free_positions(self):
        positions = []
        for i in range(3):
            for j in range(3):
                if self.is_free((i, j)):
                    positions.append((i, j))
        return positions


class Bot:
    @staticmethod
    def turn(board: Board):
        free_positions = board.get_free_positions()
        if not free_positions:
            return
        idx = np.random.randint(0, len(free_positions))
        board.update(free_positions[idx], False)


class Game:
    def __init__(self):
        self.flag_bot_turn = False
        self.board = Board()

    def player_callback(self, event, x, y, *args):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.flag_bot_turn:
                return
            if not self.board.update_by_coordinates((x, y), circle=True):
                if self.board.game_state is not None:
                    self.board.reload()
                return
            self.board.display()
            self.flag_bot_turn = True

    def main_loop(self):
        self.board.display()
        cv2.setMouseCallback(Board.WINDOW_NAME, self.player_callback)
        while True:
            # game_state is not None if game is over
            if self.board.game_state is not None:
                self.board.display_game_over_message()
            self.board.display()
            key = cv2.waitKey(10)
            if key == ord('q'):
                break
            if not self.flag_bot_turn:
                continue
            Bot.turn(self.board)
            self.flag_bot_turn = False


def _test1():
    b = Board()
    b.display()
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def _test2():
    b = Board()
    b.update((0, 0), circle=True)
    b.update((2, 0), circle=False)
    b.display()
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def _test3():
    b = Board()
    print('Initial game state: ', b.game_state)
    b.update((0, 0), True)
    b.update((1, 1), True)
    b.update((2, 2), True)
    b.display()
    print('Final game state: ', b.game_state)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # _test1()
    # _test2()
    # _test3()
    pass
