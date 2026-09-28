import tkinter as tk
from board import Board
from ai import QLearningAgent


# Window settings
WIDTH = 600
HEIGHT = 600
TILE_SIZE = WIDTH // 8

# Colors
BG_COLOR = "#1E1E3C"
TEXT_COLOR = "#FFFFFF"
OPTION_COLOR = "#C8C8FF"
LIGHT_SQUARE = "#F5F5F5"
DARK_SQUARE = "#323232"
RED_COLOR = "#C83232"
BLACK_COLOR = "#1E1E1E"
GOLD = "#FFD700"
MOVE_HINT = "#00FF00"
SELECT_HIGHLIGHT = "#00BFFF"


class CheckersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Checkers")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Stats
        self.games_played = 0
        self.red_wins = 0
        self.black_wins = 0
        self.ties = 0
        self.total_moves = 0

        self.difficulty_settings = {
            "Easy": 0.5,
            "Medium": 0.2,
            "Hard": 0.05
        }

        # Game state
        self.mode = None
        self.difficulty = None
        self.red_is_ai = False
        self.black_is_ai = False

        self.board = None
        self.turn = "red"
        self.selected_piece = None
        self.valid_moves = {}
        self.moves_count = 0

        self.ai_red = None
        self.ai_black = None
        self.ai_job = None
        self.game_over = False

        # UI
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        self.show_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_frame()

        title = tk.Label(
            self.main_frame,
            text="AI Checkers",
            font=("Helvetica", 28, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=30)

        mode_label = tk.Label(
            self.main_frame,
            text="Select Game Mode",
            font=("Helvetica", 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        mode_label.pack(pady=10)

        tk.Button(
            self.main_frame,
            text="Human vs AI",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.select_mode("Human_vs_AI")
        ).pack(pady=8)

        tk.Button(
            self.main_frame,
            text="Human vs Human",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.select_mode("Human_vs_Human")
        ).pack(pady=8)

        tk.Button(
            self.main_frame,
            text="AI vs AI",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.select_mode("AI_vs_AI")
        ).pack(pady=8)

        self.difficulty_label = tk.Label(
            self.main_frame,
            text="Select Difficulty",
            font=("Helvetica", 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )

        self.easy_btn = tk.Button(
            self.main_frame,
            text="Easy",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.start_game("Easy")
        )

        self.medium_btn = tk.Button(
            self.main_frame,
            text="Medium",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.start_game("Medium")
        )

        self.hard_btn = tk.Button(
            self.main_frame,
            text="Hard",
            font=("Helvetica", 14),
            width=20,
            command=lambda: self.start_game("Hard")
        )

    def select_mode(self, mode):
        self.mode = mode

        if mode == "Human_vs_Human":
            self.start_game(None)
            return

        self.difficulty_label.pack(pady=(25, 10))
        self.easy_btn.pack(pady=5)
        self.medium_btn.pack(pady=5)
        self.hard_btn.pack(pady=5)

    def start_game(self, difficulty):
        self.difficulty = difficulty

        if self.mode == "Human_vs_Human":
            self.red_is_ai = False
            self.black_is_ai = False
        elif self.mode == "Human_vs_AI":
            self.red_is_ai = False
            self.black_is_ai = True
        elif self.mode == "AI_vs_AI":
            self.red_is_ai = True
            self.black_is_ai = True

        self.clear_frame()

        # Top info bar
        self.info_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.info_frame.pack(fill="x", pady=5)

        self.stats_label = tk.Label(
            self.info_frame,
            text="",
            font=("Helvetica", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.stats_label.pack(side="left", padx=10)

        self.turn_label = tk.Label(
            self.info_frame,
            text="",
            font=("Helvetica", 12, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.turn_label.pack(side="right", padx=10)

        # Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=WIDTH,
            height=HEIGHT,
            bg=LIGHT_SQUARE,
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bottom buttons
        self.controls_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.controls_frame.pack(pady=10)

        tk.Button(
            self.controls_frame,
            text="Restart",
            font=("Helvetica", 12),
            command=self.restart_game,
            width=12
        ).pack(side="left", padx=10)

        tk.Button(
            self.controls_frame,
            text="Back to Menu",
            font=("Helvetica", 12),
            command=self.back_to_menu,
            width=12
        ).pack(side="left", padx=10)

        # Init board
        self.board = Board(tile_size=TILE_SIZE, canvas=self.canvas)
        self.turn = "red"
        self.selected_piece = None
        self.valid_moves = {}
        self.moves_count = 0
        self.game_over = False

        # Init AI
        self.ai_red = QLearningAgent("red") if self.red_is_ai else None
        self.ai_black = QLearningAgent("black") if self.black_is_ai else None

        if self.ai_red:
            try:
                self.ai_red.load("q_red.pkl")
            except Exception:
                pass
            self.ai_red.epsilon = self.difficulty_settings.get(self.difficulty, 0.2)

        if self.ai_black:
            try:
                self.ai_black.load("q_black.pkl")
            except Exception:
                pass
            self.ai_black.epsilon = self.difficulty_settings.get(self.difficulty, 0.2)

        self.update_labels()
        self.draw_board()
        self.schedule_ai_turn()

    def update_labels(self):
        stats_text = (
            f"Games: {self.games_played}  "
            f"Red Wins: {self.red_wins}  "
            f"Black Wins: {self.black_wins}"
        )

        if self.games_played > 0:
            avg_moves = self.total_moves / self.games_played
            stats_text += f"  Avg Moves/Game: {avg_moves:.1f}"

        self.stats_label.config(text=stats_text)

        turn_color = RED_COLOR if self.turn == "red" else "#000000"
        self.turn_label.config(text=f"Turn: {self.turn.capitalize()}", fg=turn_color)

    def draw_board(self):
        self.canvas.delete("all")

        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE

                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Draw valid move hints
        for (r, c) in self.valid_moves:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2
            self.canvas.create_oval(
                cx - 15, cy - 15,
                cx + 15, cy + 15,
                fill=MOVE_HINT,
                outline=""
            )

        # Draw pieces
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                piece = self.board.grid[row][col]
                if piece is None:
                    continue

                cx = col * TILE_SIZE + TILE_SIZE // 2
                cy = row * TILE_SIZE + TILE_SIZE // 2
                radius = TILE_SIZE // 2 - 8

                if piece == self.selected_piece:
                    self.canvas.create_oval(
                        cx - radius - 4, cy - radius - 4,
                        cx + radius + 4, cy + radius + 4,
                        fill=SELECT_HIGHLIGHT,
                        outline=""
                    )

                color = RED_COLOR if piece.color == "red" else BLACK_COLOR
                self.canvas.create_oval(
                    cx - radius, cy - radius,
                    cx + radius, cy + radius,
                    fill=color,
                    outline="#888888",
                    width=1
                )

                if piece.king:
                    kr = radius // 2
                    self.canvas.create_oval(
                        cx - kr, cy - kr,
                        cx + kr, cy + kr,
                        fill=GOLD,
                        outline=""
                    )

    def on_canvas_click(self, event):
        if self.game_over:
            return

        # Ignore clicks on AI turn
        if (self.turn == "red" and self.red_is_ai) or (self.turn == "black" and self.black_is_ai):
            return

        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        must_capture = self.board.has_capture(self.turn)

        if self.selected_piece:
            if (row, col) in self.valid_moves:
                self.execute_human_move(row, col)
                return

        piece = self.board.grid[row][col]
        if piece and piece.color == self.turn:
            all_moves = self.board.get_valid_moves(piece)
            if not all_moves:
                return

            if must_capture:
                cap_moves = {dst: caps for dst, caps in all_moves.items() if caps}
                if not cap_moves:
                    return
                self.valid_moves = cap_moves
            else:
                self.valid_moves = all_moves

            self.selected_piece = piece
            self.draw_board()
        else:
            self.selected_piece = None
            self.valid_moves = {}
            self.draw_board()

    def execute_human_move(self, row, col):
        captured = self.board.move_piece(self.selected_piece, row, col)
        self.moves_count += 1

        next_caps = {
            dst: caps
            for dst, caps in self.board.get_valid_moves(self.selected_piece).items()
            if caps
        }

        if captured and next_caps:
            self.valid_moves = next_caps
            self.draw_board()
            return

        self.selected_piece = None
        self.valid_moves = {}

        winner = self.board.check_winner()
        if winner:
            self.finish_game(winner)
            return

        self.turn = "black" if self.turn == "red" else "red"
        self.update_labels()
        self.draw_board()
        self.schedule_ai_turn()

    def schedule_ai_turn(self):
        if self.game_over:
            return

        if self.ai_job is not None:
            return

        if self.turn == "red" and self.red_is_ai:
            self.ai_job = self.root.after(250, self.play_ai_turn)
        elif self.turn == "black" and self.black_is_ai:
            self.ai_job = self.root.after(250, self.play_ai_turn)

    def play_ai_turn(self):
        self.ai_job = None

        if self.game_over:
            return

        ai_agent = self.ai_red if self.turn == "red" else self.ai_black
        if ai_agent is None:
            return

        try:
            action = ai_agent.choose_action(self.board)
            if not action:
                winner = "black" if self.turn == "red" else "red"
                self.finish_game(winner)
                return

            sr, sc, dr, dc = map(int, action.replace("->", ",").split(","))
            piece = self.board.grid[sr][sc]

            if piece is None:
                winner = "black" if self.turn == "red" else "red"
                self.finish_game(winner)
                return

            captured = self.board.move_piece(piece, dr, dc)
            self.moves_count += 1

            while captured:
                action = ai_agent.choose_piece_action(self.board, piece)
                if not action:
                    break
                sr, sc, dr, dc = map(int, action.replace("->", ",").split(","))
                captured = self.board.move_piece(piece, dr, dc)

            winner = self.board.check_winner()
            if winner:
                self.finish_game(winner)
                return

            self.turn = "black" if self.turn == "red" else "red"
            self.update_labels()
            self.draw_board()
            self.schedule_ai_turn()

        except Exception as e:
            print("AI move error:", e)
            winner = "black" if self.turn == "red" else "red"
            self.finish_game(winner)

    def finish_game(self, winner):
        self.game_over = True

        self.games_played += 1
        self.total_moves += self.moves_count

        if winner == "red":
            self.red_wins += 1
        elif winner == "black":
            self.black_wins += 1
        else:
            self.ties += 1

        self.update_labels()
        self.draw_board()
        self.show_winner_popup(winner)

    def show_winner_popup(self, winner):
        popup = tk.Toplevel(self.root)
        popup.title("Game Over")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(
            popup,
            text=f"{winner.capitalize()} wins!",
            font=("Helvetica", 20, "bold"),
            padx=30,
            pady=20
        ).pack()

        tk.Label(
            popup,
            text="Choose an option below",
            font=("Helvetica", 12),
            pady=5
        ).pack()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Play Again",
            font=("Helvetica", 12),
            width=12,
            command=lambda: [popup.destroy(), self.restart_game()]
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame,
            text="Back to Menu",
            font=("Helvetica", 12),
            width=12,
            command=lambda: [popup.destroy(), self.back_to_menu()]
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame,
            text="Quit",
            font=("Helvetica", 12),
            width=12,
            command=self.root.destroy
        ).pack(side="left", padx=8)

    def restart_game(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.board = Board(tile_size=TILE_SIZE, canvas=self.canvas)
        self.turn = "red"
        self.selected_piece = None
        self.valid_moves = {}
        self.moves_count = 0
        self.game_over = False

        self.update_labels()
        self.draw_board()
        self.schedule_ai_turn()

    def back_to_menu(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.board = None
        self.turn = "red"
        self.selected_piece = None
        self.valid_moves = {}
        self.moves_count = 0
        self.game_over = False
        self.mode = None
        self.difficulty = None
        self.red_is_ai = False
        self.black_is_ai = False
        self.ai_red = None
        self.ai_black = None

        self.show_menu()


if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()
