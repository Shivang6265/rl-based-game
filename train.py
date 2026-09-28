import random
from board import Board
from ai import QLearningAgent

def compute_reward(captured, done, winner, agent_color):
    """Reward shaping: +10 per piece captured, +100 for win, –100 for loss."""
    r = 0
    r += 10 * len(captured)
    if done:
        r += 100 if winner == agent_color else -100
    return r

def self_play(episodes=5000):
    red_agent   = QLearningAgent("red")
    black_agent = QLearningAgent("black")

    for ep in range(1, episodes+1):
        board = Board()
        turn = "red"
        state = board.encode_state()
        done = False

        while not done:
            agent = red_agent if turn == "red" else black_agent
            action = agent.choose_action(board)

            # parse and execute
            sr, sc, dr, dc = map(int, action.replace("->", ",").split(","))
            piece = board.grid[sr][sc]
            captured = board.move_piece(piece, dr, dc)

            total_captures = list(captured)
            while captured:
                next_caps = {
                    dst: caps
                    for dst, caps in board.get_valid_moves(piece).items()
                    if caps
                }
                if not next_caps:
                    break
                dst, caps = random.choice(list(next_caps.items()))
                captured = board.move_piece(piece, *dst)
                total_captures.extend(captured)

            winner = board.check_winner()
            done = winner is not None

            new_state = board.encode_state()
            reward = compute_reward(total_captures, done, winner, agent.color)

            agent.learn(state, action, reward, new_state, done)

            # prepare next step
            state = new_state
            turn = "black" if turn == "red" else "red"

        # every 500 episodes, print progress
        if ep % 500 == 0:
            print(f"Episode {ep}/{episodes} - eps red: {red_agent.epsilon:.3f}, black: {black_agent.epsilon:.3f}")

    red_agent.save("q_red.pkl")
    black_agent.save("q_black.pkl")
    print("Training complete. Q-tables saved.")

if __name__ == "__main__":
    self_play(episodes=5000)
