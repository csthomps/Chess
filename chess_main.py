'''
Handling user input and displaying current game state
'''
import pygame as p
import chess_engine,chess_ai

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512 # 400 is another option
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 # dimenstions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15 # for animations later on
IMAGES = {}

'''
load in images
Initialize a global dictionary of images
only called once in the main
'''
def load_images():
    pieces = ["wp", "wR", "wN", "wB","wQ","wK", "bp", "bR","bN","bB","bQ","bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("fun_projects\Chess\Pictures/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # note: we can acces an image by saying 'IMAGES['wp']'
    
'''
The main driver for our code.  This handles user input and updating graphics
'''
def main():
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.game_state()
    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable for when a move is made
    animate = False # flag variable for when to animate
    load_images() # only do this once, before the loop
    running = True
    sq_selected = () # no square selected initially, keep track of the last click of user (tuple:(row,col))
    player_clicks = [] # keep track of player clicks (two tuples[(r1,c1),(r2,c2)])
    game_over = False
    player_one = True # if a human is playing white, this will be true, if an AI is playing white, then false
    player_two = False # if a human is playing black, this is true, if AI is black, then false
    move_log_font = p.font.SysFont("Arial", 15, False, False) # move log font information
    AI_move = None
    while running:
        is_human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    location = p.mouse.get_pos() # x,y location of mouse
                    col = location[0]//SQ_SIZE 
                    row = location[1]//SQ_SIZE
                    
                    if sq_selected == (row,col) or col >= 8 : # if user clicked same square twice or user clicked move log
                        sq_selected = () #deselect
                        player_clicks = [] # clear player clicks
                    else:
                        sq_selected = (row,col)
                        player_clicks.append(sq_selected) # append for both 1st and 2nd clicks
                    if len(player_clicks)==2: #after 2nd click
                        move = chess_engine.move(player_clicks[0],player_clicks[1],gs.board)
                        for i in range(len(valid_moves)):  
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                #print(move.get_chess_notation()) ####
                                sq_selected = () # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE: #undo when 'backspace' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r: # reset the board when "r" is pressed
                    gs = chess_engine.game_state()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    
        # AI move finder logic  
        if not game_over and not is_human_turn:
            
            #AI_move = chess_ai.find_random_move(valid_moves)
            #AI_move = chess_ai.greedy_move(gs, valid_moves)
            #AI_move = chess_ai.find_best_move_minmax(gs,valid_moves)
            #AI_move = chess_ai.find_best_move_negamax(gs,valid_moves)
            AI_move = chess_ai.find_best_move_negamax_aplhabeta(gs,valid_moves)
            if AI_move == None:
                AI_move = chess_ai.find_random_move(valid_moves) # random moves
            gs.make_move(AI_move)
            move_made = True
            animate = True
            
        
        
        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
                animate = False
                gs.turn_counter += 1
            valid_moves = gs.get_valid_moves()
            
        move_made = False            
        draw_game_state(screen,gs, valid_moves, sq_selected, move_log_font)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_endgame_text(screen, "Black wins by checkmate")
            else: 
                draw_endgame_text(screen, "White wins by checkmate")
        elif gs.stalemate:
            game_over = True
            draw_endgame_text(screen, "Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics for current game state
'''
def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font):
    draw_board(screen) # draw squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) # draw pieces on top of those squares
    draw_move_log(screen, gs, move_log_font)

'''
draw squares on board (top left square is always light)
'''
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight square selected and valid moves for piece selected
'''
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"): # sq_selected is a piece that can be moved
            # highlight selecteed square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) # transparency value -> 0 = transparent, 255 = opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE,r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))
      
      
'''
draw pieces on the board using current gamestate
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
'''
Draws move log
'''      
def draw_move_log(screen, gs, move_log_font):
    
    move_log_rect = p.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("Black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    move_string = None
    for i in range(0, len(move_log), 2):
        move_string =  str(i//2 + 1) + ". " + str(move_log[i]) + "  "
        if i+1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i+1]) + "    "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = move_log_font.render(text,True,p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height()
'''
animating a move
'''
def animate_move(move,screen,board,clock):
    global colors
    coords = [] # list of coordinates animation will move through
    dr = move.end_row - move.start_row # delta row
    dc = move.end_col - move.start_col # delta col
    frames_per_square = 3 # frames to move one square
    frame_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frame_count + 1):
        r,c = ((move.start_row + dr * frame / frame_count, move.start_col + dc * frame/frame_count))
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from it's ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != "--":
            if move.is_enpassant_move:
                enpassant_row = (move.end_row + 1) if move.piece_captured[0] =="b" else (move.end_row - 1)
                end_square = p.Rect(move.end_col*SQ_SIZE, enpassant_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

'''
drawing text at the end of the game
'''
def draw_endgame_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text,0,p.Color("Black"))
    text_location = p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_object.get_width()/2, BOARD_HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text,0,p.Color("Blue"))
    screen.blit(text_object, text_location.move(2,2))
    
    
    
    
    
main()