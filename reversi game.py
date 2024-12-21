from tkinter import *
import random
ai_or_human=input("Ai or Double player: ")
if ai_or_human.lower() ==  "ai":
    difficulty=input("Choose difficulty: hard or Easy ")
    ai_color=input("What color do you want to be: ")
class ReversiBoard:
    '''represents a board of Reversi'''

    def __init__(self):
        '''ReversiBoard()
        creates a ReversiBoard in starting position'''
        self.board = {}  # dict to store position
        # create opening position
        for row in range(8):
            for column in range(8):
                coords = (row, column)
                if coords in [(3, 3), (4, 4)]:
                    self.board[coords] = 1  # player 1
                elif coords in [(3, 4), (4, 3)]:
                    self.board[coords] = 0  # player 0
                else:
                    self.board[coords] = None  # empty
        self.currentPlayer = 0
        self.endgame = None  # replace with string when game ends

    def get_piece(self, coords):
        return self.board[coords]

    def get_endgame(self):
        return self.endgame

    def get_player(self):
        return self.currentPlayer

    def next_player(self):
        self.currentPlayer = 1 - self.currentPlayer

    def get_scores(self):
        pieces = list(self.board.values())  # list of all the pieces
        # count the number of pieces belonging to both players
        return pieces.count(0), pieces.count(1)

    def flip_pieces(self, coords, checkingOnly=False):
        '''ReversiBoard.flip_pieces(coords[checkingOnly]) -> int
        returns number of pieces flipped when a piece is played at coords
          checkingOnly True just computes, doesn't actually flip
          checkingOnly False also flips the pieces'''
        # get player colors
        thisPlayer = self.currentPlayer
        otherPlayer = 1 - thisPlayer
        flipped = 0  # counts flipped pieces
        # loop over the 8 possible directions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:  # non-direction
                    continue
                # look at the first square in the given direction
                (row, col) = (coords[0] + dr, coords[1] + dc)
                counter = 0  # keep track of how many squares have a
                             # piece of the opposite color
                # keep looking as long as we have pieces of the opposite
                #   color and we're still on the board
                while (0 <= row < 8) and (0 <= col < 8) and \
                      self.board[(row, col)] == otherPlayer:
                    (row, col) = (row + dr, col + dc) # continue moving in this direction
                    counter += 1  # increment the count of number of stones flipped
                # the next stone must be of the current player's color
                #  (and still on the board)
                if (0 <= row < 8) and (0 <= col < 8) and \
                   self.board[(row, col)] == thisPlayer:
                    # this direction will get flipped
                    flipped += counter  # update the overall flipped counter
                    if not checkingOnly:  # if not just checking, flip them!
                        for i in range(1, counter + 1):
                            self.board[(coords[0] + i*dr, coords[1] + i*dc)] = thisPlayer
        return flipped

    def get_legal_moves(self):
        moves = []  # place legal moves here
        for row in range(8):  # check each square
            for column in range(8):
                coords = (row, column)
                # if space is empty and would flip pieces
                if self.board[coords] is None and \
                   self.flip_pieces(coords, checkingOnly=True) > 0:
                    moves.append(coords)  # add to list
        return moves

    def try_move(self, coords):
        '''ReversiBoard.try_move(coords)
        places the current player's piece in the given square if the
          square is empty and the move is legal
        also flips necessary pieces and goes to other player's turn'''
        if self.board[coords] is not None:  # if square occupied
            return False  # move not valid
        # flip any pieces and check how many got flipped
        numFlipped = self.flip_pieces(coords)
        if numFlipped > 0:  # if any pieces flipped
            # set the current square to the current player's color
            self.board[coords] = self.currentPlayer
            self.next_player()  # next player's turn
            self.check_endgame()  # check if game over
        return numFlipped > 0  # tell ReversiGame if move was valid

    def computer_turn(self):
        legalMoves = self.get_legal_moves()
        if len(legalMoves) == 0:  # if no moves
            self.next_player()  # player passes
        else:
            self.try_move(random.choice(legalMoves))  # make random move

    def computer_turn_hard(self):
        global bestMoves
        legalMoves = self.get_legal_moves()
        if len(legalMoves) == 0:  # if no moves
            self.next_player()  # player passes
        else:
            bestMoveValue = -999  # initialize best move tracking variable
            for move in legalMoves:  # loop through all legal moves
                value = self.evaluate_coordinate(move)
                if value > bestMoveValue:  # if better
                    bestMoves = [move]  # start new list
                    bestMoveValue = value  # new best value
                elif value == bestMoveValue:  # just as good
                    bestMoves.append(move)  # add to list
            # randomly pick one of the best moves found
            self.try_move(random.choice(bestMoves))

    def check_endgame(self):
        # if current player has no legal move
        if len(self.get_legal_moves()) == 0:
            self.next_player()  # temporarily switch to next player
            # if other player has no legal move, game is over
            if len(self.get_legal_moves()) == 0:
                scores = self.get_scores()
                if scores[0] > scores[1]:
                    self.endgame = 0
                elif scores[0] < scores[1]:
                    self.endgame = 1
                else:
                    self.endgame = 'draw'
            self.next_player()  # return to original player

    def evaluate_coordinate(self, coords):
        '''ReversiBoard.evaluate_coordinate(coords) -> int
        returns the value of the (row, column) tuple coords'''
        coordValues = ((99, -8, 8, 6, 6, 8, -8, 99),
                       (-8, -24, -4, -3, -3, -4, -24, -8),
                       (8, -4, 7, 4, 4, 7, -4, 8),
                       (6, -3, 4, 0, 0, 4, -3, 6),
                       (6, -3, 4, 0, 0, 4, -3, 6),
                       (8, -4, 7, 4, 4, 7, -4, 8),
                       (-8, -24, -4, -3, -3, -4, -24, -8),
                       (99, -8, 8, 6, 6, 8, -8, 99))
        row, column = coords  # unpack coordinates
        return coordValues[row][column]
class ReversiSquare(Canvas):
    '''displays a square in the Reversi game'''

    def __init__(self, master, r, c):
        # create and place the widget
        Canvas.__init__(self, master, width=50, height=50, bg='medium sea green')
        self.grid(row=r, column=c)
        # set the attributes
        self.position = (r, c)
        # bind button click to placing a piece
        self.bind('<Button>', master.get_click)

    def get_position(self):
        return self.position

    def make_color(self, color):
        ovalList = self.find_all()  # remove existing piece
        for oval in ovalList:
            self.delete(oval)
        self.create_oval(10, 10, 44, 44, fill=color)

class ReversiGame(Frame):
    '''represents a game of Reversi'''

    def __init__(self, master, computerPlayer=None):
        '''ReversiGame(master, [computerPlayer])
        creates a new Reversi game
        computerPlayer is the computer player (2-player by default)'''
        # initialize the Frame
        Frame.__init__(self, master, bg='white')
        self.grid()
        # set up game data
        self.colors = ('black', 'white')  # players' colors
        # create the board and squares
        self.board = ReversiBoard()  # board in starting position
        # also sets player 0 to go first
        self.squares = {}  # stores ReversiSquares
        for row in range(8):
            for column in range(8):
                rc = (row, column)
                self.squares[rc] = ReversiSquare(self, row, column)
        # set up computer player
        if computerPlayer is not None:
            # equals X if player X is computer
            self.computerPlayer = self.colors.index(computerPlayer)
        else:
            self.computerPlayer = None  # no computer player
        # set up scoreboard and status markers
        self.rowconfigure(8, minsize=3)  # leave a little space
        self.turnSquares = []  # to store the turn indicator squares
        self.scoreLabels = []  # to store the score labels
        # create indicator squares and score labels
        for i in range(2):
            self.turnSquares.append(ReversiSquare(self, 9, 7*i))
            self.turnSquares[i].make_color(self.colors[i])
            self.scoreLabels.append(Label(self, text='2', font=('Arial', 18)))
            self.scoreLabels[i].grid(row=9, column=1+5*i)
        self.passButton = Button(self, text='Pass', command=self.pass_move)
        self.passButton.grid(row=9, column=3, columnspan=2)
        self.update_display()

    def get_click(self, event):
        coords = event.widget.get_position()
        # cannot move during computer's turn
        # calling try_move will make the move if it is valid
        if self.board.get_player() != self.computerPlayer and \
           self.board.try_move(coords):
            self.update_display()  # update the display

    def pass_move(self):
        self.board.next_player()  # move onto next player
        self.update_display()

    def take_computer_turn(self):
        if difficulty.lower()=="hard":
            self.board.computer_turn_hard()
        elif difficulty.lower()=="easy":
            self.board.computer_turn()
        self.update_display()

    def update_display(self):
        # update squares
        for row in range(8):
            for column in range(8):
                rc = (row, column)
                piece = self.board.get_piece(rc)
                if piece is not None:
                    self.squares[rc].make_color(self.colors[piece])
        # update the turn indicator
        newPlayer = self.board.get_player()
        oldPlayer = 1 - newPlayer
        self.turnSquares[newPlayer]['highlightbackground'] = 'blue'
        self.turnSquares[oldPlayer]['highlightbackground'] = 'white'
        # update the score displays
        scores = self.board.get_scores()
        for i in range(2):
            self.scoreLabels[i]['text'] = scores[i]
        # enable or disable the Pass button
        if len(self.board.get_legal_moves()) == 0:  # if no legal moves
            self.passButton.config(state=NORMAL)  # enable button
        else:  # if there are legal moves
            self.passButton.config(state=DISABLED)
        # if game over, show endgame message
        endgame = self.board.get_endgame()
        if endgame is not None:  # if game is over
            # remove the turn indicator
            self.turnSquares[newPlayer]['highlightbackground'] = 'white'
            # disable Pass button
            self.passButton.config(state=DISABLED)
            if isinstance(endgame, int):  # if a player won
                winner = self.colors[endgame]  # color of winner
                endgameMessage = '{} wins!'.format(winner.title())
            else:
                endgameMessage = "It's a tie!"
            Label(self, text=endgameMessage, font=('Arial', 18)).grid(row=9, column=2, columnspan=4)
        # if game not over and computer player's turn
        elif self.board.get_player() == self.computerPlayer:
            self.after(1000, self.take_computer_turn)

def play_reversi(computerPlayer=None):
    '''play_reversi()
    starts a new game of Reversi'''

    root = Tk()
    root.title('Reversi')
    RG = ReversiGame(root, computerPlayer)
    RG.mainloop()

if ai_or_human.lower() != "ai":
    play_reversi()

elif ai_color.lower()=="white":
    play_reversi("black")
elif ai_color.lower()=="black":
    play_reversi("white")
