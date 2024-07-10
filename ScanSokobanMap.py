from enum import Enum

mapSize = 0

scanedMap = []

startPoint = (0, 0)


class Direction(Enum):
    left = 0
    up = 1
    right = 2
    down = 3


class TempObject(Enum):
    box = 0
    barrier = 1
    null = 2


def Scan() -> bool:
    pass


def SpinTo():
    pass


def Move():
    pass


def Init(size: int = 5):
    global mapSize, scanedMap
    mapSize = size
    scanedMap = [[0] * mapSize for _ in range(mapSize)]


def SetStart(x: int, y: int):
    global startPoint
    startPoint = (x, y)


def StartScan():
    pass


def dfs(grid, x, y, visited):
    # 如果x或y超出网格边界，或者该位置是障碍物，或者已经访问过，那么就返回
    if x < 0 or y < 0 or x >= len(grid) or y >= len(grid[0]):
        return
    if grid[x][y] == TempObject.barrier or visited[x][y]:
        return
    
    # 标记当前位置已访问
    visited[x][y] = True
    # 对当前位置的上下左右四个方向进行深度优先搜索
    dfs(grid, x - 1, y, visited)
    dfs(grid, x + 1, y, visited)
    dfs(grid, x, y - 1, visited)
    dfs(grid, x, y + 1, visited)


def ScanObstacles(grid):
    # 初始化访问标记数组
    visited = [[False] * len(grid[0]) for _ in range(len(grid))]
    # 遍历网格的每一个位置
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            # 如果当前位置是障碍物，那么就进行深度优先搜索
            if grid[i][j] == TempObject.barrier:
                dfs(grid, i, j, visited)
