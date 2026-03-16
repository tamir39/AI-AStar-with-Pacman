## Project Overview

This application finds the most efficient path for Pacman to collect all pellets (.) on a given map. It utilizes a sophisticated heuristic approach combined with state-space search to handle complex environmental obstacles.
### Key Features
A Search Algorithm:* Uses a priority queue to explore states based on $f(n) = g(n) + h(n)$, ensuring an optimal path to the goals.
Dynamic Mechanics: * Teleportation: Pacman can jump between map corners.

Power Pellets (O): Collecting these allows Pacman to move through walls (%) for a limited duration (5 steps).
Advanced Heuristics: Includes a pre-calculated distance matrix and BFS-based path estimation to guide the search efficiently.
Interactive Visualization: A Pygame-based GUI that animates Pacman’s movement, displays current actions (North, South, East, West, Teleport), and calculates the final path cost.
