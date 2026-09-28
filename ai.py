import random
import pickle

class QLearningAgent:
    def __init__(self, color,
                 alpha=0.1, gamma=0.9,
                 epsilon=1.0, epsilon_min=0.05,
                 epsilon_decay=0.995):
        # constructor
        self.color = color
        self.Q = {}  # Q-table: maps state strings to a dictionary of action: Q-value
        self.alpha = alpha  # Learning rate: how much new info overrides old
        self.gamma = gamma  # Discount factor: future reward importance
        self.epsilon = epsilon  # Exploration rate: chance to explore instead of exploit(randomness)
        self.epsilon_min = epsilon_min  # Minimum exploration rate
        self.epsilon_decay = epsilon_decay  # Rate at which epsilon decays over time

    def get_state(self, board):
        """Convert the board into a unique string representing the current state."""
        return board.encode_state()

    def available_actions(self, board):
        """
        Generate a list of all valid actions (as strings) for the agent’s color.
        Each action is formatted as "sr,sc->dr,dc" representing source to destination.
        If a capture is possible, only capture moves are included.
        """
        must_capture = board.has_capture(self.color)
        acts = []
        for piece in board.get_all_pieces(self.color):
            moves = board.get_valid_moves(piece)
            # If capturing is mandatory, filter to only capture moves
            if must_capture:
                moves = {dst: caps for dst, caps in moves.items() if caps}
            for (dr, dc), caps in moves.items():
                key = f"{piece.row},{piece.col}->{dr},{dc}"
                acts.append(key)
        return acts

    def choose_action(self, board):
        """
        Select an action using epsilon-greedy policy:
        - With probability epsilon, choose a random action (exploration)
        - Otherwise, choose the best-known action from the Q-table (exploitation)
        """
        state = self.get_state(board)
        actions = self.available_actions(board)
        
        # Initialize Q-values for this state if it’s the first time seeing it
        if state not in self.Q:
            self.Q[state] = {a: 0.0 for a in actions}
        # Add any missing actions to Q[state] with default value 0.0
        for a in actions:
            if a not in self.Q[state]:
                self.Q[state][a] = 0.0

        # Decide between exploration or exploitation
        #condition: random number generated bw 0 and 1 < epsilon
        if random.random() < self.epsilon:
            return random.choice(actions)  # Explore: choose random action

        # Exploit: choose action with max Q-value (break ties randomly)
        qvals = self.Q[state]
        maxq = max(qvals[a] for a in actions)
        best = [a for a in actions if qvals[a] == maxq]
        return random.choice(best)

    def learn(self, old_state, action, reward, new_state, done):
        """
        Update the Q-table using the Q-learning update rule.
        This is where the agent learns from experience.
        """
        # Initialize entries in Q-table if they don’t exist
        if old_state not in self.Q:
            self.Q[old_state] = {}
        if action not in self.Q[old_state]:
            self.Q[old_state][action] = 0.0

        old_q = self.Q[old_state][action]  # Current Q-value for the state-action pair
        future_q = 0.0

        # If not terminal state, estimate best possible future Q-value
        if not done and new_state in self.Q and self.Q[new_state]:
            future_q = max(self.Q[new_state].values())

        # Bellman equation to update Q-value
        self.Q[old_state][action] = old_q + self.alpha * (
            reward + self.gamma * future_q - old_q
        )

        # Reduce exploration as learning progresses
        if done and self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filename):
        """Save the Q-table to a file using pickle."""
        with open(filename, 'wb') as f:
            pickle.dump(self.Q, f)

    def load(self, filename):
        """Load a saved Q-table from a file and set epsilon to minimum for exploitation."""
        with open(filename, 'rb') as f:
            self.Q = pickle.load(f)
            self.epsilon = self.epsilon_min  # After loading, mostly exploit known knowledge

    def choose_piece_action(self, board, piece):
        """
        Like choose_action, but restricts to moves starting from a specific piece.
        Used during multi-capture situations to continue jumping with the same piece.
        """
        state = self.get_state(board)
        must_capture = True  # Only call this when captures are mandatory

        # Filter all actions to only those starting from this piece
        all_actions = self.available_actions(board)
        prefix = f"{piece.row},{piece.col}->"
        piece_actions = [a for a in all_actions if a.startswith(prefix)]

        if not piece_actions:
            return None  # No valid actions from this piece

        # Initialize Q entries for piece-specific actions
        if state not in self.Q:
            self.Q[state] = {}
        for a in piece_actions:
            self.Q[state].setdefault(a, 0.0)

        # Use epsilon-greedy over these actions
        if random.random() < self.epsilon:
            return random.choice(piece_actions)  # Explore
        # Exploit: choose the highest Q-value action for this piece
        qvals = self.Q[state]
        best_q = max(qvals[a] for a in piece_actions)
        best = [a for a in piece_actions if qvals[a] == best_q]
        return random.choice(best)
