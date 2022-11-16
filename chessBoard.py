
class Chesspiece:
    def __init__(self, row=-1, col=-1) -> None:
        self.strRep = '~'
        self.color = None
        self.pos = (row, col)
    
    def __str__(self):
        return self.strRep
    
    def __eq__(self, other):
        return True if self.strRep == other else False

    def canMoveTo(self, move: str, chessboard):
        return False # just so my program doesn't get confused

    def checkKnightMoves(self, chessboard):
        row, col = self.pos
        up = row + 2
        down = row - 2
        left = col - 2
        right = col + 2
        coords = [
                    (up, col + 1), (up, col - 1),
            (row + 1, left),            (row + 1, right),
            (row - 1, left),            (row - 1, right),
                  (down, col + 1), (down, col - 1)
        ]

        coords = [
            (row, col) for row, col in coords 
            if chessboard.isOnBoard(row, col)
        ]

        return [chessboard.board[row][col] for row, col in coords]
    
    # this is a fundamental moving technique for multiple pieces
    def checkDiagonals(self, chessboard):
        # four diagonals we need to take into account
        row, col = self.pos
        downRight, downLeft, upRight, upLeft = [], [], [], []

        for i in range(1,8): # in any position can only have at most 7 diagonal moves
            if chessboard.isOnBoard(row + i, col + i):
                downRight.append(chessboard.board[row + i][col + i]) # downRight

            if chessboard.isOnBoard(row + i, col - i):
                downLeft.append(chessboard.board[row + i][col - i])  # downLeft

            if chessboard.isOnBoard(row - i, col + i):
                upRight.append(chessboard.board[row - i][col + i])   # upRight

            if chessboard.isOnBoard(row - i, col - i):
                upLeft.append(chessboard.board[row - i][col - i])    # upLeft  

        return [downRight, downLeft, upRight, upLeft]

    def checkFileHor(self, chessboard):
        # start from this piece pos, check left and right of it in row
        row, col = self.pos  # position of this piece
        allPieces = [chessboard.board[row][i] for i in range(8)]
        leftPieces = allPieces[:col]
        rightPieces = allPieces[col + 1:]
        leftPieces.reverse() # want the first element to be the first after this piece

        return [leftPieces, rightPieces]

    def checkFileVer(self, chessboard):
        # column will not change but need to see what's in all the rows
        row, col = self.pos
        columnPieces = [chessboard.board[i][col] for i in range(8)]
        aboveThis = columnPieces[:row]
        belowThis = columnPieces[row + 1:]
        aboveThis.reverse() 
        
        return [aboveThis, belowThis]

    # I have to do this for ever chess move
    def checkMoves(self, check: list, chessboard):
        possibleMoves = []
        for list in check:
            for piece in list:
                if piece == '~':
                    possibleMoves.append(piece)
                elif piece.color != self.color:
                    possibleMoves.append(piece)
                    break
                else:
                    break
        # now convert the valid moves into chess notation to check the move
        if possibleMoves:
            notation = chessboard.positions # p for piece
            possibleMoves = [notation[p.pos[0]][p.pos[1]] for p in possibleMoves]
        
        return possibleMoves

class Chessboard:
    isReversed = False
    positions = [
        [chr(97+i) + str(j) for i in range(0,8)]
        for j in range(8, 0, -1)
    ]
    files = [chr(97+i) for i in range(0,8)]
    

    def __init__(self) -> None:
        self.board = [[Chesspiece() for i in range(8)] for j in range(8)]
        self.setBackrows()
        self.setPawnRows()
        self.setAllPositions()

    def setBackrows(self):
        backrow = lambda color : [
            Rook(color), Knight(color), Bishop(color), Queen(color), 
            King(color), Bishop(color), Knight(color), Rook(color)
        ]

        whiteBackrow = backrow('white')
        blackBackrow = backrow('black')
        self.board[7] = whiteBackrow
        self.board[0] = blackBackrow

    def setPawnRows(self):
        pawns = lambda color : [
            Pawn(color), Pawn(color), Pawn(color), Pawn(color),
            Pawn(color), Pawn(color), Pawn(color), Pawn(color)
        ]

        whitePawns = pawns('white')
        blackPawns = pawns('black')
        self.board[6] = whitePawns
        self.board[1] = blackPawns

    def setAllPositions(self):
        """Set all the chesspiece's stored pos to their current row and col"""
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                self.board[i][j].pos = (i, j)

    def printBoard(self):
        for i in range(8):
            for j in range(8):
                print(self.board[i][j], end=' ')
            print()
    
    def printPositions(self):
        """Prints the squares on the board in chess notation"""
        for row in self.positions:
            for square in row:
                print(square, end=' ')
            print()

    def printPiecesPos(self):
        for row in self.board:
            for piece in row:
                print(piece.pos, end=' ')
            print()

    def reverseBoard(self):
        self.board.reverse()
        for list in self.board:
            list.reverse()
        # want the positons to correspond to the actual board too
        self.positions.reverse()
        for list in self.positions:
            list.reverse()
        self.files.reverse()
        # handle the double reverses
        self.isReversed = False if self.isReversed else True
        # make sure the pieces know their positions!
        self.setAllPositions()

    def searchBoard(self, target: Chesspiece):
        # linear search top to bottom, because there is no way to know where
        # the pieces are with high level of certainty, well at least for me
        pieces = []
        for row in self.board:
            for piece in row:
                # ex. if piece is instance of Pawn then add piece to list
                if isinstance(piece, target):
                    pieces.append(piece)
        return pieces
    
    def isOnBoard(self, row: int, col: int):
        # row == 0-7   col == 0-7
        rowCheck = 0 <= row < 8
        colCheck = 0 <= col < 8
        return True if rowCheck and colCheck else False

    def checkForCastle(self, color, kingside: bool):
        # check for space between rook and king of some color
        # make sure rook is on the board
        rooks = self.searchBoard(Rook)
        rooks = [rook for rook in rooks if rook.color == color]
        rooks = [rook for rook in rooks if not rook.hasMoved]
        if rooks:
            if kingside:
                rook = [rook for rook in rooks if self.distanceKingToRook(color, rook) == 3]
            else:
                rook = [rook for rook in rooks if self.distanceKingToRook(color, rook) == 4]
    
            if len(rook) != 0:
                return True

        return False

    def distanceKingToRook(self, color, rook: Chesspiece):
        kings = self.searchBoard(King)
        king = [king for king in kings if king.color == color][0]
        # same row
        kingCol = king.pos[1]
        rookCol = rook.pos[1]
        # difference between kingside and queenside
        # 7 - 4 = 3
        # 0 - 4 = 4
        return abs(rookCol - kingCol)

    def piecesBetweenRookKing(self, king, rook):
        # given that they are on the same row
        # start the search at the lesser columns position
        startCol = king.pos[1] if king.pos[1] < rook.pos[1] else rook.pos[1]
        stopCol = king.pos[1] if king.pos[1] > rook.pos[1] else rook.pos[1]
        row = king.pos[0]
        pieces = []
        for col in range(startCol + 1, stopCol):
            pieces.append(self.board[row][col])
        return pieces

    def getKing(self, color):
        kings = self.searchBoard(King)
        king = [king for king in kings if king.color == color][0]
        return king

class Rook(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        self.hasMoved = False
        if color == 'white':
            self.strRep = '♜'
        else:
            self.strRep = '♖'

    def canMoveTo(self, move: str, chessboard: Chessboard):
        horizontalMoves = self.checkFileHor(chessboard)
        verticalMoves = self.checkFileVer(chessboard)
        checkMoves = horizontalMoves + verticalMoves
        possibleMoves = self.checkMoves(checkMoves, chessboard)
        return True if move in possibleMoves else False

class Knight(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        if color == 'white':
            self.strRep = '♞'
        else:
            self.strRep = '♘'

    def canMoveTo(self, move: str, chessboard: Chessboard):
        checkMoves = self.checkKnightMoves(chessboard)
        possibleMoves = []
        for piece in checkMoves:
            if piece == '~' or piece.color != self.color:
                possibleMoves.append(piece)

        # now convert the valid moves into chess notation to check the move
        if possibleMoves:
            notation = chessboard.positions # p for piece
            possibleMoves = [notation[p.pos[0]][p.pos[1]] for p in possibleMoves]

        return True if move in possibleMoves else False

class Bishop(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        if color == 'white':
            self.strRep = '♝'
        else:
            self.strRep = '♗'

    def canMoveTo(self, move: str, chessboard: Chessboard):
        checkMoves = self.checkDiagonals(chessboard)
        possibleMoves = self.checkMoves(checkMoves, chessboard)
        return True if move in possibleMoves else False

class Queen(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        if color == 'white':
            self.strRep = '♛'
        else:
            self.strRep = '♕'

    def canMoveTo(self, move: str, chessboard: Chessboard):
        horizontalMoves = self.checkFileHor(chessboard)
        verticalMoves = self.checkFileVer(chessboard)
        diagonalMoves = self.checkDiagonals(chessboard)
        # now we have to check if the moves are legitimate
        checkMoves = horizontalMoves + verticalMoves + diagonalMoves
        possibleMoves = self.checkMoves(checkMoves, chessboard)
        return True if move in possibleMoves else False

class King(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        if color == 'white':
            self.strRep = '♚'
        else:
            self.strRep = '♔'

    def getPossibleMoves(self, chessboard: Chessboard):
        possibleMoves = []
        row, col = self.pos
        left, right = col - 1, col + 1
        up, down = row - 1,  row + 1

        coords = [ # all eight spaces around king
            (up, left),   (up, col),   (up, right), 
            (row, left),               (row, right), 
            (down, left), (down, col), (down, right)
        ]
        for coord in coords:
            row, col = coord # row, col of this coord
            onBoard = chessboard.isOnBoard(row, col)
            if onBoard: # can't access what isn't on the board
                empty = chessboard.board[row][col] == '~'
                enemy = chessboard.board[row][col].color != self.color
                if empty or enemy:
                    possibleMoves.append(chessboard.positions[row][col])

        return possibleMoves
    
    def canMove(self, chessboard: Chessboard) -> bool:
        return len(self.getPossibleMoves(chessboard)) != 0

    def canMoveTo(self, move: str, chessboard: Chessboard):
        possibleMoves = self.getPossibleMoves(chessboard)
        return True if move in possibleMoves else False

class Pawn(Chesspiece):
    def __init__(self, color) -> None:
        super().__init__()
        self.color = color
        self.hasMoved = False
        
        if color == 'white':
            self.strRep = '♟'
        else:
            self.strRep = '♙'

    def canMoveTo(self, move: str, chessboard: Chessboard):
        # move == the position the piece is supposed to move to
        # board == the board all the pieces are on
        possibleMoves = []
        row, col = self.pos

        # deals with the directly up cases being different
        if (self.color == 'white' and not chessboard.isReversed or 
            self.color == 'black' and chessboard.isReversed):
            up = row - 1
            twoUp = row - 2

        elif (self.color == 'black' and not chessboard.isReversed or
              self.color == 'white' and chessboard.isReversed):
            up = row + 1
            twoUp = row + 2
        
        # directly one space forward
        if chessboard.isOnBoard(up, col):
            directUp = chessboard.board[up][col]
            if directUp == '~' and self.color != directUp.color:
                possibleMoves.append(chessboard.positions[up][col])
            
        # upward diagonals
        # error check for diagonals that are off the board
        diags = [col - 1, col + 1]
        diags = [diag for diag in diags if chessboard.isOnBoard(up, diag)]
        
        for diag in diags:
            piece = chessboard.board[up][diag]
            if piece != '~' and self.color != piece.color:
                possibleMoves.append(chessboard.positions[up][diag])

        # two spaces forward
        if not self.hasMoved:
            piece = chessboard.board[twoUp][col]
            if directUp == '~':                     # can't move through pieces
                if piece == '~' and self.color != piece.color:
                    possibleMoves.append(chessboard.positions[twoUp][col])

        return True if move in possibleMoves else False