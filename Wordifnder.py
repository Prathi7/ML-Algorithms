import copy
import random
import sys
from enum import Enum
from typing import Collection, List, NamedTuple, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

class GameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable. The `new_game` method
        should be called to initialize a playable game.

        Example
        -------
        ```
        dictionary: BoggleDictionary = ...
        game = GameManager()
        game.new_game(4, 2, "cubes.txt", dictionary)
        ```
        """
        pass
        # raise NotImplementedError("method __init__") # TODO: implement your code here

    def new_game(
        self, size: int, num_players: int, cubefile: str, dict: BoggleDictionary
    ) -> None:
        self.size = size
        self.num_players = num_players
        self.cubefile = cubefile
        self.dict = dict

        self.players_score = [0] * self.num_players
        self.players_dict = {} # Players dictionary
        for i in range(self.num_players):
            self.players_dict[i]=[]

        self.dict_all_words = []
        self.board_all_words = []


        self.cubes_list=[]

        with open(self.cubefile) as file:
            for line in file:
                line = line.strip().upper()
                self.cubes_list.append(str(line))
        self.game_board = [[0 for i in range(self.size)] for j in range(self.size)]
        self.board = [[0 for i in range(self.size)] for j in range(self.size)]
        while len(self.cubes_list) >= 1:
            for i in range(self.size):
                for j in range(self.size):
                    k = random.choice(self.cubes_list)
                    self.game_board[i][j]=random.choice(k)
                    self.cubes_list.remove(k)
        self.board = copy.deepcopy(self.game_board)

    def get_board(self) -> List[List[str]]:

        return self.board

    def add_word(self, word: str, player: int) -> int:
        self.score=0
        # word.upper()
        # self.last_added_word = None
        self.player = player
        if len(word.upper()) >= 4:
            if word.upper() not in self.players_dict[self.player]:
                if self.dict.contains(word.upper()):
                    if self.valid_board_word(word.upper()):
                        self.score = len(word.upper())-3
                        self.players_dict[self.player].append(word.upper())
                        self.last_added_word = word.upper()
                        self.players_score[self.player] += len(word.upper())-3
        return self.score
        # raise NotImplementedError("method add_word") # TODO: implement your code here

    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        return self.pos_last_word
        # raise NotImplementedError("method get_last_added_word") # TODO: implement your code here

    def set_game(self, board: List[List[str]]) -> None:

        self.board = board

        assert len(self.board) == self.size

        for row in range(len(self.board)):
            assert len(self.board[row]) == self.size

        self.players_score = [0] * self.num_players
        for i in range(self.num_players):
            self.players_dict[i]=[]

        self.last_added_word = None

        self.dict_all_words = []
        self.board_all_words = []
        # raise NotImplementedError("method set_game") # TODO: implement your code here

    def get_all_words(self) -> Collection[str]:
        """Return a collection containing all valid words in the current
        Boggle board.

        Uses the current search tactic.

        This is a sample implementation provided to make the project easier.
        You can delete this if you don't want to use it.
        """

        self.set_search_tactic(BoggleGame.SearchTactic.SEARCH_BOARD)
        # self.set_search_tactic(BoggleGame.SearchTactic.SEARCH_DICT)
        if self.tactic == BoggleGame.SearchTactic.SEARCH_BOARD:
            return self.__board_driven_search()
        else:
            return self.__dictionary_driven_search()

    def set_search_tactic(self, tactic: BoggleGame.SearchTactic) -> None:
        """Set the search tactic to the given tactic.

        This tactic is used by `get_all_words()`. Valid tactics are
        defined in BoggleGame.SearchTactic.
        """
        self.tactic = tactic

    def get_scores(self) -> List[int]:

        return self.players_score

    def __dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board.
        """
        self.dict_all_words = []
        for i in self.dict.nlist:
            if len(i) >= 4:
                if self.valid_board_word(i):
                    self.dict_all_words.append(i)

        return set(self.dict_all_words)

        # raise NotImplementedError("method __dictionary_driven_search") # TODO: implement your code here

    def __board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board.
        """
        # raise NotImplementedError("method __board_driven_search") # TODO: implement your code here

        self.board_all_words = []
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                path = [(i,j)]
                word = self.board[i][j]
                self.board_dfs(i, j,word,path)

        return set(self.board_all_words)

    def valid_board_word(self,word: str):
        l = []
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i][j] == word[0]:
                    l.append((i, j))
        if len(l) == 0:
            return False
        else:
            for i,j in l:
                visited = [[False for i in range(4)] for i in range(4)]
                k=[(i,j)]
                flag = self.dfs(i,j,word,k,visited)
                self.track = []
                if flag == True:
                    return True
        return False

    def dfs(self, r, c, word: str, k, visited):
        if len(word) <= 1:
            self.pos_last_word = k
            return True
        else:
            visited[r][c] = True
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    nr = r + i
                    nc = c + j
                    if 0 <= nr < self.size and 0 <= nc < self.size and not (i == j == 0):
                        if not visited[nr][nc] and self.board[nr][nc] == word[1:][0]:
                            flag = self.dfs(nr, nc, word[1:], k+[(nr,nc)], visited)
                            if flag == True:
                                return True
        return False

    def board_dfs(self, r, c, word: str, path):

        if len(word) > self.size*self.size:
            return
        if not self.dict.is_prefix(word):
            return
        if self.dict.contains(word) and len(word) >= 4:
            self.board_all_words.append(word)
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                nr = r+i
                nc = c+j
                if 0 <= nr < self.size and 0 <= nc < self.size and not (i == j == 0):
                    if (nr, nc) not in path:
                        self.board_dfs(nr, nc, word+self.board[nr][nc], path + [(nr, nc)])
        return
