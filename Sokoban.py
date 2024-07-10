from enum import Enum
from queue import PriorityQueue, Queue

matrixSize = 0


class Operation(Enum):
    moveLeft = 0
    moveUp = 1
    moveRight = 2
    moveDown = 3
    pushLeft = 4
    pushUp = 5
    pushRight = 6
    pushDown = 7

    def IsMove(opt) -> bool:
        return opt in [Operation.moveLeft, Operation.moveDown, Operation.moveRight, Operation.moveUp]

    def IsPush(opt) -> bool:
        return opt in [Operation.pushLeft, Operation.pushDown, Operation.pushRight, Operation.pushUp]


class BoxState:
    def __init__(
        self,
        boxPoint: tuple[int, int],
        playerPoint: tuple[int, int],
        moveList: list = [],
        bookMap: list = [],
        visMap: list = [],
    ) -> None:
        self.boxPoint = boxPoint
        self.playerPoint = playerPoint
        self.moveList = moveList.copy()
        ta = [[0] * matrixSize for _ in range(matrixSize)]
        if bookMap != []:
            for i in range(matrixSize):
                for j in range(matrixSize):
                    ta[i][j] = bookMap[i][j]
        self.bookMap = ta
        tb = [[0] * matrixSize for _ in range(matrixSize)]
        if visMap != []:
            for i in range(matrixSize):
                for j in range(matrixSize):
                    tb[i][j] = visMap[i][j]
        self.visMap = tb

    def __lt__(self, other):
        return len(self.moveList) < len(other.moveList)

    def Step(self) -> int:
        return len(self.moveList)


class PlayerState:
    def __init__(self, playerPoint: tuple[int, int], moveList: list = [], bookMap: list = []) -> None:
        self.playerPoint = playerPoint
        self.moveList = moveList.copy()
        temp = [[0] * matrixSize for _ in range(matrixSize)]
        if bookMap != []:
            for i in range(matrixSize):
                for j in range(matrixSize):
                    temp[i][j] = bookMap[i][j]
        self.bookMap = temp

    def __lt__(self, other):
        return len(self.moveList) < len(other.moveList)


startPoint = (0, 0)
endPoint = (0, 0)
boxPoint = (0, 0)

sokobanMap = []

moveQueue = []


def Init(size: int = 5):
    global matrixSize, sokobanMap
    matrixSize = size
    sokobanMap = [[0] * matrixSize for _ in range(matrixSize)]


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


def PlayerSolve(
    targetPoint: tuple[int, int],
    startPoint: tuple[int, int],
    bookMap: list,
) -> list:
    global sokobanMap
    q = Queue()
    ans = PriorityQueue()
    q.put(PlayerState(startPoint, [], bookMap))
    n = [
        [1, 0, Operation.moveRight],
        [0, 1, Operation.moveDown],
        [-1, 0, Operation.moveLeft],
        [0, -1, Operation.moveUp],
    ]
    while not q.empty():
        temp = q.get()
        temp.bookMap[temp.playerPoint[0]][temp.playerPoint[1]] = 1
        if temp.playerPoint == targetPoint:
            ans.put(temp)
            continue
        for o in n:
            tx = temp.playerPoint[0] + o[0]
            ty = temp.playerPoint[1] + o[1]
            if tx < 0 or tx >= matrixSize or ty < 0 or ty >= matrixSize:
                continue
            if sokobanMap[tx][ty] == 1 or temp.bookMap[tx][ty] == 1:
                continue
            temp.moveList.append(o[2])
            temp.bookMap[tx][ty] = 1
            q.put(PlayerState((tx, ty), temp.moveList, temp.bookMap))
            temp.moveList.pop()
            temp.bookMap[tx][ty] = 0
    if ans.empty():
        return []
    t = ans.get()
    return t.moveList


def ShowTable(mat, x=-1, y=-1):
    for i in range(matrixSize):
        c = ""
        for j in range(matrixSize):
            if x == j and y == i:
                c += "* "
            else:
                c += str(mat[j][i]) + " "
        print(c)
    print()


def SokobanSolve() -> list:
    PrintSokobanMap(startPoint, boxPoint)
    q = Queue()
    ans = PriorityQueue()
    q.put(BoxState(boxPoint, startPoint))
    n = [
        [1, 0, Operation.pushRight, Operation.moveLeft],
        [0, 1, Operation.pushDown, Operation.moveUp],
        [-1, 0, Operation.pushLeft, Operation.moveRight],
        [0, -1, Operation.pushUp, Operation.moveDown],
    ]
    while not q.empty():
        temp = q.get()
        temp.visMap[temp.boxPoint[0]][temp.boxPoint[1]] = 1
        if temp.boxPoint == endPoint:
            ans.put(temp)
            continue
        for o in n:
            tx = temp.boxPoint[0] + o[0]
            ty = temp.boxPoint[1] + o[1]
            tmx = temp.boxPoint[0] - o[0]
            tmy = temp.boxPoint[1] - o[1]
            if tx < 0 or tx >= matrixSize or ty < 0 or ty >= matrixSize:
                continue
            if sokobanMap[tx][ty] == 1 or temp.visMap[tx][ty] >= 1:
                continue
            if tmx < 0 or tmx >= matrixSize or tmy < 0 or tmy >= matrixSize:
                continue
            if sokobanMap[tmx][tmy] == 1:
                continue
            temp.bookMap[temp.boxPoint[0]][temp.boxPoint[1]] = 1
            temp.bookMap[temp.playerPoint[0]][temp.playerPoint[1]] = 1
            subMove = PlayerSolve((tmx, tmy), temp.playerPoint, temp.bookMap)
            if subMove == []:
                continue

            temp.bookMap[temp.playerPoint[0]][temp.playerPoint[1]] = 0
            temp.bookMap[temp.boxPoint[0]][temp.boxPoint[1]] = 0
            temp.visMap[tx][ty] = 1
            subMove.append(o[2])
            subMove.append(o[3])
            q.put(BoxState((tx, ty), (tmx, tmy), temp.moveList + subMove, temp.bookMap, temp.visMap))

            temp.visMap[tx][ty] = 0
    if ans.empty():
        return []
    unoptList = ans.get().moveList
    optList = OptimizePath(unoptList)
    return optList


def OptimizePath(unoptList: list) -> list:
    tempList = []
    buff = []
    dic = {
        Operation.pushLeft: Operation.moveLeft,
        Operation.pushUp: Operation.moveUp,
        Operation.pushRight: Operation.moveRight,
        Operation.pushDown: Operation.moveDown,
    }

    optList = []
    for i in unoptList:
        if Operation.IsMove(i):
            buff.append(i)
        elif Operation.IsPush(i):
            tempList.append(buff.copy())
            buff.clear()
            buff.append(i)
    tempList.append(buff.copy())
    for i in tempList:
        if Operation.IsPush(i[0]):
            head = i[0]
            optList.append(head)
            if dic[head] in i:
                flag = True
                for j in range(2, len(i)):
                    if flag and i[j] == dic[head]:
                        flag = False
                        continue
                    optList.append(i[j])
        else:
            for j in i:
                optList.append(j)
    return optList


def PrintSokobanMap(playerPoint: tuple[int, int], boxPoint: tuple[int, int]) -> None:
    print()
    printMap = [["⬜ "] * matrixSize for _ in range(matrixSize)]
    for i in range(matrixSize):
        for j in range(matrixSize):
            if sokobanMap[i][j] == 1:
                printMap[i][j] = "🛑 "
    printMap[endPoint[0]][endPoint[1]] = "⭕ "
    printMap[playerPoint[0]][playerPoint[1]] = "😋 "
    printMap[boxPoint[0]][boxPoint[1]] = "📦 "
    for i in range(matrixSize):
        c = ""
        for j in range(matrixSize):
            c += printMap[j][i]
        print(c)
    print()


if __name__ == "__main__":
    # Init()
    # SetStart(3, 1)
    # SetBox(2, 3)
    # SetEnd(1, 0)

    # SetBarrier(0, 1)
    # SetBarrier(0, 3)
    # SetBarrier(2, 1)
    # SetBarrier(2, 2)

    Init(4)
    SetStart(0, 0)
    SetBox(1, 1)
    SetEnd(2, 2)

    SetBarrier(0, 1)

    print(SokobanSolve())
    # SokobanSolve()
