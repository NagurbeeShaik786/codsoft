import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math
import sys


try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    if sys.platform == 'darwin': 
        import os
        def beep(frequency=440, duration=100):
            os.system(f"afplay -v 0.5 /System/Library/Sounds/Ping.aiff &")
    else:  
        try:
            import pygame
            pygame.mixer.init()
            SOUND_ENABLED = True
        except ImportError:
            SOUND_ENABLED = False

class TicTacToeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Tic Tac Toe")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        self.root.configure(bg='#121212')
        
       

        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.buttons = []
        self.player_name = "Player"
        self.ai_name = "AI"
        self.current_player = 'X'
        self.scores = {'Player': 0, 'AI': 0, 'Draws': 0}
        self.history = []
        self.settings_window = None
        self.game_history_window = None
        self.ai_difficulty = "Hard" 
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        self.animation_in_progress = False
        
       

        self.title_font = ("Arial", 24, "bold")
        self.status_font = ("Arial", 16)
        self.button_font = ("Arial", 14)
        self.cell_font = ("Arial", 48, "bold")
        
        

        self.create_gradient_background()
      

        self.create_widgets()
        self.update_status()
        
        if self.player_symbol == 'O':
            self.root.after(500, self.ai_move)

    def create_gradient_background(self):
     

        self.bg_canvas = tk.Canvas(self.root, width=800, height=650, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
       
        for i in range(650):
            r = int(18 + (i/650)*10)
            g = int(18 + (i/650)*10)
            b = int(25 + (i/650)*20)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_line(0, i, 800, i, fill=color)

    def create_widgets(self):
        
        
        header_frame = tk.Frame(self.root, bg='#1a1a2e', bd=0)
        header_frame.pack(fill='x', padx=20, pady=15)
        
        

        title_label = tk.Label(header_frame, text="ULTIMATE TIC TAC TOE", 
                              font=self.title_font, bg='#1a1a2e', fg='#e94560')
        title_label.pack(pady=10)
        
      


        status_frame = tk.Frame(self.root, bg='#16213e', bd=0, relief='flat')
        status_frame.pack(fill='x', padx=20, pady=(0, 15))
        self.status_label = tk.Label(status_frame, text="", font=self.status_font, 
                                   bg='#16213e', fg='#f9f9f9')
        self.status_label.pack(side='left', padx=20, pady=10)
        self.score_label = tk.Label(status_frame, text="", font=self.status_font, 
                                  bg='#16213e', fg='#f9f9f9')
        self.score_label.pack(side='right', padx=20, pady=10)
        self.update_scores()
        board_frame = tk.Frame(self.root, bg='#0f3460', bd=0)
        board_frame.pack(padx=20, pady=10)
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                cell_frame = tk.Frame(board_frame, bg='#0f3460', highlightbackground="#e94560", 
                                     highlightthickness=1 if (i+j) % 2 == 0 else 2)
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                
                btn = tk.Button(cell_frame, text='', font=self.cell_font, width=3, height=1,
                               bg='#1a1a2e', fg='#f9f9f9', activebackground='#16213e',
                               activeforeground='#f9f9f9', relief='flat',
                               command=lambda i=i, j=j: self.human_move(i, j))
                btn.pack(padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)
        control_frame = tk.Frame(self.root, bg='#121212', bd=0)
        control_frame.pack(fill='x', padx=20, pady=20)
    
        button_style = {
            'font': self.button_font,
            'width': 10,
            'height': 1,
            'bd': 0,
            'relief': 'flat',
            'activebackground': '#2c2c54'
        }
        
        self.restart_button = tk.Button(control_frame, text="Restart", bg='#2ecc71', 
                                      fg='#f9f9f9', command=self.reset_game, **button_style)
        self.restart_button.grid(row=0, column=0, padx=10, pady=5)
        
        self.settings_button = tk.Button(control_frame, text="Settings", bg='#f1c40f', 
                                       fg='#121212', command=self.open_settings, **button_style)
        self.settings_button.grid(row=0, column=1, padx=10, pady=5)
        
        self.history_button = tk.Button(control_frame, text="History", bg='#9b59b6', 
                                      fg='#f9f9f9', command=self.show_history, **button_style)
        self.history_button.grid(row=0, column=2, padx=10, pady=5)
        
        self.quit_button = tk.Button(control_frame, text="Quit", bg='#e74c3c', 
                                   fg='#f9f9f9', command=self.root.quit, **button_style)
        self.quit_button.grid(row=0, column=3, padx=10, pady=5)
        
        # Difficulty selector
        diff_frame = tk.Frame(control_frame, bg='#121212')
        diff_frame.grid(row=0, column=4, padx=10, pady=5)
        
        tk.Label(diff_frame, text="AI Difficulty:", bg='#121212', fg='#f9f9f9', 
                font=("Arial", 10)).pack(side='left', padx=(10, 5))
        
        self.diff_var = tk.StringVar(value=self.ai_difficulty)
        diff_menu = ttk.Combobox(diff_frame, textvariable=self.diff_var, 
                                values=["Easy", "Medium", "Hard"], width=8, state="readonly")
        diff_menu.pack(side='left')
        diff_menu.bind("<<ComboboxSelected>>", self.change_difficulty)

    def update_scores(self):
        score_text = f"{self.player_name}: {self.scores['Player']}   {self.ai_name}: {self.scores['AI']}   Draws: {self.scores['Draws']}"
        self.score_label.config(text=score_text)

    def update_status(self):
        player_text = f"{self.player_name} ({self.player_symbol})" 
        ai_text = f"{self.ai_name} ({self.ai_symbol})"
        
        if self.current_player == self.player_symbol:
            status = f"{player_text}'s Turn"
            self.status_label.config(fg='#2ecc71')  # Green for player
        else:
            status = f"{ai_text}'s Turn"
            self.status_label.config(fg='#e94560')  # Red for AI
            
        self.status_label.config(text=status)

    def reset_game(self):
        if self.animation_in_progress:
            return
        self.board = [['' for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text='', state='normal', bg='#1a1a2e')
        self.current_player = self.player_symbol
        self.update_status()
        self.history = []
        if self.player_symbol == 'O':
            self.root.after(500, self.ai_move)

    def open_settings(self):
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Game Settings")
        self.settings_window.geometry("400x350")
        self.settings_window.configure(bg='#1a1a2e')
        self.settings_window.resizable(False, False)
        self.settings_window.grab_set()
   
        self.center_window(self.settings_window)
        settings_frame = tk.Frame(self.settings_window, bg='#1a1a2e', padx=20, pady=20)
        settings_frame.pack(fill='both', expand=True)

        tk.Label(settings_frame, text="Game Settings", font=("Arial", 18, "bold"), 
                bg='#1a1a2e', fg='#e94560').pack(pady=(0, 20))

        tk.Label(settings_frame, text="Player Name:", bg='#1a1a2e', fg='#f9f9f9', 
                font=("Arial", 12)).pack(anchor='w', pady=5)
        
        name_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        name_frame.pack(fill='x', pady=(0, 15))
        
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12), width=20)
        self.name_entry.insert(0, self.player_name)
        self.name_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
     
        tk.Label(settings_frame, text="Play as:", bg='#1a1a2e', fg='#f9f9f9', 
                font=("Arial", 12)).pack(anchor='w', pady=5)
        
        symbol_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        symbol_frame.pack(fill='x', pady=(0, 15))
        
        self.symbol_var = tk.StringVar(value=self.player_symbol)
        tk.Radiobutton(symbol_frame, text="X (First Player)", variable=self.symbol_var, 
                      value='X', bg='#1a1a2e', fg='#f9f9f9', selectcolor='#16213e',
                      font=("Arial", 11)).pack(side='left', padx=(0, 20))
        tk.Radiobutton(symbol_frame, text="O (Second Player)", variable=self.symbol_var, 
                      value='O', bg='#1a1a2e', fg='#f9f9f9', selectcolor='#16213e',
                      font=("Arial", 11)).pack(side='left')
        
        sound_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        sound_frame.pack(fill='x', pady=(0, 20))
        
        self.sound_var = tk.BooleanVar(value=SOUND_ENABLED)
        tk.Checkbutton(sound_frame, text="Enable Sound", variable=self.sound_var, 
                      bg='#1a1a2e', fg='#f9f9f9', selectcolor='#16213e',
                      font=("Arial", 11)).pack(anchor='w')
  


        apply_btn = tk.Button(settings_frame, text="Apply Settings", font=("Arial", 12, "bold"),
                            bg='#3498db', fg='#f9f9f9', activebackground='#2980b9',
                            activeforeground='#f9f9f9', relief='flat', width=15,
                            command=self.apply_settings)
        apply_btn.pack(pady=15)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')

    def apply_settings(self):
        self.player_name = self.name_entry.get().strip() or "Player"
        self.player_symbol = self.symbol_var.get()
        self.ai_symbol = 'O' if self.player_symbol == 'X' else 'X'
        
        global SOUND_ENABLED
        SOUND_ENABLED = self.sound_var.get()
        
        self.update_scores()
        self.update_status()
        self.settings_window.destroy()
        self.reset_game()

    def change_difficulty(self, event):
        self.ai_difficulty = self.diff_var.get()

    def human_move(self, i, j):
        if self.animation_in_progress:
            return
            
        if self.board[i][j] == '' and self.current_player == self.player_symbol:
            self.play_move(i, j, self.player_symbol)
            if not self.check_game_end(self.player_symbol):
                self.current_player = self.ai_symbol
                self.update_status()
                self.root.after(500, self.ai_move)

    def ai_move(self):
        if self.animation_in_progress:
            return
        if self.ai_difficulty == "Easy":
            move = self.random_move()
        elif self.ai_difficulty == "Medium":
            move = self.medium_move()
        else:  # Hard
            _, move = self.minimax(self.board, True, -float('inf'), float('inf'))
            
        if move:
            self.play_move(*move, self.ai_symbol)
            if not self.check_game_end(self.ai_symbol):
                self.current_player = self.player_symbol
                self.update_status()

    def random_move(self):
        empty_cells = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']
        return random.choice(empty_cells) if empty_cells else None

    def medium_move(self):
        # Medium difficulty: sometimes makes optimal moves, sometimes random
        if random.random() < 0.7:  # 70% chance to make optimal move
            _, move = self.minimax(self.board, True, -float('inf'), float('inf'))
            return move
        return self.random_move()

    def play_move(self, i, j, player):
        self.board[i][j] = player
        self.history.append((player, i, j))
        
        # Animation effect
        self.animate_move(i, j, player)
        self.play_sound(player)

    def animate_move(self, i, j, player):
        self.animation_in_progress = True
        btn = self.buttons[i][j]
        btn.config(state='disabled')
        
        # Animation parameters
        size = 5
        step = 0
        color = '#2ecc71' if player == self.player_symbol else '#e94560'
        
        def grow():
            nonlocal size, step
            if size < 48:
                size += 3
                btn.config(font=("Arial", size))
                btn.after(10, grow)
            else:
                btn.config(text=player, font=self.cell_font, fg=color)
                self.animation_in_progress = False
                
        # Start animation
        btn.config(text=player, fg=color)
        grow()

    def play_sound(self, player):
        if not SOUND_ENABLED:
            return
            
        try:
            if player == self.player_symbol:
                winsound.Beep(440, 150)  # Higher pitch for player
            else:
                winsound.Beep(330, 200)  # Lower pitch for AI
        except:
            # Fallback for non-Windows systems
            try:
                if sys.platform == 'darwin':
                    beep(440 if player == self.player_symbol else 330)
                else:
                    import pygame
                    pygame.mixer.music.load('/usr/share/sounds/freedesktop/stereo/complete.oga')
                    pygame.mixer.music.play()
            except:
                pass

    def check_game_end(self, player):
        if self.check_winner(self.board, player):
            winner_name = self.player_name if player == self.player_symbol else self.ai_name
            self.scores['Player' if player == self.player_symbol else 'AI'] += 1
            self.show_result(f"{winner_name} wins!")
            self.play_win_sound()
            return True
        elif self.is_draw(self.board):
            self.scores['Draws'] += 1
            self.show_result("It's a draw!")
            self.play_draw_sound()
            return True
        return False

    def play_win_sound(self):
        if not SOUND_ENABLED:
            return
            
        try:
            winsound.Beep(523, 300)
            winsound.Beep(659, 300)
            winsound.Beep(783, 500)
        except:
            pass

    def play_draw_sound(self):
        if not SOUND_ENABLED:
            return
            
        try:
            winsound.Beep(392, 300)
            winsound.Beep(330, 300)
            winsound.Beep(294, 500)
        except:
            pass

    def show_result(self, result_text):
        self.update_scores()
        self.disable_board()
        self.highlight_winning_line()
        
        # Create a custom message box
        result_window = tk.Toplevel(self.root)
        result_window.title("Game Over")
        result_window.geometry("300x150")
        result_window.configure(bg='#1a1a2e')
        result_window.resizable(False, False)
        self.center_window(result_window)
        result_window.grab_set()
        
        # Message
        tk.Label(result_window, text=result_text, font=("Arial", 14), 
                bg='#1a1a2e', fg='#f9f9f9').pack(pady=20)
        
        # Buttons
        btn_frame = tk.Frame(result_window, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Play Again", font=("Arial", 10), 
                 bg='#2ecc71', fg='#f9f9f9', width=10,
                 command=lambda: [result_window.destroy(), self.reset_game()]).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="Quit", font=("Arial", 10), 
                 bg='#e74c3c', fg='#f9f9f9', width=10,
                 command=self.root.quit).pack(side='left', padx=10)

    def highlight_winning_line(self):
        # Check for winning lines and highlight them
        board = self.board
        
        # Check rows
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '':
                for j in range(3):
                    self.buttons[i][j].config(bg='#34495e')
                return
                
        # Check columns
        for j in range(3):
            if board[0][j] == board[1][j] == board[2][j] != '':
                for i in range(3):
                    self.buttons[i][j].config(bg='#34495e')
                return
                
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            for i in range(3):
                self.buttons[i][i].config(bg='#34495e')
            return
            
        if board[0][2] == board[1][1] == board[2][0] != '':
            for i in range(3):
                self.buttons[i][2-i].config(bg='#34495e')
            return

    def disable_board(self):
        for row in self.buttons:
            for btn in row:
                btn['state'] = 'disabled'

    def check_winner(self, board, player):
        # Check rows
        for i in range(3):
            if all(board[i][j] == player for j in range(3)):
                return True
                
        # Check columns
        for j in range(3):
            if all(board[i][j] == player for i in range(3)):
                return True
                
        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return True
            
        if all(board[i][2-i] == player for i in range(3)):
            return True
            
        return False

    def is_draw(self, board):
        return all(board[i][j] != '' for i in range(3) for j in range(3))

    def minimax(self, board, is_max, alpha, beta):
        if self.check_winner(board, self.ai_symbol):
            return 1, None
        if self.check_winner(board, self.player_symbol):
            return -1, None
        if self.is_draw(board):
            return 0, None

        best_move = None
        if is_max:
            max_eval = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = self.ai_symbol
                        eval, _ = self.minimax(board, False, alpha, beta)
                        board[i][j] = ''
                        if eval > max_eval:
                            max_eval = eval
                            best_move = (i, j)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = self.player_symbol
                        eval, _ = self.minimax(board, True, alpha, beta)
                        board[i][j] = ''
                        if eval < min_eval:
                            min_eval = eval
                            best_move = (i, j)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval, best_move

    def show_history(self):
        if self.game_history_window and tk.Toplevel.winfo_exists(self.game_history_window):
            self.game_history_window.lift()
            return

        self.game_history_window = tk.Toplevel(self.root)
        self.game_history_window.title("Game History")
        self.game_history_window.geometry("500x400")
        self.game_history_window.configure(bg='#1a1a2e')
        self.game_history_window.resizable(False, False)
        self.center_window(self.game_history_window)
        
        # Title
        tk.Label(self.game_history_window, text="Game History", font=("Arial", 18, "bold"), 
                bg='#1a1a2e', fg='#e94560').pack(pady=10)
        
        # History list
        history_frame = tk.Frame(self.game_history_window, bg='#16213e')
        history_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(history_frame, bg='#16213e', highlightthickness=0)
        scrollbar = tk.Scrollbar(history_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#16213e')
        
        # Fixed the parenthesis issue here
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Display history
        if not self.history:
            tk.Label(scrollable_frame, text="No moves recorded yet", 
                    font=("Arial", 12), bg='#16213e', fg='#f9f9f9').pack(pady=20)
            return
            
        for idx, move in enumerate(self.history, 1):
            player, i, j = move
            player_name = self.player_name if player == self.player_symbol else self.ai_name
            move_text = f"Move {idx}: {player_name} placed {player} at ({i+1}, {j+1})"
            
            move_frame = tk.Frame(scrollable_frame, bg='#16213e', padx=10, pady=5)
            move_frame.pack(fill='x', pady=2)
            
            color = '#2ecc71' if player == self.player_symbol else '#e94560'
            tk.Label(move_frame, text=move_text, font=("Arial", 11), 
                    bg='#16213e', fg=color, anchor='w').pack(side='left')

if __name__ == '__main__':
    root = tk.Tk()
    game = TicTacToeGame(root)
    root.mainloop()