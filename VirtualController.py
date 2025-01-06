import pygame
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
from ControllerLayouts import GetControllerLayout

class Keybind:
    def __init__(self, keyboard: KeyboardController=KeyboardController(), mouse: MouseController=MouseController()):
        self.bound_keys = []                                # The key bound to this keybind
        self.is_pressed = False                             # Whether the key is currently pressed on the keyboard
        self.while_pressed = False                          # Whether the key should be pressed repeatedly while self.is_pressed is True
        self.keyboard = keyboard                            # The keyboard controller to use for simulating input
        self.mouse = mouse                                  # The mouse controller to use for simulating input

    def bind_key(self, key):
        pynput_key = self.tkinter_key_to_pynput_key(key)# if type(key) != type(Key) else key
        if pynput_key not in self.bound_keys:
            self.bound_keys.append(pynput_key)

    def clear_key(self):
        self.bound_keys = []
        
    def start(self):
        self.is_pressed = True
        self.simulate_input()
        
    def stop(self):
        self.is_pressed = False
        self.simulate_input()
        
    def always(self):
        self.while_pressed = True
        self.is_pressed != self.is_pressed
        self.simulate_input()

    def simulate_input(self):
        if not self.bound_keys or len(self.bound_keys) == 0:
            return
        for key in self.bound_keys:
            if type(key) == Key or (type(key) == str and not key.startswith("m_")):
                try:
                    if self.is_pressed:
                        self.keyboard.press(key)
                        self.is_pressed = True
                    else:
                        self.keyboard.release(key)
                        self.is_pressed = False
                except Exception as e:
                    print(f"Error simulating input for {key}: {e}")
            elif type(key) == Button:
                try:
                    if self.is_pressed:
                        self.mouse.press(key)
                        self.is_pressed = True
                    else:
                        self.mouse.release(key)
                        self.is_pressed = False
                except Exception as e:
                    print(f"Error simulating input for {key}: {e}")
            else:
                key = key.replace("m_", "")
                if key.startswith("move_") and self.is_pressed:
                    key = key.replace("move_", "")
                    directions = {"up": (0, -10), "down": (0, 10), "left": (-10, 0), "right": (10, 0)}
                    self.mouse.move(directions[key][0], directions[key][1])
                elif key.startswith("scroll_") and self.is_pressed:
                    key = key.replace("scroll_", "")
                    directions = {"up": (0, 1), "down": (0, -1)}
                    self.mouse.scroll(directions[key][0], directions[key][1])
                
    def tkinter_key_to_pynput_key(self, key):
        key = key.lower()
        if key.startswith("m_"):
            if not key.startswith("m_move_"):
                if hasattr(Button, key):
                    key = getattr(Button, key, None)
                else:
                    key_translations = {'m_left': Button.left, 'm_right': Button.right, 'm_middle': Button.middle}
                    key = key_translations.get(key, key)
        else:
            if hasattr(Key, key):
                key = getattr(Key, key, None)
            else:
                key_translations = {'escape': Key.esc, 'return': Key.enter}
                key = key_translations.get(key, key)
        return key

class Controller:
    class Input:
        def __init__(self, name: str):
            self.name = name            # The name of the input
            self.keybind = None         # The keybind associated with the input.This is a Keybind object for Button and Trigger inputs and a dictionary of Keybind objects for Axis inputs
            self.changed = False        # Whether the input has changed state since the last poll
            
    class Button(Input):
        def __init__(self, name: str, input: int):
            super().__init__(name)
            self.input = input
            self.pressed = False
            self.last_pressed = False
            self.keybind = Keybind()
            
        def update(self, joystick: pygame.joystick):
            self.last_pressed = self.pressed
            self.pressed = joystick.get_button(self.input)
            self.changed = self.last_pressed != self.pressed
            
            if self.pressed and self.keybind.while_pressed:
                self.keybind.always()
                
            elif self.changed:
                if self.pressed:
                    self.keybind.start()
                else:
                    self.keybind.stop()

    class Axis(Input):
        def __init__(self, name: str, inputX: int, inputY: int, deadzone: float=0.2):
            super().__init__(name)
            self.inputX = inputX
            self.inputY = inputY
            self.deadzone = deadzone
            self.X = 0
            self.Y = 0
            self.direction = (0, 0)
            self.last_direction = (0, 0)
            self.keybind = {
                "up": Keybind(),
                "down": Keybind(),
                "left": Keybind(),
                "right": Keybind(),
            }
            
        def update(self, joystick: pygame.joystick):
            raw_x = joystick.get_axis(self.inputX)
            raw_y = joystick.get_axis(self.inputY)

            # Apply deadzone
            self.X = raw_x if abs(raw_x) > self.deadzone else 0
            self.Y = raw_y if abs(raw_y) > self.deadzone else 0
            
            self.last_direction = self.direction
            self.direction = (
                -1 if self.Y < -self.deadzone else (1 if self.Y > self.deadzone else 0),
                -1 if self.X < -self.deadzone else (1 if self.X > self.deadzone else 0),
            )
            self.changed = (self.direction[0] != self.last_direction[0], self.direction[1] != self.last_direction[1])
            
            if self.direction[0] == -1 and self.keybind["up"].while_pressed:
                self.keybind["up"].always()
            if self.direction[0] == 1 and self.keybind["down"].while_pressed:
                self.keybind["down"].always()
            if self.direction[1] == -1 and self.keybind["left"].while_pressed:
                self.keybind["left"].always()
            if self.direction[1] == 1 and self.keybind["right"].while_pressed:
                self.keybind["right"].always()
            
            if self.changed[0]:
                if self.direction[0] == 1:
                    self.keybind["down"].start()
                    self.keybind["up"].stop()
                elif self.direction[0] == -1:
                    self.keybind["up"].start()
                    self.keybind["down"].stop()
                else:
                    self.keybind["up"].stop()
                    self.keybind["down"].stop()
            if self.changed[1]:
                if self.direction[1] == 1:
                    self.keybind["right"].start()
                    self.keybind["left"].stop()
                elif self.direction[1] == -1:
                    self.keybind["left"].start()
                    self.keybind["right"].stop()
                else:
                    self.keybind["right"].stop()
                    self.keybind["left"].stop()

    class Trigger(Input):
        def __init__(self, name: str, input: int, normal: float = 0, threshold: float = 0):
            super().__init__(name)
            self.input = input
            self.value = 0
            self.normal = normal
            self.threshold = threshold
            self.pressed = False
            self.last_pressed = False
            self.keybind = Keybind()
            
        def update(self, joystick: pygame.joystick):
            self.value = joystick.get_axis(self.input)
            self.last_pressed = self.pressed
            self.pressed = self.value >= self.threshold
            self.changed = self.last_pressed != self.pressed

            if self.pressed and self.keybind.while_pressed:
                self.keybind.always()
                
            elif self.changed:
                if self.pressed:
                    self.keybind.start()
                else:
                    self.keybind.stop()
            
    def __init__(self):
        self.input_types = [self.Button, self.Axis, self.Trigger, "DummyButton", "DummyAxis", "DummyTrigger"] # Dummy types are used for controllers that don't have buttons or axes in numerical order (cough cough. joycons. cough)
        self.joystick = None
        self.inputs = {}
        self.pressed = []
        self.held = []
        self.released = []
        self.sticks = []
        
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
                    self.sticks.append(self.inputs[key])
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
        
        # Reset the lists of pressed, held, and released buttons
        self.pressed = []
        self.held = []
        self.released = []
        
        # Dictionaries to store the previous and new states of the inputs
        prev_states = {}
        new_states = {}
        
        # Iterate over all inputs and update their states
        for key, value in self.inputs.items():
            # Check if the input has a "pressed" attribute. Applies to buttons and triggers
            if hasattr(value, "pressed"):
                # Store the previous state
                prev_states[key] = value.pressed
                # Update the input state
                value.update(self.joystick)
                # Store the new state
                new_states[key] = value.pressed
            else:
                value.update(self.joystick)
        
        # Determine which buttons are pressed, held, or released
        for key, value in new_states.items():
            if value and not prev_states[key]:
                self.pressed.append(key)
            elif not value and prev_states[key]:
                self.released.append(key)
            elif value and prev_states[key]:
                self.held.append(key)
