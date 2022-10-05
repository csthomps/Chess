'''
Storing all information about the current state of chess game.
Determining valid moves at the current state.
Keep a move log
'''


class game_state():
    def __init__(self):
        # board is an 8x8 2d list, each element of list has 2 characters
        # the first character represents color, "b" or "w"
        # second character represents type of piece
        # "--" represents an empty space
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"] ]
        
        self.move_functions = {"p":self.pawn_moves, "R":self.rook_moves, "N":self.knight_moves,
                               "B":self.bishop_moves, "Q":self.queen_moves, "K":self.king_moves}
        self.white_to_move = True
        self.move_log = []
        self.turn_counter = 0
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = () # coordinates for square where en passant is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = castle_rights(True,True,True,True)
        self.castle_rights_log = [castle_rights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        
        
        
        
        
        '''
        takes a move as a parameter and executes it
        Will not work for castling, en passant, pawn promotion
        '''   
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) # log the move so we can undo it later
        self.white_to_move = not self.white_to_move # swap players
        # update king's position
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        
        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
        
        # en passant move
        if move.is_enpassant_move:
            move.piece_captured = self.board[move.start_row][move.end_col]
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn
        
        # update enpassant_possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2: # only on 2 square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.end_col)
        else:
            self.enpassant_possible = ()
        # update enpassant possible log
        self.enpassant_possible_log.append(self.enpassant_possible)
        
        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else: # queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col -2]
                self.board[move.end_row][move.end_col - 2] = "--"
        
        # update castling rights - whenever it's a rook or king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(castle_rights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    '''
    undo the last move
    '''
    def undo_move(self):
        if len(self.move_log) != 0: # make sure there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved # replace pieces
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move # switch turns back
            # update king's position
            if move.piece_moved == "wK":
                self.white_king_location = (move.end_row, move.end_col)
                self.get_valid_moves()
            elif move.piece_moved == "bK":
                self.black_king_location = (move.end_row, move.end_col)
                self.get_valid_moves()
            # undo en passsant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--" # leave landing square empty
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]
            
            
            # undo castling move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"
            # give back castling rights if we took them away
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castling_rights = castle_rights(new_rights.wks,new_rights.bks,new_rights.wqs,new_rights.bqs)
            # bug fix to undo checkmate and stalemate
            self.checkmate = False
            self.stalemate = False
    
    # update castling rights - whenever it's a rook or king move            
    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0: # queen side rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7: #king side rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0: # queen side rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7: # king side rook
                    self.current_castling_rights.bks = False
        
        # if rooks are captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False
        
    '''
    all moves considering checks
    '''
    def get_valid_moves(self):
        moves = []
        moves_reordered = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1: # only 1 check, block check or move king
                moves = self.get_all_possible_moves()
                # to block a check move a piece into one of the squares between enemy piece and king
                check = self.checks[0] # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                # if knight, must capture knight or move king
                if piece_checking[1] == "N":
                    valid_squares = [(check_row,check_col)]
                else:
                    for i in range(1,8):
                        valid_square = ((king_row) + check[2] * i, king_col + check[3] * i) # check 2 and check 3 are check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: # once you get to piece end checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): # go through backwards when removing from a list as iterating
                    if moves[i].piece_moved[1] != "K": # move doesn't move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.king_moves(king_row, king_col, moves)
        else: # not in check so all moves are fine
            moves = self.get_all_possible_moves()
        if len(moves) == 0: # either checkmate or stalemate
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
                
        # TODO mess with order of moves
        return moves
        
    '''
    returns if player is in check, a list of pins, and a list of checks
    '''
    def check_for_pins_and_checks(self):
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0]== ally_color and end_piece[1] != "K":
                        if possible_pin == (): # list allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0],d[1])
                        else:# 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 5 possibilities
                        # straight away from king and piece is a rook
                        # diagonally away from king and piece is a bishop
                        # 1 square away diagonally from king and piece is a pawn
                        # any direction away and piece is a queen
                        # any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or (i == 1 and type == "K"):
                            if possible_pin == (): # no piece blocking, so check
                                in_check = True
                                checks.append((end_row,end_col,d[0],d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else: # enemy piece not applying check
                            break
                else:
                    break # off board
        # check for knight checks
        knight = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knight:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N": # enemy knight attacking king
                    in_check = True
                    checks.append((end_row,end_col, m[0],m[1]))
        return in_check, pins, checks
                                
                                 
                                
    def square_under_attack(self,r,c):
        if self.white_to_move:
            temp_king_location = self.white_king_location
            self.white_king_location = (r,c)
            under_attack = self.check_for_pins_and_checks()[0]
            self.white_king_location = temp_king_location
        else: 
            temp_king_location = self.black_king_location
            self.black_king_location = (r,c)
            under_attack = self.check_for_pins_and_checks()[0]
            self.black_king_location = temp_king_location
        return under_attack

        
                            
        
    '''
    all moves without considering checks
    ''' 
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of columns in given row
                turn = self.board[r][c][0] 
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r,c,moves) # calls the appropriate move function based on piece type
        return moves

    '''
    get all moves for piece at row, col and add moves to the list
    '''
    # pawns  
    def pawn_moves(self,r,c,moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.white_to_move: # white pawn moves
            king_row, king_col = self.white_king_location
            if self.board[r-1][c] == "--": # 1 square pawn advance
                if not piece_pinned or pin_direction == (-1,0):
                    moves.append(move((r,c),(r-1,c),self.board))
                    if r == 6 and self.board[r-2][c] == "--": # 2 square pawn advance
                        moves.append(move((r,c),(r-2,c),self.board))
            if c-1 >= 0: # capturing left
                if self.board[r-1][c-1][0]=="b": # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1,-1):
                        moves.insert(0,move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside is between king and pawn, outside is between pawn and border
                            inside_range = range(king_col + 1, c-1) # c-1 so doesn't include enemy pawn captured by enpassant
                            outside_Range = range(c+1, self.board.length)
                        else: # king is right of the pawn
                            inside_range = range(king_col - 1, c, -1)
                            outside_Range = range(c-2, -1, -1)
                        for i in inside_range: 
                            if self.board[r][i] != "--": # some other piece is blocking
                                blocking_piece = True
                        for i in outside_Range:
                            square = self.board[r][i]
                            if square[0] == "b" and (square[1] == "Q" or square[1] == "R"): # there is an attacking piece
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.insert(0,move((r,c),(r-1,c-1),self.board, enpassant_move = True))
            if c+1 <= 7: # capturing right
                if self.board[r-1][c+1][0] == "b": # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1,1):
                        moves.insert(0,move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside is between king and pawn, outside is between pawn and border
                            inside_range = range(king_col + 1, c) # c-1 so doesn't include enemy pawn captured by enpassant
                            outside_Range = range(c+2, len(self.board))
                        else: # king is right of the pawn
                            inside_range = range(king_col - 1, c + 1, -1)
                            outside_Range = range(c - 1, -1, -1)
                        for i in inside_range: 
                            if self.board[r][i] != "--": # some other piece is blocking
                                blocking_piece = True
                        for i in outside_Range:
                            square = self.board[r][i]
                            if square[0] == "b" and (square[1] == "Q" or square[1] == "R"): # there is an attacking piece
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.insert(0,move((r,c),(r-1,c+1),self.board, enpassant_move = True))    
                

        else: # black pawn moves
            king_row, king_col = self.black_king_location
            if self.board[r+1][c] == "--": # 1 square pawn advance
                if not piece_pinned or pin_direction == (-1,0):
                    moves.append(move((r,c),(r+1,c),self.board))
                    if r == 1 and self.board[r+2][c] == "--": # 2 square pawn advance
                        moves.append(move((r,c),(r+2,c),self.board))
            if c-1 >= 0: # capturing left
                if self.board[r+1][c-1][0]=="w": # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1,0):
                        moves.insert(0,move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside is between king and pawn, outside is between pawn and border
                            inside_range = range(king_col + 1, c-1) # c-1 so doesn't include enemy pawn captured by enpassant
                            outside_Range = range(c+1, self.board.length)
                        else: # king is right of the pawn
                            inside_range = range(king_col - 1, c, -1)
                            outside_Range = range(c-2, -1, -1)
                        for i in inside_range: 
                            if self.board[r][i] != "--": # some other piece is blocking
                                blocking_piece = True
                        for i in outside_Range:
                            square = self.board[r][i]
                            if square[0] == "w" and (square[1] == "Q" or square[1] == "R"): # there is an attacking piece
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.insert(0,move((r,c),(r+1,c-1),self.board, enpassant_move = True))
            if c+1 <= 7: # capturing right
                if self.board[r+1][c+1][0] == "w": # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1,0):
                        moves.insert(0,move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside is between king and pawn, outside is between pawn and border
                            inside_range = range(king_col + 1, c) # c-1 so doesn't include enemy pawn captured by enpassant
                            outside_Range = range(c+2, self.board.length)
                        else: # king is right of the pawn
                            inside_range = range(king_col - 1, c + 1, -1)
                            outside_Range = range(c - 1, -1, -1)
                        for i in inside_range: 
                            if self.board[r][i] != "--": # some other piece is blocking
                                blocking_piece = True
                        for i in outside_Range:
                            square = self.board[r][i]
                            if square[0] == "w" and (square[1] == "Q" or square[1] == "R"): # there is an attacking piece
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.insert(0,move((r,c),(r+1,c+1),self.board, enpassant_move = True))

    # rooks
    def rook_moves(self,r,c,moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0), (0,-1), (1,0), (0,1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r+d[0] * i
                end_col = c+d[1] * i
                if 0 <= end_row <8 and 0 <= end_col <8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space valid
                            moves.append(move((r,c),(end_row,end_col),self.board))
                        elif end_piece[0] == enemy_color: # enemy piece valid
                            moves.insert(0,move((r,c),(end_row,end_col),self.board))
                            break
                        else: # friendly piece invalid
                            break
                else: # off the board
                    break
                     

    # knight  
    def knight_moves(self,r,c,moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        ally_color = "w" if self.white_to_move else "b"
        for k in knight:
            end_row = r + k[0]
            end_col = c + k[1]
            if 0 <= end_row <8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # empty square
                        moves.append(move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0] != ally_color:
                         moves.insert(0,move((r,c),(end_row,end_col),self.board))
                    else:
                        break
                
    
    # bishop
    def bishop_moves(self,r,c,moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,-1), (1,-1), (-1,1), (1,1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r+d[0] * i
                end_col = c+d[1] * i
                if 0 <= end_row <8 and 0 <= end_col <8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0],-d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space valid
                            moves.append(move((r,c),(end_row,end_col),self.board))
                        elif end_piece[0] == enemy_color: # enemy piece valid
                            moves.insert(0,move((r,c),(end_row,end_col),self.board))
                            break
                        else: # friendly piece invalid
                            break
                else: # off the board
                    break

    # queen
    def queen_moves(self,r,c,moves):
        self.bishop_moves(r,c,moves)
        self.rook_moves(r,c,moves)
    
    # king
    def king_moves(self,r,c,moves):
        king = ((1,1),(-1,1),(-1,-1),(1,-1),(0,1),(1,0),(0,-1),(-1,0))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king[i][0]
            end_col = c + king[i][1]
            if 0 <= end_row <8 and 0 <= end_col <8: # on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # not an ally piece
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row,end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(move((r,c), (end_row, end_col), self.board))
                    # place king back on original locatio
                    if ally_color == "w":
                        self.white_king_location = (r,c)
                    else: 
                        self.black_king_location = (r,c)
        self.castle_moves(r,c,moves, ally_color)
    
    # generate all valid castle moves for the king at (r,c) and add them to the list of moves
    def castle_moves(self,r,c,moves,ally_color):
        if self.in_check:
            return # can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.ks_castle_moves(r,c,moves,ally_color)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.qs_castle_moves(r,c,moves,ally_color)
        
        
    def ks_castle_moves(self,r,c,moves,ally_color):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r,c+2):
                moves.insert(0,move((r,c),(r,c+2),self.board, castle_move = True))
            
    
    
    def qs_castle_moves(self,r,c,moves,ally_color):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r,c-2):
                moves.insert(0,move((r,c),(r,c-2),self.board, castle_move = True))
    
    
                               
class castle_rights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
            




class move():
    # maps keys to values
    # key : value
    ranks_to_rows = {"1":7,"2":6,"3":5,"4":4,
                     "5":3,"6":2,"7":1,"8":0}
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a":0,"b":1,"c":2,"d":3,
                     "e":4,"f":5,"g":6,"h":7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}
    
    def __init__(self, start_sq, end_sq, board, enpassant_move = False, castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.moveID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7)
        # en passant
        self.is_enpassant_move = enpassant_move
        self.is_castle_move = castle_move
        self.is_capture = self.piece_captured != "--"
    '''
    overriding the equals method
    '''
    def __eq__(self,other):
        if isinstance(other, move):
            return self.moveID == other.moveID
        return False
            
    
    def get_chess_notation(self):
        # add to make this like real chess notation
        return self.get_rank_file(self.start_row,self.start_col) + self.get_rank_file(self.end_row,self.end_col)
    
    def get_rank_file(self,r,c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    # overriding the str() function
    def __str__(self):
        # castle move
        if self.is_castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O" 

        end_square = self.get_rank_file(self. end_row, self.end_col)
        
        # pawn moves
        if self.piece_moved[1] == "p":
            if self.is_capture:
             return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square
            
            # pawn promotions
        # two of same type of piece moving to a square, eg. Nbd2 if both knights can move to d2
        # adding + for check move and # for checkmate move
        
        # piece moves
        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square