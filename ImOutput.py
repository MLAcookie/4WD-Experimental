import dearpygui.dearpygui as dpg


class Out:
    texts: list = []
    textComponents: list = []

    def __GenStr():
        ans = ""
        for s in Out.texts:
            ans = "%s%s" % (ans, s)
        return ans

    def __Sync():
        for t in Out.textComponents:
            dpg.set_value(t, Out.__GenStr())

    def Clear():
        Out.texts = []
        Out.__Sync()

    def Print(text: str):
        if len(Out.texts) > 200:
            Out.Clear()
        print("(ImOutput): " + text, end="")
        Out.texts.append(str(text))
        Out.__Sync()

    def Println(text: str = None):
        if text == "":
            text = "(\\n)"
        Out.Print(str(text) + "\n")

    def DelteLast():
        if Out.texts == []:
            return
        Out.texts.pop()
        Out.__Sync()

    def DeleteRow(index: int):
        del Out.texts[index]
        Out.__Sync()

    def Close(self):
        Out.textComponents.remove(self.textComponent)
        dpg.delete_item(self.window)

    def OnWindowClose(self):
        Out.textComponents.remove(self.textComponent)

    def __init__(self, warp: int = 800):
        self.textComponent: int = dpg.generate_uuid()
        Out.textComponents.append(self.textComponent)
        self.window: int = dpg.generate_uuid()

        with dpg.child_window(
            label="Output", tag=self.window, width=-1, height=-1, horizontal_scrollbar=True
        ):
            dpg.add_text(tag=self.textComponent, default_value=Out.__GenStr(), wrap=warp)
