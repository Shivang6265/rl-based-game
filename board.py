from piece import Piece


class Board:
    def __init__(self, rows=8, cols=8, tile_size=75, canvas=None):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.canvas = canvas

        # 2D list: None or a Piece instance
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self._setup_pieces()

    def _setup_pieces(self):
        """Place the 12 red and 12 black pieces on starting squares."""
        for r in range(self.rows):
            for c in range(self.cols):
                # only place on dark squares
                if (r + c) % 2 == 0:
                    continue

                if r < 3:
                    # top three rows: black
                    self.grid[r][c] = Piece(r, c, "black")
                elif r > 4:
                    # bottom three rows: red
                    self.grid[r][c] = Piece(r, c, "red")

    def get_valid_moves(self, piece):
        """
        For a given Piece, return a dict mapping:
        destination (row, col) -> list of jumped-over coordinates
        Empty list means normal move, non-empty means capture.
        """
        if piece is None:
            return {}

        moves = {}

        # Regular movement directions
        if piece.color == "red":
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        # Kings move both directions
        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = piece.row + dr
            c = piece.col + dc

            if 0 <= r < self.rows and 0 <= c < self.cols:
                # Simple move
                if self.grid[r][c] is None:
                    moves[(r, c)] = []

                # Capture move
                elif self.grid[r][c].color != piece.color:
                    jump_r = r + dr
                    jump_c = c + dc

                    if (
                        0 <= jump_r < self.rows
                        and 0 <= jump_c < self.cols
                        and self.grid[jump_r][jump_c] is None
                    ):
                        moves[(jump_r, jump_c)] = [(r, c)]

        return moves

    def move_piece(self, piece, dest_row, dest_col):
        """
        Move `piece` to (dest_row, dest_col), remove captured pieces,
        promote to king if needed, and return list of captured Piece(s).
        """
        captured = []

        dr = dest_row - piece.row
        dc = dest_col - piece.col

        # If it's a jump, remove jumped piece
        if abs(dr) == 2 and abs(dc) == 2:
            mid_r = piece.row + dr // 2
            mid_c = piece.col + dc // 2

            captured_piece = self.grid[mid_r][mid_c]
            self.grid[mid_r][mid_c] = None

            if captured_piece is not None:
                captured.append(captured_piece)

        # Move the piece
        self.grid[piece.row][piece.col] = None
        piece.row = dest_row
        piece.col = dest_col
        self.grid[dest_row][dest_col] = piece

        # Promote to king
        if (piece.color == "red" and dest_row == 0) or (
            piece.color == "black" and dest_row == self.rows - 1
        ):
            piece.make_king()

        return captured

    def get_all_pieces(self, color):
        """Return a list of all pieces of the given color."""
        pieces = []
        for row in self.grid:
            for piece in row:
                if piece is not None and piece.color == color:
                    pieces.append(piece)
        return pieces

    def has_capture(self, color):
        """Return True if any piece of `color` has at least one capture move."""
        for piece in self.get_all_pieces(color):
            moves = self.get_valid_moves(piece)
            for captured_list in moves.values():
                if captured_list:
                    return True
        return False

    def encode_state(self):
        """
        Return a string encoding of the board:
        '.' empty
        'r' red man
        'R' red king
        'b' black man
        'B' black king
        """
        symbols = []

        for r in range(self.rows):
            for c in range(self.cols):
                p = self.grid[r][c]

                if p is None:
                    symbols.append(".")
                elif p.color == "red":
                    symbols.append("R" if p.king else "r")
                else:
                    symbols.append("B" if p.king else "b")

        return "".join(symbols)

    def check_winner(self):
        """
        Return:
        - 'red' if red wins
        - 'black' if black wins
        - None if game is still going
        """
        red_pieces = self.get_all_pieces("red")
        black_pieces = self.get_all_pieces("black")

        # No pieces left
        if not red_pieces:
            return "black"
        if not black_pieces:
            return "red"

        # No legal moves left
        red_has_moves = any(self.get_valid_moves(piece) for piece in red_pieces)
        black_has_moves = any(self.get_valid_moves(piece) for piece in black_pieces)

        if not red_has_moves:
            return "black"
        if not black_has_moves:
            return "red"

        return None
