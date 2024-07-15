# 这个文件定义了一个用来生成可供小车识别的二维码的生成器
# UI也是拿dearpygui搓的
import dearpygui.dearpygui as dpg
from enum import Enum
import qrcode


class ButtonState(Enum):
    null = 0
    start = 1
    end = 2
    box = 3
    barrier = 4


class MapButton:
    stateToLable = {
        ButtonState.null: "",
        ButtonState.start: "Start",
        ButtonState.end: "End",
        ButtonState.box: "Box",
        ButtonState.barrier: "Barrier",
    }

    def SetState(self, state):
        self.buttonState = state
        dpg.configure_item(self.buttonId, label=MapButton.stateToLable[self.buttonState])

    def __ButtonClick_Callback(self, sender, data):
        swich = {
            ButtonState.null: ButtonState.start,
            ButtonState.start: ButtonState.end,
            ButtonState.end: ButtonState.box,
            ButtonState.box: ButtonState.barrier,
            ButtonState.barrier: ButtonState.null,
        }

        self.buttonState = swich[self.buttonState]
        dpg.configure_item(self.buttonId, label=MapButton.stateToLable[self.buttonState])
        self.buttonCallback(sender, data)

    def __init__(self, size: int = 75, callback=None):
        self.buttonId = dpg.generate_uuid()
        self.buttonState = ButtonState.null
        self.buttonCallback = callback
        dpg.add_button(tag=self.buttonId, height=size, width=size, callback=self.__ButtonClick_Callback)


# 程序主界面以及逻辑
class MapSettingWindow:
    def __init__(self) -> None:
        self.__components = {}
        self.__buttonMatrix = []

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

    def __SetMapSizeSlider_Callback(self, sender, data):
        dpg.delete_item(item=self.__components["MapView"], children_only=True)
        size = data
        unitSize = 360 / size - 5
        self.__buttonMatrix = []
        for i in range(size):
            self.__buttonMatrix.append([])
            with dpg.group(horizontal=True, horizontal_spacing=5, parent=self.__components["MapView"]):
                for j in range(size):
                    self.__buttonMatrix[i].append(MapButton(unitSize, self.__GenerateQR_Callback))

    def __GenerateData(self):
        size = self.GetComponentValue("SetMapSizeSlider")
        temp = "%d\n" % size
        stateToLable = {
            ButtonState.null: "",
            ButtonState.start: "Start",
            ButtonState.end: "End",
            ButtonState.box: "Box",
            ButtonState.barrier: "Barrier",
        }
        for i in range(size):
            for j in range(size):
                if self.__buttonMatrix[i][j].buttonState == ButtonState.null:
                    continue
                else:
                    s = " %d %d\n" % (j, i)
                    temp += stateToLable[self.__buttonMatrix[i][j].buttonState] + s
        return temp

    def __GenerateQR_Callback(self, sender, data):
        data = self.__GenerateData()
        img = qrcode.make(data, version=8, border=4, box_size=8)
        img.save("./data/temp.png")
        img = img.convert("RGBA")
        width, height, channels, data = dpg.load_image("./data/temp.png")
        self.SetComponentValue("ImgTexture", data)

    def ShowWindow(self) -> None:
        with dpg.window(
            tag=self.RegComponent("MainWindow"),
            label="Map Setting",
            no_resize=True,
            no_close=True,
        ):
            texture_data = []
            for i in range(0, 456 * 456):
                texture_data.append(1)
                texture_data.append(1)
                texture_data.append(1)
                texture_data.append(1)

            with dpg.texture_registry():
                dpg.add_raw_texture(
                    width=456,
                    height=456,
                    default_value=texture_data,
                    tag=self.RegComponent("ImgTexture"),
                    format=dpg.mvFormat_Float_rgba,
                )
            dpg.add_slider_int(
                tag=self.RegComponent("SetMapSizeSlider"),
                width=370,
                label="Set Map Size",
                max_value=6,
                min_value=2,
                default_value=4,
                callback=self.__SetMapSizeSlider_Callback,
            )
            size = self.GetComponentValue("SetMapSizeSlider")
            unitSize = 360 / size - 5
            self.__buttonMatrix = []
            with dpg.group(horizontal=True):
                with dpg.child_window(tag=self.RegComponent("MapView"), width=370, height=370):
                    for i in range(size):
                        self.__buttonMatrix.append([])
                        with dpg.group(horizontal=True, horizontal_spacing=5):
                            for j in range(size):
                                self.__buttonMatrix[i].append(MapButton(unitSize, self.__GenerateQR_Callback))
                with dpg.child_window(tag=self.RegComponent("QRView"), width=370, height=370):
                    with dpg.plot(width=-1, height=-1, equal_aspects=True):
                        dpg.add_plot_axis(
                            dpg.mvXAxis,
                            no_gridlines=True,
                            no_tick_labels=True,
                            no_tick_marks=True,
                        )
                        with dpg.plot_axis(
                            dpg.mvYAxis,
                            tag=self.RegComponent("PlotAxis"),
                            invert=True,
                            no_gridlines=True,
                            no_tick_labels=True,
                            no_tick_marks=True,
                        ):
                            dpg.add_image_series(
                                self.__components["ImgTexture"],
                                [0, 456],
                                [456, 0],
                            )
            dpg.add_button(
                label="Clear",
                tag=self.RegComponent("GenerateButton"),
                width=-1,
                callback=self.ClearState,
            )


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="QRCode", width=780, height=550)
    dpg.configure_app(init_file="dpg.ini", load_init_file=True)
    dpg.configure_app(docking=True, docking_space=True)

    w = MapSettingWindow()
    w.ShowWindow()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()
