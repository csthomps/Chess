'''
Chess AI
'''
import random

CHECKMATE = 10000
STALEMATE = -100
DEPTH = 4


piece_scores = {"K":0, "Q":9, "R":5, "B":3, "N":3, "p":1}


knight_scores =[[1,1,1,1,1,1,1,1],
                [1,2,2,2,2,2,2,1],
                [1,2,5,3,3,5,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [1,1,1,1,1,1,1,1]] 

bishop_scores =[[4,3,2,1,1,2,3,4],
                [3,6,3,2,2,2,6,3],
                [2,3,4,3,3,4,3,2],
                [1,2,4,2,2,4,2,1],
                [1,2,4,2,2,4,2,1],
                [2,3,4,3,3,4,3,2],
                [3,6,3,2,2,2,6,3],
                [4,3,2,1,1,2,3,4]] 

queen_scores = [[1,1,1,3,1,1,1,1],
                [1,2,3,3,3,1,1,1],
                [1,4,3,3,3,4,2,1],
                [1,2,3,3,3,2,2,1],
                [1,2,3,3,3,2,2,1],
                [1,4,3,3,3,4,2,1],
                [1,2,3,3,3,1,1,1],
                [1,1,1,3,1,1,1,1]] 

rook_scores =  [[4,3,4,4,4,4,3,4],
                [4,4,4,4,4,4,4,4],
                [1,1,2,3,3,2,1,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,1,2,3,3,2,1,1],
                [4,4,4,4,4,4,4,4],
                [4,3,4,4,4,4,3,4]] 

white_pawn_scores = [[10,10,10,10,10,10,10,10],
                     [8,8,8,8,8,8,8,8],
                     [5,6,6,6,6,6,6,5],
                     [1,2,3,7,7,3,2,1],
                     [1,2,3,8,8,3,2,1],
                     [2,5,2,1,1,2,5,2],
                     [1,1,1,-1,-1,1,1,1],
                     [0,0,0,0,0,0,0,0]]

black_pawn_scores = [[0,0,0,0,0,0,0,0],
                     [1,1,1,-1,-1,1,1,1],
                     [2,5,2,1,1,2,5,2],
                     [1,2,3,8,8,3,2,1],
                     [1,2,3,7,7,3,2,1],
                     [5,6,6,6,6,6,6,5],
                     [8,8,8,8,8,8,8,8],
                     [10,10,10,10,10,10,10,10]]

enemy_king_scores =[[5,5,5,5,5,5,5,5],
                [5,0,0,0,0,0,0,5],
                [5,0,0,0,0,0,0,5],
                [5,0,0,0,0,0,0,5],
                [5,0,0,0,0,0,0,5],
                [5,0,0,0,0,0,0,5],
                [5,0,0,0,0,0,0,5],
                [5,5,5,5,5,5,5,5]] 




piece_position_scores = {"N": knight_scores, "Q":queen_scores, "B":bishop_scores, "R":rook_scores, "bp":black_pawn_scores, "wp":white_pawn_scores, "K":enemy_king_scores}



'''
purely random
'''

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


'''
score board based on material
'''
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_scores[square[1]]
            elif square[0] == "b":
                score -= piece_scores[square[1]]
    return score

'''
better board scoring
a positive score is good for white, negative is good for black
'''
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #score it positionally
                if square[1] == "K" and gs.turn_counter > 70: 
                    if gs.white_to_move and square[0] == "b":
                        piece_position_score = piece_position_scores[square[1]][row][col]
                    elif not gs.white_to_move and square[0] == "w":
                        piece_position_score = piece_position_scores[square[1]][row][col]
                    else:
                        piece_position_score = 0
                elif square[1] == "p":
                    piece_position_score = piece_position_scores[square][row][col] # only for pawns
                else:
                    piece_position_score = piece_position_scores[square[1]][row][col] # all other pieces
            
                if square[0] == "w":
                    score += piece_scores[square[1]] + piece_position_score * .3
                elif square[0] == "b":
                    score -= piece_scores[square[1]] + piece_position_score * .3
                
            
    return score



'''
best move based on material alone
'''
def greedy_move(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponent_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                gs.make_move(opponent_move)
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()
        if opponent_max_score < opponent_minmax_score: 
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move 
        gs.undo_move()
    return best_player_move




'''
minmax recursive algorithm
'''

# helper method to make first recursive call
def find_best_move_minmax(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    minmax_move(gs, valid_moves, DEPTH, gs.white_to_move)
    return next_move

# actual algorithm
def minmax_move(gs,valid_moves, depth, white_to_move): 
    global next_move 
    if depth == 0:
        return score_material(gs.board)
    
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = minmax_move(gs, next_moves, depth - 1, white_to_move= False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = minmax_move(gs, next_moves, depth - 1, white_to_move= True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score        
    
'''
negamax algorithm
'''              

def find_best_move_negamax(gs, valid_moves):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    negamax_move(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    print(counter)
    return next_move

  
def negamax_move(gs, valid_moves, depth, turn_mult):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_mult*score_board(gs)
    
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -negamax_move(gs, next_moves, depth - 1, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score
                    
'''
alpha beta pruning
'''    


# helper method
def find_best_move_negamax_aplhabeta(gs, valid_moves):
    global next_move, counter
    next_move = None
    counter = 0
    negamax_move_alphabeta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    print(counter)
    return next_move

# negamax with alphabeta
def negamax_move_alphabeta(gs, valid_moves, depth,  alpha, beta, turn_mult):
    global next_move, counter
    counter += 1
    if gs.turn_counter > 100:
        depth = DEPTH + 2
    if depth == 0:
        return turn_mult*score_board(gs)
    # move ordering - try to evaluate best moves first - implement later

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -negamax_move_alphabeta(gs, next_moves, depth - 1,-beta,-alpha, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha: # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

                