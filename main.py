"""
Mobile Calculator App (Kivy)
A calculator built with Kivy that runs on Android/iOS and uses real
haptic feedback (vibration) when buttons are pressed.

Requirements:
    pip install kivy plyer

To package for Android, use Buildozer (https://buildozer.readthedocs.io).
Make sure to add these permissions in buildozer.spec:
    android.permissions = VIBRATE

Color scheme:
- Background: white
- Number buttons (0-9, .): yellow
- Operation buttons (+, -, ×, ÷, %, (, ), =, C, X): blue

Vibration pattern (different feedback per button type):
- Numbers: one very short buzz
- Operations (+ - × ÷ % ( ) =): one medium buzz
- Delete buttons (C, X): two short buzzes in a row (distinct "delete" feel)
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp, dp
from kivy.uix.widget import Widget

# Try to import the vibrator. On a desktop machine (no phone), it may not
# exist, so we fall back gracefully and simply skip vibration.
try:
    from plyer import vibrator
    VIBRATION_AVAILABLE = True
except Exception:
    VIBRATION_AVAILABLE = False


# ---------- Colors (RGBA, values from 0 to 1 for Kivy) ----------
BG_COLOR = (1, 1, 1, 1)                  # white background
NUMBER_BTN_COLOR = (1, 0.843, 0, 1)      # yellow (#FFD700)
OPERATION_BTN_COLOR = (0.118, 0.565, 1, 1)  # blue (#1E90FF)
TEXT_ON_NUMBER = (0, 0, 0, 1)            # black text on yellow buttons
TEXT_ON_OPERATION = (1, 1, 1, 1)         # white text on blue buttons

NUMBER_LABELS = set("0123456789.")
DELETE_LABELS = {"C", "X"}


def vibrate_for(label):
    """
    Trigger a different vibration pattern depending on the button type.
    Numbers -> short single buzz
    Operations -> medium single buzz
    Delete (C, X) -> two quick buzzes
    """
    if not VIBRATION_AVAILABLE:
        return

    try:
        if label in NUMBER_LABELS:
            vibrator.vibrate(0.02)  # very short buzz (20ms)

        elif label in DELETE_LABELS:
            # Pattern: [delay, vibrate, delay, vibrate] in seconds
            # Two short buzzes to feel distinct from a normal press
            vibrator.pattern([0, 0.05, 0.05, 0.05])

        else:
            # Operation buttons: +, -, ×, ÷, %, (, ), =
            vibrator.vibrate(0.08)  # medium buzz (80ms)
    except (NotImplementedError, Exception):
        # Some platforms/devices don't support patterns or vibration at all
        pass


class CalculatorLayout(BoxLayout):
    """Main layout: display on top, button grid below."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # Give the whole app a white background
        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        Window.bind(on_resize=self._update_bg)

        self.expression = ""

        self.display = TextInput(
            text="0",
            font_size=sp(46),
            size_hint=(1, None),
            height=dp(90),
            readonly=True,
            multiline=False,
            halign="right",
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_blink=False,
        )
        self.add_widget(self.display)

        # Flexible empty space above the buttons, so the keypad sits lower
        # on the screen and is easier to reach with one hand/thumb.
        self.add_widget(Widget(size_hint=(1, 1)))

        BTN_HEIGHT = dp(75)

        grid = GridLayout(
            cols=4,
            spacing=4,
            padding=4,
            size_hint=(1, None),
            row_default_height=BTN_HEIGHT,
            row_force_default=True,
        )
        grid.bind(minimum_height=grid.setter("height"))

        buttons = [
            "C", "X", "(", ")",
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "-",
            "0", ".", "%", "+",
        ]

        for label in buttons:
            is_number = label in NUMBER_LABELS
            btn = Button(
                text=label,
                font_size=sp(31),
                background_normal="",
                background_color=NUMBER_BTN_COLOR if is_number else OPERATION_BTN_COLOR,
                color=TEXT_ON_NUMBER if is_number else TEXT_ON_OPERATION,
            )
            btn.bind(on_press=self.on_button_press)
            grid.add_widget(btn)

        self.add_widget(grid)

        # "=" gets its own full-width row for emphasis
        equals_btn = Button(
            text="=",
            font_size=sp(33),
            size_hint=(1, None),
            height=BTN_HEIGHT,
            background_normal="",
            background_color=OPERATION_BTN_COLOR,
            color=TEXT_ON_OPERATION,
        )
        equals_btn.bind(on_press=self.on_button_press)
        self.add_widget(equals_btn)

        # A little breathing room below the buttons (thumb-friendly margin)
        self.add_widget(Widget(size_hint=(1, None), height=dp(15)))

    def _update_bg(self, *args):
        self.bg_rect.size = Window.size
        self.bg_rect.pos = self.pos

    def on_button_press(self, instance):
        label = instance.text
        vibrate_for(label)

        if label == "C":
            self.expression = ""
            self.display.text = "0"

        elif label == "X":
            self.expression = self.expression[:-1]
            self.update_display()

        elif label == "=":
            self.calculate_result()

        elif label == "%":
            self.calculate_result(as_percentage=True)

        else:
            symbol_map = {"×": "*", "÷": "/"}
            actual_char = symbol_map.get(label, label)

            if self.expression == "0":
                self.expression = ""
            self.expression += actual_char
            self.update_display()

    def update_display(self):
        """Show the expression using friendly symbols (× and ÷)."""
        display_text = self.expression.replace("*", "×").replace("/", "÷")
        self.display.text = display_text if display_text else "0"
        # Move cursor to the end so long expressions stay readable
        self.display.cursor = (len(self.display.text), 0)

    def calculate_result(self, as_percentage=False):
        try:
            result = eval(self.expression)
            if as_percentage:
                result = result / 100
            self.expression = str(result)
            self.update_display()
        except ZeroDivisionError:
            self.display.text = "Error: Div by 0"
            self.expression = ""
        except Exception:
            self.display.text = "Error"
            self.expression = ""


class CalculatorApp(App):
    def build(self):
        self.title = "Simple Calculator"
        return CalculatorLayout()


if __name__ == "__main__":
    CalculatorApp().run()
