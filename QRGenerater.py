import dearpygui.dearpygui as dpg
from enum import Enum


class ButtonState(Enum):
    null = 0
    start = 1
    end = 2
    box = 3
    barrier = 4


class MapButton:
    def __ButtonClickCallback(self):
        swich = {
            ButtonState.null: ButtonState.start,
            ButtonState.start: ButtonState.end,
            ButtonState.end: ButtonState.box,
            ButtonState.box: ButtonState.barrier,
            ButtonState.barrier: ButtonState.null,
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

    def __init__(self, size: int = 75):
        self.buttonId = dpg.generate_uuid()
        self.buttonState = ButtonState.null

        dpg.add_button(tag=self.buttonId, height=size, width=size, callback=self.__ButtonClickCallback)


class MapSettingWindow:
    def __init__(self) -> None:
        self.__components = {}

    def RegComponent(self, name: str) -> int:
        self.__components[name] = dpg.generate_uuid()
        return self.__components[name]

    def GetComponentValue(self, name: str) -> any:
        return dpg.get_value(self.__components[name])

    def SetComponentValue(self, name: str, value: any) -> None:
        dpg.set_value(self.__components[name], value)

    def ConfigComponent(self, name: str, **kwargs: any) -> None:
        dpg.configure_item(self.__components[name], **kwargs)

    def ShowWindow(self) -> None:
        with dpg.window(
            tag=self.RegComponent("MainWindow"),
            label="New EVM Session",
            width=410,
            height=500,
            no_resize=True,
            no_close=True,
        ):
            dpg.add_slider_int(
                tag=self.RegComponent("SetMapSize"),
                width=340,
                label="Set Map Size",
                max_value=6,
                min_value=2,
                default_value=4,
            )
            with dpg.child_window(width=360, height=360):
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    MapButton()
                    MapButton()
                    MapButton()
                    MapButton()
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    MapButton()
                    MapButton()
                    MapButton()
                    MapButton()
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    MapButton()
                    MapButton()
                    MapButton()
                    MapButton()
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    MapButton()
                    MapButton()
                    MapButton()
                    MapButton()
            dpg.add_button(
                label="Generate",
                tag=self.RegComponent("GenerateButton"),
                width=0,
            )


if __name__ == "__main__":
    dpg.create_context()
    dpg.create_viewport(title="Test", width=800, height=600)
    dpg.configure_app(init_file="dpg.ini", load_init_file=True)
    dpg.configure_app(docking=True, docking_space=True)

    w = MapSettingWindow()
    w.ShowWindow()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()

    dpg.destroy_context()
