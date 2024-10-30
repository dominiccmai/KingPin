# KingPin

**KingPin** is a high-performance chess engine designed for efficiency and scalability. Leveraging advanced algorithms for move evaluation and multithreading, KingPin provides a competitive and customizable AI capable of handling complex chess scenarios.

## Key Features
  
- **Alpha-Beta Pruning with Move Ordering**: Implements an optimized Alpha-Beta pruning algorithm that improves search efficiency by focusing on promising moves first, drastically reducing the search space.

- **Quiescence Search**: An additional search layer that addresses the horizon effect, ensuring the engine accurately evaluates positions with pending captures or checks before returning evaluations.

- **Multithreaded Search for Parallel Evaluation**: Leverages multithreading to perform concurrent evaluations of possible moves, maximizing CPU utilization and reducing response time.

- **Piece-Square Tables for Positional Evaluation**: Employs piece-square tables to guide the engine’s positional play, considering the optimal squares for each piece type at different stages of the game.

- **Iterative Deepening**: Uses iterative deepening to build search depth progressively, allowing the engine to return the best found move within a set time frame even if the search is cut short.


### Customizable Difficulty Levels

The AI difficulty can be adjusted by:
- Limiting search depth.
- Adjusting evaluation weights (favoring material over position, for example).
- Reducing the quiescence depth or iterative deepening increment, making the engine play faster but less accurately.

## Project Structure
- **assets/**: Chess piece images and sound effects.
- **src/**: Core engine files, including board representation, AI logic, and utilities.
  - **src/engine/**: Contains engine-specific files, such as move generation, evaluation, and search algorithms.
  - **src/gui/**: GUI interface files, rendering 

## Installation

1. **Clone the repository**:
   `git clone <repository_url>`
   `cd KingPin`

2. **Install dependencies** (once `requirements.txt` is generated):
   `pip install -r requirements.txt`

3. **Running the Engine**:
   `python main.py`

