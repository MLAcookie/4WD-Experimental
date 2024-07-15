# 在VNC环境中，由于此时x11不会指定MESA的OpenGL版本，需要在运行前指定OpenGL版本
# 需要在运行前加上这句
# MESA_GL_VERSION_OVERRIDE=4.3

# 这段代码是给小车的main文件，会启动一个使用dearpygui的GUI界面，可以在里面进行一些操作
from enum import Enum
import dearpygui.dearpygui as dpg
import ImOutput
import Sokoban
import CameraService
import box3


# 定义按钮的状态
class ButtonState(Enum):
    null = 0
    start = 1
    end = 2
    box = 3
    barrier = 4
    unknow = 5
    up = 6
    right = 7
    down = 8
    left = 9
    fine = 10


# 定义GUI中地图的按钮控件
class MapButton:
    stateToLable = {
        ButtonState.null: "",
        ButtonState.start: "起始",
        ButtonState.end: "终点",
        ButtonState.box: "箱子",
        ButtonState.barrier: "障碍",
        ButtonState.unknow: "未知",
        ButtonState.up: "↑",
        ButtonState.right: "→",
        ButtonState.down: "↓",
        ButtonState.left: "←",
        ButtonState.left: "#",
    }

    # 定义按钮的回调事件
    def __ButtonClick_Callback(self, sender, data):
        # 当按钮开启切换状态功能时
        if self.enableSwitch:
            swich = {
                ButtonState.null: ButtonState.start,
                ButtonState.start: ButtonState.end,
                ButtonState.end: ButtonState.box,
                ButtonState.box: ButtonState.barrier,
                ButtonState.barrier: ButtonState.null,
            }

            self.buttonState = swich[self.buttonState]
            dpg.configure_item(self.buttonId, label=MapButton.stateToLable[self.buttonState])
        # 执行按钮的其他回调
        if self.buttonCallback is not None:
            self.buttonCallback(sender, {"state": self.buttonState, "location": self.buttonLocation})

    # 设定按钮的状态
    def SetState(self, state):
        self.buttonState = state
        dpg.configure_item(self.buttonId, label=MapButton.stateToLable[self.buttonState])

    # 设定是否启动按钮
    def SetEnable(self, enable):
        dpg.configure_item(self.buttonId, enabled=enable)

    # 按钮控件的构造函数
    def __init__(self, size: int = 75, location=(0, 0), callback=None, enableSwitch=False, enabled=True):
        # 按钮控件的UUID
        self.buttonId = dpg.generate_uuid()
        # 设定初始状态
        self.buttonState = ButtonState.null
        # 表示按钮代表的地图位置
        self.buttonLocation = location
        # 设定按钮的其他回调
        self.buttonCallback = callback
        # 是否启用状态切换功能
        self.enableSwitch = enableSwitch
        dpg.add_button(
            tag=self.buttonId, height=size, width=size, callback=self.__ButtonClick_Callback, enabled=enabled
        )


# 定义GUI中的地图视图
class MapGrid:
    def __init__(self, mapSize, buttonCallback=None, initShow=True, buttonEnable=True) -> None:
        self.__components = {}
        self.__buttonMatrix = []
        self.__mapSize = mapSize
        self.__buttonEnable = buttonEnable
        self.buttonCallback = buttonCallback
        if initShow:
            self.Show()

    def RegComponent(self, name: str) -> int:
        self.__components[name] = dpg.generate_uuid()
        return self.__components[name]

    def GetComponentValue(self, name: str) -> any:
        return dpg.get_value(self.__components[name])

    def SetComponentValue(self, name: str, value: any) -> None:
        dpg.set_value(self.__components[name], value)

    def ConfigComponent(self, name: str, **kwargs: any) -> None:
        dpg.configure_item(self.__components[name], **kwargs)

    def ClearState(self):
        for i in self.__buttonMatrix:
            for j in i:
                j.SetState(ButtonState.null)

    def SetStateAt(self, point, state):
        self.__buttonMatrix[point[1]][point[0]].SetState(state)

    def SetEnableAt(self, point, enable):
        self.__buttonMatrix[point[1]][point[0]].SetEnable(enable)

    def SetState(self, mat):
        for i in range(self.__mapSize):
            for j in range(self.__mapSize):
                self.__buttonMatrix[i][j].SetState(mat[j][i])

    def GetButton(self, point):
        return self.__buttonMatrix[point[1]][point[0]]

    def Show(self) -> None:
        size = self.__mapSize
        unitSize = 360 / size - 5
        self.__buttonMatrix = []
        with dpg.child_window(tag=self.RegComponent("MapView"), width=370, height=370):
            for i in range(size):
                self.__buttonMatrix.append([])
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    for j in range(size):
                        self.__buttonMatrix[i].append(
                            MapButton(unitSize, (j, i), self.buttonCallback, enabled=self.__buttonEnable)
                        )


# 程序主界面
class CarUI:
    def __init__(self, initShow=True) -> None:
        self.__components = {}
        self.objectMatrix = []
        self.scanMapGrid = None
        self.solveMapGrid = None
        self.outputView = None
        self.exploredMap = []
        self.optPath = []
        self.startPoint = (-1, -1)
        self.endPoint = (-1, -1)
        self.flag = [False, False]
        self.index = 0
        self.point = (-1, -1)
        if initShow:
            self.Show()

    def RegComponent(self, name: str) -> int:
        self.__components[name] = dpg.generate_uuid()
        return self.__components[name]

    def GetComponentValue(self, name: str) -> any:
        return dpg.get_value(self.__components[name])

    def SetComponentValue(self, name: str, value: any) -> None:
        dpg.set_value(self.__components[name], value)

    def ConfigComponent(self, name: str, **kwargs: any) -> None:
        dpg.configure_item(self.__components[name], **kwargs)

    # 定义起始/终止点行为
    def __SetPoint_Callback(self, sender, data):
        startPoint = self.GetComponentValue("Scan_StartPoint_intx")
        endPoint = self.GetComponentValue("Scan_EndPoint_intx")
        if self.flag[0] and self.flag[1]:
            self.scanMapGrid.SetStateAt((startPoint[0], startPoint[1]), ButtonState.null)
            self.scanMapGrid.SetStateAt((endPoint[0], endPoint[1]), ButtonState.null)
            self.flag = [False, False]
            self.SetComponentValue("Scan_StartPoint_intx", [-1, -1, 0, 0])
            self.SetComponentValue("Scan_EndPoint_intx", [-1, -1, 0, 0])
            self.SetComponentValue("Solve_StartPoint_intx", [-1, -1, 0, 0])
            self.SetComponentValue("Solve_EndPoint_intx", [-1, -1, 0, 0])
            ImOutput.Out.Println("已重置起始点/终止点")
            return
        point = data["location"]
        if not self.flag[0]:
            self.scanMapGrid.SetStateAt(point, ButtonState.start)
            self.SetComponentValue("Scan_StartPoint_intx", [point[0], point[1], 0, 0])
            self.startPoint = point
            self.SetComponentValue("Solve_StartPoint_intx", [point[0], point[1], 0, 0])
            ImOutput.Out.Println("设置起始点: " + str((point[0], point[1])))
            self.flag[0] = True
        else:
            tl = self.GetComponentValue("Scan_StartPoint_intx")
            if point == (tl[0], tl[1]):
                return
            self.scanMapGrid.SetStateAt(point, ButtonState.end)
            self.SetComponentValue("Scan_EndPoint_intx", [point[0], point[1], 0, 0])
            self.SetComponentValue("Solve_EndPoint_intx", [point[0], point[1], 0, 0])
            ImOutput.Out.Println("设置终止点: " + str((point[0], point[1])))
            self.flag[1] = True

    # 定义开始扫描行为
    def __StartScan_Callback(self, sender, data):
        startPoint = self.GetComponentValue("Scan_StartPoint_intx")
        endPoint = self.GetComponentValue("Scan_EndPoint_intx")

        if (startPoint[0], startPoint[1]) == (-1, -1) or (endPoint[0], endPoint[1]) == (-1, -1):
            ImOutput.Out.Println("未输入起始点/终止点")
            return
        self.ConfigComponent("Scan_WaitGroup", show=True)
        ImOutput.Out.Println("开始扫描...")
        box3.delayTime = self.GetComponentValue("SpinOffset_float")
        box3.delayTime2 = self.GetComponentValue("ReverseOffset_float")
        switch = {"上": 0, "右": 1, "下": 2, "左": 3}
        box3.dir_code = switch[self.GetComponentValue("OriginDirection_combo")]
        (box3.column, box3.row) = (startPoint[0], startPoint[1])
        self.endPoint = (endPoint[0], endPoint[1])

        tempList = box3.bfs_explore_map()
        self.exploredMap = tempList
        size = len(tempList)
        buttonStateMap = [[ButtonState.null] * size for _ in range(size)]
        switch = {
            "O": ButtonState.barrier,
            "B": ButtonState.box,
            "X": ButtonState.unknow,
            "L": ButtonState.null,
        }
        for i in range(size):
            for j in range(size):
                buttonStateMap[i][j] = switch[tempList[j][i]]
                self.scanMapGrid.SetEnableAt((i, j), False)
        buttonStateMap[startPoint[0]][startPoint[1]] = ButtonState.start
        buttonStateMap[endPoint[0]][endPoint[1]] = ButtonState.end
        Sokoban.SetStart(startPoint[0], startPoint[1])
        Sokoban.SetEnd(endPoint[0], endPoint[1])
        self.scanMapGrid.SetState(buttonStateMap)
        self.solveMapGrid.SetState(buttonStateMap)
        self.ConfigComponent("Scan_WaitGroup", show=False)
        ImOutput.Out.Println("扫描完成")

    # 定义从二维码导入行为
    def __ScanQRCode_Callback(self, sender, data):
        if not CameraService.Service.enableQRCodeModule:
            ImOutput.Out.Println("请启用二维码功能 ( 开始 >> 启用二维码 )")
            return
        qrCodeData = CameraService.QRCodeModule.qrCodeInfo
        # qrCodeData = "4\nStart 0 1\nEnd 2 2\nBox 3 1\n"

        if qrCodeData is None:
            ImOutput.Out.Println("未检测到二维码")
            return

        self.scanMapGrid.ClearState()
        commands = qrCodeData.split("\n")
        size = int(commands[0])
        buttonStateMap = [[ButtonState.null] * size for _ in range(size)]
        Sokoban.Init(size)
        swichMethod = {
            "Start": Sokoban.SetStart,
            "End": Sokoban.SetEnd,
            "Box": Sokoban.SetBox,
            "Barrier": Sokoban.SetBarrier,
        }
        swichState = {
            "Start": ButtonState.start,
            "End": ButtonState.end,
            "Box": ButtonState.box,
            "Barrier": ButtonState.barrier,
        }
        for i in range(1, len(commands)):
            if commands[i] == "":
                continue
            command = commands[i].split(" ")
            h = command[0]
            p0 = int(command[1])
            p1 = int(command[2])
            ImOutput.Out.Println("%s: (%d, %d)" % (h, p0, p1))
            swichMethod[h](p0, p1)
            buttonStateMap[p0][p1] = swichState[h]
            self.scanMapGrid.SetEnableAt((p0, p1), False)
        self.scanMapGrid.SetState(buttonStateMap)
        self.solveMapGrid.SetState(buttonStateMap)

        self.flag = (True, True)

        ImOutput.Out.Println("已从二维码中导入")

    # 定义开始求解行为
    def __StartSolve_Callback(self, sender, data):
        self.ConfigComponent("Solve_WaitGroup", show=True)
        Sokoban.LoadFromMatrix(self.exploredMap)
        self.optPath = Sokoban.SokobanSolve()
        if self.optPath == []:
            ImOutput.Out.Println("otto: 欸, 你怎么似了")
            ImOutput.Out.Println("此情况无解")
            return

        box3.path = Sokoban.Prase(self.optPath)
        box3.MoveAsPath(self.__CarMove_Callback)
        self.solveMapGrid.SetStateAt(self.point, ButtonState.fine)
        self.ConfigComponent("Solve_WaitGroup", show=False)

    # 定义小车移动后同步展示路径的行为
    def __CarMove_Callback(self):
        switchToOffset = {
            Sokoban.Operation.moveLeft: (-1, 0),
            Sokoban.Operation.moveUp: (0, -1),
            Sokoban.Operation.moveRight: (1, 0),
            Sokoban.Operation.moveDown: (0, 1),
        }
        switchToState = {
            Sokoban.Operation.moveLeft: ButtonState.left,
            Sokoban.Operation.moveUp: ButtonState.up,
            Sokoban.Operation.moveRight: ButtonState.right,
            Sokoban.Operation.moveDown: ButtonState.down,
        }
        if self.index == 0:
            self.point = self.startPoint
        current = self.optPath[self.index]
        if Sokoban.Operation.IsPush(current):
            current = Sokoban.Operation.ToMove(current)
        self.solveMapGrid.SetStateAt(self.point, switchToState[current])
        self.point = (self.point[0] + switchToOffset[current][0], self.point[1] + switchToOffset[current][1])
        ImOutput.Out.Println("移动，当前坐标为(%d, %d)" % (self.point[0], self.point[1]))
        self.index += 1

    # 程序的ui定义
    def Show(self):
        with dpg.window(
            tag=self.RegComponent("MainWindow"),
            label="推箱子",
            width=700,
            height=600,
            no_close=True,
            no_collapse=True,
        ):
            with dpg.tab_bar():
                with dpg.tab(label="扫描地图"):
                    with dpg.group(horizontal=True):
                        self.scanMapGrid = MapGrid(4, self.__SetPoint_Callback)
                        with dpg.child_window(width=-1, height=370):
                            dpg.add_text()
                            dpg.add_slider_float(
                                tag=self.RegComponent("SpinOffset_float"),
                                label="旋转偏移量",
                                default_value=0,
                                max_value=0.25,
                                min_value=-0.25,
                            )
                            dpg.add_slider_float(
                                tag=self.RegComponent("ReverseOffset_float"),
                                label="倒车偏移量",
                                default_value=0,
                                max_value=0.25,
                                min_value=-0.25,
                            )
                            dpg.add_separator()
                            dpg.add_text("初始方向")
                            dpg.add_radio_button(
                                ("上", "右", "下", "左"),
                                horizontal=True,
                                default_value="上",
                                tag=self.RegComponent("OriginDirection_combo"),
                            )
                            dpg.add_drag_intx(
                                tag=self.RegComponent("Scan_StartPoint_intx"),
                                size=2,
                                enabled=False,
                                label="起始点",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_drag_intx(
                                tag=self.RegComponent("Scan_EndPoint_intx"),
                                size=2,
                                enabled=False,
                                label="终止点",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_separator()
                            with dpg.group(horizontal=True):
                                dpg.add_button(
                                    label="开始扫描", callback=self.__StartScan_Callback, height=30
                                )
                                dpg.add_button(
                                    label="二维码导入", callback=self.__ScanQRCode_Callback, height=30
                                )
                            with dpg.group(
                                horizontal=True, show=False, tag=self.RegComponent("Scan_WaitGroup")
                            ):
                                dpg.add_loading_indicator()
                                dpg.add_text(default_value="等待遍历完成...")
                with dpg.tab(label="开始推箱"):
                    with dpg.group(horizontal=True):
                        self.solveMapGrid = MapGrid(4, self.__SetPoint_Callback, buttonEnable=False)
                        with dpg.child_window(width=-1, height=370):
                            dpg.add_text()
                            dpg.add_drag_intx(
                                tag=self.RegComponent("Solve_StartPoint_intx"),
                                size=2,
                                enabled=False,
                                label="起始点",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_drag_intx(
                                tag=self.RegComponent("Solve_EndPoint_intx"),
                                size=2,
                                enabled=False,
                                label="终止点",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_separator()
                            dpg.add_button(label="开始寻路", callback=self.__StartSolve_Callback, height=30)
                            with dpg.group(
                                horizontal=True, show=False, tag=self.RegComponent("Solve_WaitGroup")
                            ):
                                dpg.add_loading_indicator()
                                dpg.add_text(default_value="等待演示完成...")
            ImOutput.Out()


if __name__ == "__main__":

    def ToggleShowCamera_Callback():
        CameraService.Service.showCamera = not CameraService.Service.showCamera

    def ToggleQRCodeModule_Callback():
        CameraService.Service.enableQRCodeModule = not CameraService.Service.enableQRCodeModule

    def ToggleGestureModule_Callback():
        CameraService.GestureModule.enable = not CameraService.GestureModule.enable

    def ProjectInfo_Callback():
        ImOutput.Out.Println(
            """
            ---关于本项目--------------------------------------------
            本项目基于4WD车型小车, 实现小车自主完成简化版的推箱子小游戏
            (也是我们神秘的工程实践项目)
            本项目依照CC-BY-SA-3.0协议开源
            特别感谢: 我的组员, dearpygui, opencv
            """
        )

    dpg.create_context()

    with dpg.font_registry():
        with dpg.font("Hei.ttf", 14) as font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.add_font_range(0x2190, 0x2194)
    dpg.bind_font(font)

    dpg.configure_app(docking=True, docking_space=True)
    # dpg.configure_app(init_file="dpg.ini", load_init_file=True)

    with dpg.viewport_menu_bar():
        with dpg.menu(label="开始"):
            dpg.add_menu_item(
                label="显示相机画面",
                check=True,
                default_value=CameraService.Service.showCamera,
                callback=ToggleShowCamera_Callback,
            )
            dpg.add_menu_item(
                label="启用二维码",
                check=True,
                default_value=CameraService.Service.enableQRCodeModule,
                callback=ToggleQRCodeModule_Callback,
            )
            # dpg.add_menu_item(
            #     label="启用手势检测",
            #     check=True,
            #     default_value=CameraService.GestureModule.enable,
            #     callback=ToggleGestureModule_Callback,
            # )
            dpg.add_separator()
            # dpg.add_menu_item(label="保存布局", callback=lambda: dpg.save_init_file("dpg.ini"))
            dpg.add_menu_item(label="退出")
        with dpg.menu(label="工具"):
            dpg.add_menu_item(label="性能面板", callback=dpg.show_metrics)
            dpg.add_menu_item(label="关于Imgui", callback=dpg.show_about)
            dpg.add_separator()
            dpg.add_menu_item(label="关于这个项目", callback=ProjectInfo_Callback)
    CarUI()
    ImOutput.Out.Println("你好")
    CameraService.Service.Start()
    ImOutput.Out.Println("摄像头服务已启动")
    box3.init()
    ImOutput.Out.Println("GPIO初始化")

    dpg.create_viewport(title="Simple Sokoban Solver", width=780, height=650)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()
