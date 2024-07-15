# 定义了简化版推箱子的求解逻辑
# 大致上的过程是两层BFS，先求解箱子的路径，然后根据箱子的每步移动求出小车的路径
# 最后合并一些额外的路径，得到一条最优路径
from enum import Enum
from queue import PriorityQueue, Queue
import ImOutput

# 定义地图的大小
matrixSize = 0


# 定义操作
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

    def ToMove(opt):
        switchToMove = {
            Operation.pushLeft: Operation.moveLeft,
            Operation.pushUp: Operation.moveUp,
            Operation.pushRight: Operation.moveRight,
            Operation.pushDown: Operation.moveDown,
        }
        return switchToMove[opt]


# 定义箱子求解过程的状态
class BoxState:
    def __init__(
        self,
        boxPoint,
        playerPoint,
        moveList=[],
        bookMap=None,
        visMap=None,
    ) -> None:
        # 会进行一些矩阵复制操作
        self.boxPoint = boxPoint
        self.playerPoint = playerPoint
        self.moveList = moveList.copy()
        ta = [[0] * matrixSize for _ in range(matrixSize)]
        if bookMap is not None:
            for i in range(matrixSize):
                for j in range(matrixSize):
                    ta[i][j] = bookMap[i][j]
        self.bookMap = ta
        tb = [[0] * matrixSize for _ in range(matrixSize)]
        if visMap is not None:
            for i in range(matrixSize):
                for j in range(matrixSize):
                    tb[i][j] = visMap[i][j]
        self.visMap = tb

    def __lt__(self, other):
        return len(self.moveList) < len(other.moveList)

    def Step(self) -> int:
        return len(self.moveList)


# 定义小车单步求解过程的状态
class PlayerState:
    def __init__(self, playerPoint, moveList: list = [], bookMap: list = []) -> None:
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


# 起始点，终点，箱子点
startPoint = (0, 0)
endPoint = (0, 0)
boxPoint = (0, 0)

# 推箱子地图
sokobanMap = []


# 初始化
def Init(size: int = 5):
    global matrixSize, sokobanMap
    matrixSize = size
    sokobanMap = [[0] * matrixSize for _ in range(matrixSize)]


# 设定初始位置
def SetStart(x: int, y: int):
    global startPoint
    startPoint = (x, y)


# 设定终点
def SetEnd(x: int, y: int):
    global endPoint
    endPoint = (x, y)


# 设置箱子位置
def SetBox(x: int, y: int):
    global boxPoint
    boxPoint = (x, y)


# 设置障碍物位置
def SetBarrier(x: int, y: int):
    sokobanMap[x][y] = 1


# 定义小车单步路径求解函数
def PlayerSolve(
    targetPoint,
    startPoint,
    bookMap,
):
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
    # BFS遍历所有路径
    while not q.empty():
        temp = q.get()
        temp.bookMap[temp.playerPoint[0]][temp.playerPoint[1]] = 1
        if temp.playerPoint == targetPoint:
            # 有解的情况下加入ans这个优先队列中
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
    # 通过优先队列筛选出最优路径
    if ans.empty():
        return []
    t = ans.get()
    return t.moveList


# 定义箱子路径求解过程
def SokobanSolve():
    ImOutput.Out.Println("Sokoban: 开始求解")
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
    # BFS求解所有路径
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
            # 加入强制推箱子，先推一下再退回去
            # 保证结果可以完成推箱子游戏
            subMove.append(o[2])
            subMove.append(o[3])
            q.put(BoxState((tx, ty), (tmx, tmy), temp.moveList + subMove, temp.bookMap, temp.visMap))

            temp.visMap[tx][ty] = 0
    # 通过优先队列筛选出最优路径
    if ans.empty():
        return []
    unoptList = ans.get().moveList
    optList = OptimizePath(unoptList)
    return optList


# 优化路径
def OptimizePath(unoptList: list) -> list:
    # 先找push的操作，然后看看之后有没有同方向的move操作
    # 如果有，删除这个move操作和之前加上的回退操作
    ImOutput.Out.Println("Sokoban: 最优化路线")
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


# 终端中打印地图的函数，纯好玩的
def PrintSokobanMap(playerPoint, boxPoint) -> None:
    print()
    printMap = [["⬜ "] * matrixSize for _ in range(matrixSize)]
    for i in range(matrixSize):
        for j in range(matrixSize):
            if sokobanMap[i][j] == 1:
                printMap[i][j] = "⛔ "
    printMap[endPoint[0]][endPoint[1]] = "🏁 "
    printMap[playerPoint[0]][playerPoint[1]] = "♿ "
    printMap[boxPoint[0]][boxPoint[1]] = "📦 "
    for i in range(matrixSize):
        c = ""
        for j in range(matrixSize):
            c += printMap[j][i]
        print(c)
    print()


# 在GUI终端中打印地图的函数，也是纯好玩的
def ImPrintSokobanMap(playerPoint, boxPoint) -> None:
    printMap = [["* "] * matrixSize for _ in range(matrixSize)]
    for i in range(matrixSize):
        for j in range(matrixSize):
            if sokobanMap[i][j] == 1:
                printMap[i][j] = "障 "
    printMap[endPoint[0]][endPoint[1]] = "终 "
    printMap[playerPoint[0]][playerPoint[1]] = "人 "
    printMap[boxPoint[0]][boxPoint[1]] = "箱 "
    for i in range(matrixSize):
        c = ""
        for j in range(matrixSize):
            c += printMap[j][i]
        ImOutput.Out.Println(c)
    ImOutput.Out.Println()


# 从box3结果中加载地图
def LoadFromMatrix(mat):
    size = len(mat)
    Init(size)
    for i in range(size):
        for j in range(size):
            if mat[j][i] == "O":
                SetBarrier(i, j)
            elif mat[j][i] == "B":
                SetBox(i, j)


# 转换为box3可处理的移动操作序列
def Prase(oprationList):
    dic = {
        Operation.moveUp: 0,
        Operation.moveRight: 1,
        Operation.moveDown: 2,
        Operation.moveLeft: 3,
        Operation.pushUp: 4,
        Operation.pushRight: 5,
        Operation.pushDown: 6,
        Operation.pushLeft: 7,
    }
    ans = []
    for i in oprationList:
        ans.append(dic[i])
    return ans


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

    ans = SokobanSolve()
    print(ans)
    # SokobanSolve()
