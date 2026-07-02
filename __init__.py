

from krita import Krita, Extension
from .GamePad import GamepadThread,sample_color,eraser


class GamepadControllerExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)
        self.app=parent
        self._thread=None

    def setup(self):
        pass

    def createActions(self, window):
        # 创建设置笔刷大小的动作
        action_size = window.createAction(
            "gamepad_start", 
            "gamepad start", 
            "tools/scripts"
        )
        action_size.triggered.connect(lambda: self.start_thread())

        # action_size = window.createAction(
        #     "gamepad_end", 
        #     "gamepad end", 
        #     "tools/scripts"
        # )
        # action_size.triggered.connect(lambda: self.end_thread())
        
    def start_thread(self):
        # self.app.action('KritaShape/KisToolBrush').trigger()
        if self._thread is None:
            self._thread=GamepadThread()
            self._thread.setKeyActionMap({
                "BTN_SELECT":"edit_redo",
                "BTN_START":"edit_undo",
                "BTN_TL":"view_zoom_out",
                "ABS_Z":"view_zoom_in",
                "ABS_RZ":eraser,#"erase_action",
                "BTN_TR":sample_color,
                "BTN_THUMBL":"zoom_to_fit",
                "BTN_WEST":"decrease_brush_size",
                "BTN_NORTH":"increase_brush_size",
                "BTN_SOUTH":"decrease_opacity",
                "BTN_EAST":"increase_opacity",
            })
            self._thread.start()
        else:
            self.end_thread()
            self._thread=None

    def end_thread(self):
        self._thread.running=False

Krita.instance().addExtension(GamepadControllerExtension(Krita.instance()))

