from enum import Enum
import dearpygui.dearpygui as dpg
import Sokoban
import box3


class ButtonState(Enum):
    null = 0
    start = 1
    end = 2
    box = 3
    barrier = 4


class MapButton:
    def __ButtonClick_Callback(self, sender, data):
        swich = {
            ButtonState.null: ButtonState.start,
            ButtonState.start: ButtonState.end,
            ButtonState.end: ButtonState.null,
            # ButtonState.box: ButtonState.barrier,
            # ButtonState.barrier: ButtonState.null,
        }
        # stateToLable = {
        #     ButtonState.null: "",
        #     ButtonState.start: "🚩",
        #     ButtonState.end: "🏁",
        #     ButtonState.box: "📦",
        #     ButtonState.barrier: "🚧",
        # }
        stateToLable = {
            ButtonState.null: "",
            ButtonState.start: "Start",
            ButtonState.end: "End",
            ButtonState.box: "Box",
            ButtonState.barrier: "Barrier",
        }
        self.buttonState = swich[self.buttonState]
        dpg.configure_item(self.buttonId, label=stateToLable[self.buttonState])
        if self.buttonCallback is not None:
            self.buttonCallback(sender, {"state": self.buttonState, "location": self.buttonLocation})

    def SetState(self, state):
        stateToLable = {
            ButtonState.null: "",
            ButtonState.start: "Start",
            ButtonState.end: "End",
            ButtonState.box: "Box",
            ButtonState.barrier: "Barrier",
        }
        self.buttonState = state
        dpg.configure_item(self.buttonId, label=stateToLable[self.buttonState])

    def __init__(self, size: int = 75, location=(0, 0), callback=None):
        self.buttonId = dpg.generate_uuid()
        self.buttonState = ButtonState.null
        self.buttonLocation = location
        self.buttonCallback = callback
        dpg.add_button(tag=self.buttonId, height=size, width=size, callback=self.__ButtonClick_Callback)


class MapGrid:
    def __init__(self, mapSize, buttonCallback=None, initShow=True) -> None:
        self.__components = {}
        self.__buttonMatrix = []
        self.__mapSize = mapSize
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

    def CleanState(self):
        for i in self.__buttonMatrix:
            for j in i:
                j.SetState(ButtonState.null)

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
                        self.__buttonMatrix[i].append(MapButton(unitSize, (j, i), self.buttonCallback))


class CarUI:
    def __init__(self, initShow=True) -> None:
        self.__components = {}
        self.objectMatrix = []
        self.scanMapGrid = None
        self.solveMapGrid = None
        self.flag = [False, False]
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

    def __Test_Callback(self, sender, data):
        print(self)
        print(sender)
        print(data)

    def __SetPoint_Callback(self, sender, data):
        if self.flag[0] and self.flag[1]:
            self.scanMapGrid.CleanState()
            self.flag = [False, False]
            self.SetComponentValue("StartPoint_intx", [-1, -1, 0, 0])
            self.SetComponentValue("EndPoint_inx", [-1, -1, 0, 0])
            return
        point = data["location"]
        state = data["state"]
        if state == ButtonState.start:
            if -1 in self.GetComponentValue("StartPoint_intx"):
                self.SetComponentValue("StartPoint_intx", [point[0], point[1], 0, 0])
                self.flag[0] = True

        elif state == ButtonState.end:
            if -1 in self.GetComponentValue("EndPoint_inx"):
                self.SetComponentValue("EndPoint_inx", [point[0], point[1], 0, 0])
                self.flag[1] = True

    def __StartScan_Callback(self, sender, data):
        temp = box3.bfs_explore_map()
        size = len(temp)
        for i in range(size):
            for j in range(size):
                if temp[j][i] == "O":
                    pass
                elif temp[j][i] == "B":
                    pass

    def __ScanQRCode_Callback(self, sender, data):
        pass

    def __StartSolve_Callback(self, sender, data):
        pass

    def Show(self):
        with dpg.window(
            tag=self.RegComponent("MainWindow"),
            label="CarUI",
            no_resize=True,
            no_close=True,
            no_collapse=True,
            no_move=True,
        ):
            with dpg.tab_bar():
                with dpg.tab(label="Scan"):
                    with dpg.group(horizontal=True):
                        self.scanMapGrid = MapGrid(4, self.__SetPoint_Callback)
                        with dpg.child_window(width=-1, height=370):
                            dpg.add_text()
                            dpg.add_drag_intx(
                                tag=self.RegComponent("StartPoint_intx"),
                                size=2,
                                enabled=False,
                                label="Start Point",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_drag_intx(
                                tag=self.RegComponent("EndPoint_inx"),
                                size=2,
                                enabled=False,
                                label="End Point",
                                default_value=[-1, -1, 0, 0],
                                max_value=3,
                                min_value=0,
                            )
                            dpg.add_button(label="Start Scan", callback=self.__StartScan_Callback)
                            dpg.add_button(label="Scan From QR Code", callback=self.__ScanQRCode_Callback)
                with dpg.tab(label="Solve"):
                    with dpg.group(horizontal=True):
                        self.solveMapGrid = MapGrid(4, self.__SetPoint_Callback)
                        with dpg.child_window(width=-1, height=370):
                            dpg.add_text()
                            dpg.add_button(label="Start Solve", callback=self.__StartSolve_Callback)


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="QRCode", width=780, height=550)
    dpg.configure_app(init_file="dpg.ini", load_init_file=True)
    dpg.configure_app(docking=True, docking_space=True)

    CarUI()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()
