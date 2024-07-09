from enum import Enum
from queue import PriorityQueue, Queue


class Orientation(Enum):
    left = 0
    up = 1
    right = 2
    down = 3


class BoxState:
    def __init__(
        self, playerPoint: tuple[int, int], boxPoint: tuple[int, int], moveList: list = [], bookMap: list = []
    ) -> None:
        self.boxPoint = boxPoint
        self.playerPoint = playerPoint
        self.moveList = moveList
        self.bookMap = bookMap.copy()

    def __lt__(self, other):
        return len(self.moveList) > len(other.moveList)

    def Step(self) -> int:
        return len(self.moveList)


class PlayerState:
    def __init__(self, playerPoint: tuple[int, int], moveList: list = [], bookMap: list = []) -> None:
        self.playerPoint = playerPoint
        self.moveList = moveList.copy()
        self.bookMap = bookMap.copy()

    def __lt__(self, other):
        return len(self.moveList) < len(other.moveList)


startPoint = (0, 0)
endPoint = (0, 0)
boxPoint = (0, 0)

matrixSize = 0
sokobanMap = []
bookMap = []
visMap = []

moveQueue = []


def Init(size: int = 5):
    global matrixSize, sokobanMap, bookMap, visMap
    matrixSize = size
    sokobanMap = [[0] * matrixSize for _ in range(matrixSize)]
    bookMap = [[0] * matrixSize for _ in range(matrixSize)]
    visMap = [[0] * matrixSize for _ in range(matrixSize)]


def SetStart(x: int, y: int):
    global startPoint
    startPoint = (x, y)


def SetEnd(x: int, y: int):
    global endPoint
    endPoint = (x, y)


def SetBox(x: int, y: int):
    global boxPoint
    boxPoint = (x, y)


def SetBarrier(x: int, y: int):
    sokobanMap[x][y] = 1


def PlayerSolve(targetPoint: tuple[int, int], startPoint: tuple[int, int]) -> list:
    global bookMap
    q = Queue()
    q.put(PlayerState(startPoint, [], [[0] * matrixSize for _ in range(matrixSize)]))
    n = [
        [1, 0, Orientation.right],
        [0, 1, Orientation.down],
        [-1, 0, Orientation.left],
        [0, -1, Orientation.up],
    ]
    while not q.empty():
        temp = q.get()
        if temp.playerPoint == targetPoint:
            # print(temp.moveList)
            # print(targetPoint)
            continue
        bookMap = temp.bookMap
        bookMap[temp.playerPoint[0]][temp.playerPoint[1]] = 1
        for o in n:
            tx = temp.playerPoint[0] + o[0]
            ty = temp.playerPoint[1] + o[1]
            if tx < 0 or tx >= matrixSize or ty < 0 or ty >= matrixSize:
                continue
            if sokobanMap[tx][ty] == 1 or bookMap[tx][ty] == 1:
                continue
            temp.moveList.append(o[2])
            bookMap[tx][ty] = 1
            ShowTable(bookMap)
            q.put(PlayerState((tx, ty), temp.moveList, bookMap))
            temp.moveList.pop()
            bookMap[tx][ty] = 0
    return []


def ShowTable(mat):
    for i in range(matrixSize):
        c = ""
        for j in range(matrixSize):
            c += str(mat[j][i]) + " "
        print(c)
    print("\n")


def SokobanSolve() -> list:
    global visMap, bookMap
    q = PriorityQueue()
    q.put(BoxState(startPoint, boxPoint, [], [[0] * matrixSize for _ in range(matrixSize)]))
    n = [
        [1, 0, Orientation.right],
        [0, 1, Orientation.down],
        [-1, 0, Orientation.left],
        [0, -1, Orientation.up],
    ]
    while not q.empty():
        temp = q.get()
        PrintSokobanMap(temp.playerPoint, temp.boxPoint)
        if temp.boxPoint == endPoint:
            continue
        for o in n:
            tx = temp.boxPoint[0] + o[0]
            ty = temp.boxPoint[1] + o[1]
            tmx = temp.boxPoint[0] - o[0]
            tmy = temp.boxPoint[1] - o[1]
            if tx < 0 or tx >= matrixSize or ty < 0 or ty >= matrixSize:
                continue
            if sokobanMap[tx][ty] == 1 or visMap[tx][ty] > 2:
                continue
            if tmx < 0 or tmx >= matrixSize or tmy < 0 or tmy >= matrixSize:
                continue
            if sokobanMap[tmx][tmy] == 1:
                continue
            # bookMap = [[0] * matrixSize for _ in range(matrixSize)]
            bookMap = temp.bookMap
            bookMap[temp.boxPoint[0]][temp.boxPoint[1]] = 1

            subMove = PlayerSolve((tmx, tmy), temp.playerPoint)

            if subMove == []:
                continue
            bookMap[temp.boxPoint[0]][temp.boxPoint[1]] = 0
            q.put(BoxState((tx, ty), (tmx, tmy), temp.moveList + subMove, bookMap))
            visMap[tx][ty] += 1
    t = q.get()
    while not q.empty():
        print("==========")
        print(t.moveList)
        print(t.Step())
        print(t.boxPoint)
        print()
        t = q.get()


def PrintSokobanMap(playerPoint: tuple[int, int], boxPoint: tuple[int, int]) -> None:
    print()
    c = "  "
    for i in range(matrixSize):
        c += str(i) + " "
    print(c)

    printMap = [["* "] * matrixSize for _ in range(matrixSize)]
    for i in range(matrixSize):
        for j in range(matrixSize):
            if sokobanMap[i][j] == 1:
                printMap[i][j] = "■ "
    printMap[endPoint[0]][endPoint[1]] = "x "
    printMap[playerPoint[0]][playerPoint[1]] = "@ "
    printMap[boxPoint[0]][boxPoint[1]] = "# "
    for i in range(matrixSize):
        c = str(i) + " "
        for j in range(matrixSize):
            c += printMap[j][i]
        print(c)
    print()


if __name__ == "__main__":
    Init()
    SetStart(3, 1)
    SetBox(2, 3)
    SetEnd(1, 0)

    SetBarrier(0, 1)
    SetBarrier(0, 3)
    SetBarrier(2, 1)
    SetBarrier(2, 2)

    # print(SokobanSolve())
    SokobanSolve()
