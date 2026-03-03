import heapq

def astar(start, goal, world, grid_size=20):
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = [
            (current[0]+1, current[1]),
            (current[0]-1, current[1]),
            (current[0], current[1]+1),
            (current[0], current[1]-1)
        ]

        for neighbor in neighbors:
            x = neighbor[0] * grid_size
            y = neighbor[1] * grid_size

            if not world.is_road(x,y):
                continue

            tentative = g_score[current] + 1

            if neighbor not in g_score or tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f = tentative + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f, neighbor))

    return []