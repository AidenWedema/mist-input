import pygame
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController
from ControllerLayouts import GetControllerLayout

class Controller:
    class Button:
        def __init__(self, name: str, input: int):
            self.name = name
            self.input = input
            self.pressed = False
            
        def update(self, joystick: pygame.joystick):
            self.pressed = joystick.get_button(self.input)

    class Axis:
        def __init__(self, name: str, inputX: int, inputY: int, deadzone: float = 0.1):
            self.name = name
            self.inputX = inputX
            self.inputY = inputY
            self.X = 0
            self.Y = 0
            self.deadzone = deadzone
            self.direction = (0, 0)
            
        def update(self, joystick: pygame.joystick):
            raw_x = joystick.get_axis(self.inputX)
            raw_y = joystick.get_axis(self.inputY)

            # Apply deadzone
            self.X = raw_x if abs(raw_x) > self.deadzone else 0
            self.Y = raw_y if abs(raw_y) > self.deadzone else 0
            
            self.direction = (
                -1 if self.Y < -self.deadzone else (1 if self.Y > self.deadzone else 0),
                -1 if self.X < -self.deadzone else (1 if self.X > self.deadzone else 0),
            )
            #self.button.update(joystick)
            
    class Trigger:
        def __init__(self, name: str, input: int, normal: float = 0, threshold: float = 0):
            self.name = name
            self.input = input
            self.value = 0
            self.normal = normal
            self.threshold = threshold
            self.pressed = False
            
        def update(self, joystick: pygame.joystick):
            self.value = joystick.get_axis(self.input)
            self.pressed = self.value >= self.threshold
            
    def __init__(self):
        self.input_types = [self.Button, self.Axis, self.Trigger, "DummyButton", "DummyAxis", "DummyTrigger"]
        self.joystick = None
        self.inputs = {
            "a": self.Button,
            "b": self.Button,
            "x": self.Button,
            "y": self.Button,
            "up": self.Button,
            "down": self.Button,
            "left": self.Button,
            "right": self.Button,
            "LeftStick": self.Axis,
            "RightStick": self.Axis,
            "l": self.Button,
            "r": self.Button,
            "zl": self.Trigger,
            "zr": self.Trigger,
            "start": self.Button,
            "select": self.Button,
            "home": self.Button,
            "capture": self.Button
        }
        self.pressed = []
        self.held = []
        self.released = []
        
    def set_joystick(self, joystick: pygame.joystick):
        self.joystick = joystick
        inputs = GetControllerLayout(joystick.get_name())
        self.inputs = {}
        button_count = 0
        axis_count = 0
        for key, value in inputs.items():
            input_type = self.input_types[value]
            match input_type:
                case self.Button:
                    self.inputs[key] = input_type(key, button_count)
                    button_count += 1
                case self.Axis:
                    self.inputs[key] = input_type(key, axis_count, axis_count + 1, 0.1)
                    axis_count += 2
                case self.Trigger:
                    self.inputs[key] = input_type(key, axis_count, 0, 0)
                    axis_count += 1
                case "DummyButton":
                    button_count += 1
                case "DummyAxis":
                    axis_count += 2
                case "DummyTrigger":
                    axis_count += 1
        
    def poll(self):
        """Poll the controller for input and update the controller's internal state.\n\nRaises an `Exception` if no joystick is set."""
        if not self.joystick:
            raise Exception("No joystick set.")
        self.pressed = []
        self.held = []
        self.released = []
        prev_states = {}
        new_states = {}
        for key, value in self.inputs.items():
            if hasattr(value, "pressed"):
                prev_states[key] = value.pressed
                value.update(self.joystick)
                new_states[key] = value.pressed
        
        for key, value in new_states.items():
            if value and not prev_states[key]:
                self.pressed.append(key)
            elif not value and prev_states[key]:
                self.released.append(key)
            elif value and prev_states[key]:
                self.held.append(key)

class Keybind:
    def __init__(self, name, type, controller_input, **kwargs):
        self.name = name                                    # The name of this keybind
        self.type = type                                    # The type of this keybind, can be "button", "axis" or "trigger". bu
        self.controller_input = controller_input            # The input on the controller that triggers this keybind
        self.bound_key = None                               # The key bound to this keybind
        self.is_pressed = False                             # Whether the key is currently pressed on the keyboard
        self.default = kwargs.get("default", None)          # The default value of the controller input, IE. the output of the controller when the button/axis is not pressed
        self.deadzone = kwargs.get("deadzone", 0.1)         # The deadzone of the axis
        self.trigger = kwargs.get("trigger", 0)             # The trigger value of the trigger

    def bind_key(self, key):
        self.bound_key = self.tkinter_key_to_pynput_key(key) if type(key) != type(Key) else key

    def clear_key(self):
        self.bound_key = None
        
    def poll(self, joystick: pygame.joystick, keyboard: KeyboardController):
        if not self.bound_key:
            return

        if self.type == "button":
            self.input_button(joystick, keyboard)
        elif self.type == "axis":
            self.input_axis(joystick, keyboard)
        elif self.type == "trigger":
            self.input_trigger(joystick, keyboard)
            
    def input_button(self, joystick, keyboard):
        press = joystick.get_button(self.controller_input)
        if press and not self.is_pressed:
            self.simulate_input(keyboard, press=True)
        elif not press and self.is_pressed:
            self.simulate_input(keyboard, press=False)
            
    def input_axis(self, joystick, keyboard):
        axis_value = joystick.get_axis(self.controller_input)
        if abs(axis_value) > 0.1:
            self.simulate_input(keyboard, press=True)
        else:
            self.simulate_input(keyboard, press=False)
            
    def input_trigger(self, joystick, keyboard):
        press = joystick.get_axis(self.controller_input)
        if press and not self.is_pressed:
            self.simulate_input(keyboard, press=True)
        elif not press and self.is_pressed:
            self.simulate_input(keyboard, press=False)

    def simulate_input(self, keyboard, press=True):
        try:
            if press:
                keyboard.press(self.bound_key)
                self.is_pressed = True
            else:
                keyboard.release(self.bound_key)
                self.is_pressed = False
        except Exception as e:
            print(f"Error simulating input for {self.name}: {e}")
            
    def tkinter_key_to_pynput_key(key):
        if hasattr(Key, key):
            key = getattr(Key, key, None)
        else:
            key_translations = {'escape': Key.esc}
            key = key_translations.get(key, key)
        return key
