from re import search
from chessBoard import Chessboard, Chesspiece, Pawn, King, Queen, Bishop, Knight, Rook

class Chessgame:
    def __init__(self, boardObj: Chessboard) -> None:
        self.boardObj = boardObj
        self.turn = 'white'
        self.move = 0 # per one piece moved / captured

    def gameLoop(self):
        """main method for the game"""
        while True:
            # check for check / checkmate
            check, mate = self.inCheck()
            if check and mate:
                self.switchTurns(False)
                self.boardObj.printBoard()
                print(f'{self.turn} won! After {self.move} individual moves!')
                break
            elif check:
                print('You can only capture the checking piece or move', end='')
                print(' your king.\n')

            self.boardObj.printBoard()
            play = input(f'{self.turn.title()} what move would you like to play?\n>').strip()
            if play == '':
                print("That's definitely not a valid move!")
                continue
            elif play == 'pass':
                self.switchTurns(False)
                continue
            elif play == 'reset':
                self.reset()
                continue
            elif play == 'exit':
                break
            elif play == 'reverse':
                self.boardObj.reverseBoard()
                continue
            elif play == 'O-O' or play == 'O-O-O':
                if len(play) == 3:
                    self.castles()
                else:
                    self.qCastles()
                self.switchTurns()
                continue

            # handle normal chess move
            movePiece = self.getPieceToMove(move=play, color=self.turn)
            if movePiece:
                play = play[-2:] # remove the piece from the move

                # remove before move because you change the pos tuple in move
                self.removePiece(movePiece.pos[0], movePiece.pos[1])
                self.movePiece(movePiece, move=play)
            
            self.switchTurns()

    def getPieceToMove(self, move: str, color: str):
        """this method handles converting which piece to move and corresponding\n
        it to a piece on the actual Chessboard, if there is nothing found, this\n
        method will return None, else it will return the piece to move"""
        firstChar = move[0]
        if search('[a-h]', firstChar):
            # sometimes you have to specify the file but the position is 
            # guaranteed to be the last two indices of the move string
            rawMove = move
            move = move[-2:]
            
            # find all the pawns on the board
            pawns = self.boardObj.searchBoard(Pawn)
            # limit your pawns to only your color
            pawns = [pawn for pawn in pawns if pawn.color == color]
            
            for pawn in pawns:
                if 'x' in rawMove:
                    correctFile = rawMove[0]
                    thisFile = self.boardObj.files[pawn.pos[1]]
                    if pawn.canMoveTo(move, self.boardObj) and correctFile == thisFile:
                        return pawn
                else:
                    # this returns the first pawn that can move to that position
                    if pawn.canMoveTo(move, self.boardObj):
                        return pawn
        
        elif firstChar == 'K': # king
            # if the King is capturing don't do anything different
            # it's just unnecessary to know in chess notation because
            # it's reflected on the board
            move = move.replace('x', '')
            king = self.boardObj.getKing(color)
            if king.canMoveTo(move[1:], self.boardObj):
                return king

        elif firstChar == 'Q': # queen
            move = move.replace('x', '')
            queens = self.boardObj.searchBoard(Queen)
            queen = [queen for queen in queens if queen.color == color]
            if queen:                       # if there is a queen
                queen = queen[0]            # get your queen
                if queen.canMoveTo(move[1:], self.boardObj):
                    return queen

        elif firstChar == 'B': # bishop
            move = move.replace('x', '')
            bishops = self.boardObj.searchBoard(Bishop)
            bishops = [bishop for bishop in bishops if bishop.color == color]
            for bishop in bishops:
                if bishop.canMoveTo(move[1:], self.boardObj):
                    return bishop
             
        elif firstChar == 'N': # knight
            knights = self.boardObj.searchBoard(Knight)
            knights = [knight for knight in knights if knight.color == color]
            if len(move) == 5:
                # make sure it's the right file Knight
                correctFile = move[1]
                for knight in knights:
                    thisFile = self.boardObj.files[knight.pos[1]]
                    if knight.canMoveTo(move[-2:], self.boardObj) and correctFile == thisFile:
                        return knight
            else:
                move = move.replace('x', '')
                for knight in knights:
                    if knight.canMoveTo(move[1:], self.boardObj):
                        return knight

        elif firstChar == 'R': # rook
            move = move.replace('x', '')
            rooks = self.boardObj.searchBoard(Rook)
            rooks = [rook for rook in rooks if rook.color == color]
            for rook in rooks:
                if rook.canMoveTo(move[1:], self.boardObj):
                    return rook

    def movePiece(self, piece: Chesspiece, move: str):
        """This moves the inputed piece to the chess notation move\nDoesn't
        account for removing the piece, call removePiece()"""
        indexes = self.moveToIndexes(move)
        if isinstance(piece, Pawn) or isinstance(piece, Rook):
            piece.hasMoved = True
        piece.pos = (indexes[0], indexes[1])
        self.boardObj.board[indexes[0]][indexes[1]] = piece

    def moveToIndexes(self, move: str) -> tuple:
        """This converts the chess notation to row, col format"""
        positions = self.boardObj.positions
        for i in range(len(positions)):
            for j in range(len(positions[i])):
                if positions[i][j] == move:
                    return (i, j)
        return ()
    
    def removePiece(self, row: int, col: int):
        """remove a piece on the board at row, col\nVoid method"""
        self.boardObj.board[row][col] = Chesspiece(row, col)
    
    def switchTurns(self, countMove=True):
        """switches the turns, increments move, creates readable output of board"""
        self.turn = 'white' if self.turn != 'white' else 'black'
        if countMove:
            self.move += 1 # one move has passed
            print('\n------------------------------\n')
    
    def reset(self):
        """Resets the board and puts the turn back to white"""
        self.boardObj = Chessboard()
        self.turn = 'white'
        self.move = 0

    def castles(self):
        """O-O in chess notation, this moves the king and the rook"""
        color = self.turn
        if self.boardObj.checkForCastle(color, True):
            king, rook = self.getKingAndRook(distance=3)

            if self.checkBetween(king, rook):
                self.removeAndMovePieces(king, rook, -2, -2)

    def qCastles(self):
        """O-O-O in chess notation, this moves the king and the rook"""
        color = self.turn
        if self.boardObj.checkForCastle(color, False):
            king, rook = self.getKingAndRook(distance=4)
            
            if self.checkBetween(king, rook):
                self.removeAndMovePieces(king, rook, 2, 3)

    def getKingAndRook(self, distance):
        """Used for castling"""
        color = self.turn
        kings = self.boardObj.searchBoard(King)
        king = [king for king in kings if king.color == color][0]
        rooks = self.boardObj.searchBoard(Rook)
        rooks = [rook for rook in rooks if rook.color == color]
        rook = None
        for piece in rooks:
            if self.boardObj.distanceKingToRook(color, piece) == distance:
                rook = piece
        return king, rook

    def checkBetween(self, king, rook):
        """Used for castling"""
        between = self.boardObj.piecesBetweenRookKing(king, rook)
        for piece in between:
            if piece != '~':
                return False
        return True

    def removeAndMovePieces(self, king, rook, kingOffset: int, rookOffset: int):
        """Used for castling"""
        row, col = king.pos
        rRow, rCol = rook.pos
        self.removePiece(row, col)
        self.removePiece(rRow, rCol)
        positions = self.boardObj.positions
        
        
        if self.boardObj.isReversed:
            self.movePiece(king, positions[row][col + kingOffset])
            self.movePiece(rook, positions[rRow][rCol - rookOffset])
        else:
            self.movePiece(king, positions[row][col - kingOffset])
            self.movePiece(rook, positions[rRow][rCol + rookOffset])

    def inCheck(self) -> tuple:
        """True if in check"""
        color = self.turn
        enemyColor = 'white' if color == 'black' else 'black'
        king = self.boardObj.getKing(color)
        kingSquare = self.boardObj.positions[king.pos[0]][king.pos[1]]
        
        # check for pieces that can move to king square
        diagonals = king.checkDiagonals(self.boardObj)
        horizontals = king.checkFileHor(self.boardObj)
        verticals = king.checkFileVer(self.boardObj)
        knights = king.checkKnightMoves(self.boardObj)
        enemies = self.checkEnemies(diagonals, color, enemyColor)
        enemies += self.checkEnemies(horizontals, color, enemyColor)
        enemies += self.checkEnemies(verticals, color, enemyColor)
        enemies += self.checkEnemies([knights], color, enemyColor)

        # see if enemies can move to kingSquare
        # therefore in check
        for enemy in enemies:
            if enemy.canMoveTo(kingSquare, self.boardObj):
                
                enemySquare = self.boardObj.positions[enemy.pos[0]][enemy.pos[1]]
                possible = king.getPossibleMoves(self.boardObj)
                spaces = 0
                # check to see if the enemy piece can move to all the kin g's moves
                # and not just the enemy square
                for move in possible:
                    if enemy.canMoveTo(move, self.boardObj):
                        spaces += 1
                    elif move == enemySquare:
                        spaces += 1
                
                if spaces == len(possible):
                    return True, True
                else:
                    return True, False

        return False, False
    

    def checkEnemies(self, master: list, color, enemyColor):
        enemies = []
        for pieces in master:
            for piece in pieces:
                if piece.color == color:
                    break
                elif piece.color == enemyColor:
                    enemies.append(piece)
                    break

        return enemies
        
if __name__ == "__main__":     
    game = Chessgame(Chessboard())
    game.gameLoop()
