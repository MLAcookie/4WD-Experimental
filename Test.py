from collections import deque


class Sokoban:
    def __init__(self):
        self.output = ""
        self.N = 0
        self.M = 0
        self.mp = [[""] * 25 for _ in range(25)]
        self.sx = 0
        self.sy = 0
        self.bx = 0
        self.by = 0
        self.dir = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        self.dpathB = ["N", "S", "E", "W"]
        self.dpathP = ["n", "s", "e", "w"]
        self.ans = ""

    def cal(self, input):
        lines = input.split("\n")
        words = lines[0].split(" ")
        self.N = int(words[0])
        self.M = int(words[1])
        for i in range(self.N):
            mapLine = lines[i + 1]
            for j in range(len(mapLine)):
                self.mp[i][j] = mapLine[j]
                if self.mp[i][j] == "S":
                    self.sx = i
                    self.sy = j
                if self.mp[i][j] == "B":
                    self.bx = i
                    self.by = j
        if self.bfs():
            self.output += self.ans
        else:
            self.output += "Impossible"
        return self.output

    def check(self, x, y):
        if x < 0 or x >= self.N or y < 0 or y >= self.M:
            return False
        if self.mp[x][y] == "#":
            return False
        return True

    def bfs(self):
        vis = [[0] * 25 for _ in range(25)]
        vis[self.bx][self.by] = 1
        q = deque()
        q.append(Node(self.sx, self.sy, self.bx, self.by, ""))
        while q:
            now = q.popleft()
            for i in range(4):
                nbx = now.bx + self.dir[i][0]
                nby = now.by + self.dir[i][1]
                tx = now.bx - self.dir[i][0]
                ty = now.by - self.dir[i][1]
                path = ""
                pathBuilder = []
                if self.check(nbx, nby) and self.check(tx, ty) and vis[nbx][nby] == 0:
                    if self.bfs2(now.px, now.py, now.bx, now.by, tx, ty, pathBuilder):
                        if self.mp[nbx][nby] == "T":
                            self.ans = now.path + "".join(pathBuilder) + self.dpathB[i]
                            return True
                        vis[nbx][nby] = 1
                        q.append(
                            Node(now.bx, now.by, nbx, nby, now.path + "".join(pathBuilder) + self.dpathB[i])
                        )
        return False

    def bfs2(self, ppx, ppy, bbx, bby, tx, ty, pathBuilder):
        vis = [[0] * 25 for _ in range(25)]
        vis[ppx][ppy] = 1
        vis[bbx][bby] = 1
        Q = deque()
        Q.append(Person(ppx, ppy, ""))
        while Q:
            now = Q.popleft()
            if now.x == tx and now.y == ty:
                pathBuilder.extend(now.path)
                return True
            for i in range(4):
                npx = now.x + self.dir[i][0]
                npy = now.y + self.dir[i][1]
                if self.check(npx, npy) and vis[npx][npy] == 0:
                    vis[npx][npy] = 1
                    Q.append(Person(npx, npy, now.path + self.dpathP[i]))
        return False


class Person:
    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.path = path


class Node:
    def __init__(self, px, py, bx, by, path):
        self.px = px
        self.py = py
        self.bx = bx
        self.by = by
        self.path = path


if __name__ == "__main__":
    t = Sokoban()
    ss = t.cal(
        """7 11
        ###########
        #T##......#
        #.#.#..####
        #....B....#
        #.######..#
        #.....S...#
        ###########
        """
    )
    print(ss)
