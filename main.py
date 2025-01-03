import tkinter as tk
from tkinter import ttk
import pygame
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController

class Controller:
    class Button:
        def __init__(self, name: str, input: int):
            self.name = name
            self.input = input
            self.pressed = False
            
        def update(self, joystick: pygame.joystick):
            self.pressed = joystick.get_button(self.input)

    class Axis:
        def __init__(self, name: str, inputX: int, inputY: int, inputPress: int, deadzone: float = 0.1):
            self.name = name
            self.inputX = inputX
            self.inputY = inputY
            self.inputPress = inputPress
            self.X = 0
            self.Y = 0
            self.deadzone = deadzone
            self.direction = (0, 0)
            self.button = super().Button(f"{self.name} press", inputPress)
            
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
            self.button.update(joystick)
            
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
            
    def __init__(self, joystick: pygame.joystick):
        self.joystick = joystick
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
        self.released = []
        
    def poll(self):
        self.pressed = []
        self.released = []
        prev_states = {}
        new_states = {}
        for key, value in self.inputs.items():
            prev_states[key] = value.pressed if hasattr(value, "pressed") else value.button.pressed
            value.update(self.joystick)
            new_states[key] = value.pressed if hasattr(value, "pressed") else value.button.pressed
        
        for key, value in new_states.items():
            if value and not prev_states[key]:
                self.pressed.append(key)
            elif not value and prev_states[key]:
                self.released.append(key)

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

class ControllerMapperApp:
    def __init__(self, root):
        # Initialize the main application
        self.root = root
        self.root.title("PS4 Controller to Keyboard/Mouse Mapper")

        # Initialize pygame for controller input handling
        pygame.init()
        pygame.joystick.init()

        # Initialize keyboard and mouse controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        # Connect to the first available joystick (controller)
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Detected controller: {self.joystick.get_name()}")
        else:
            self.joystick = None

        self.pressed_keys = set()
        
        # Define mapping categories and inputs
        self.mapping = {
            "Buttons": ["X", "Square", "Circle", "Triangle"],
            "D-Pad": ["Up", "Down", "Left", "Right"],
            "Shoulder Buttons": ["L1", "L2", "R1", "R2"],
            "Left Joystick": ["Left Up", "Left Down", "Left Left", "Left Right", "L3"],
            "Right Joystick": ["Right Up", "Right Down", "Right Left", "Right Right", "R3"],
            "Misc": ["Share", "Options", "Touchpad", "PS"]
        }

        # Store key bindings
        self.key_bindings = {key: "" for category in self.mapping for key in self.mapping[category]}
        
        # Map button and axis indices to names
        self.button_names = {
            0: "X",
            1: "Circle",
            2: "Square",
            3: "Triangle",
            4: "Share",
            5: "PS",
            6: "Options",
            7: "L3",
            8: "R3",
            9: "L1",
            10: "R1",
            11: "Up",
            12: "Down",
            13: "Left",
            14: "Right",
            15: "Touchpad"
        }
        self.axis_names = {
            0: "Left Stick X",
            1: "Left Stick Y",
            2: "Right Stick X",
            3: "Right Stick Y",
            4: "L2",
            5: "R2"
        }

        self.create_widgets()
        self.create_test_screen()
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        # self.create_rumble_tab(notebook)

        # Start polling for input
        self.poll_controller()

    def create_widgets(self):
        # Create notebook for organizing input categories
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        for category, inputs in self.mapping.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=category)

            for input_name in inputs:
                self.add_input_binding_row(frame, input_name)

    def create_test_screen(self):
        # Create a frame for testing controller inputs
        test_frame = ttk.Frame(self.root)
        test_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        label = ttk.Label(test_frame, text="Controller Input Test", font=("Arial", 14))
        label.pack(pady=5)

        self.test_output = tk.Text(test_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.test_output.pack(fill=tk.BOTH, padx=10, pady=5)
        
    # def create_rumble_tab(self, notebook):
    #     rumble_frame = ttk.Frame(notebook)
    #     notebook.add(rumble_frame, text="Rumble Test")

    #     ttk.Label(rumble_frame, text="Rumble Intensity (0-100%)").pack(pady=10)

    #     self.rumble_intensity = tk.DoubleVar(value=50)
    #     intensity_slider = ttk.Scale(rumble_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.rumble_intensity)
    #     intensity_slider.pack(fill=tk.X, padx=20, pady=5)

    #     button_frame = ttk.Frame(rumble_frame)
    #     button_frame.pack(pady=10)

    #     ttk.Button(button_frame, text="Start Rumble", command=self.start_rumble).pack(side=tk.LEFT, padx=10)
    #     ttk.Button(button_frame, text="Stop Rumble", command=self.stop_rumble).pack(side=tk.LEFT, padx=10)

    # def start_rumble(self):
    #     if self.joystick:
    #         intensity = self.rumble_intensity.get() / 100.0
    #         try:
    #             self.joystick.rumble(intensity, intensity, 3600000)  # Low and high intensity, 1 hour duration
    #             print(f"Started rumble with intensity: {intensity}")
    #         except AttributeError:
    #             print("Rumble not supported by this controller.")
    #     else:
    #         print("No controller connected.")
            
    # def stop_rumble(self):
    #     if self.joystick:
    #         try:
    #             self.joystick.rumble(0, 0, 0)
    #             print("Rumble stopped.")
    #         except AttributeError:
    #             print("Rumble not supported by this controller.")
    #     else:
    #         print("No controller connected.")
            
    def add_input_binding_row(self, frame, input_name):
        # Create a row for each input mapping
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=10, pady=5)

        label = ttk.Label(row, text=input_name, width=15)
        label.pack(side=tk.LEFT)

        entry = ttk.Entry(row, width=15, state="readonly", justify="center")
        entry.pack(side=tk.LEFT, padx=5)
        entry.insert(0, self.key_bindings[input_name])
        
        def start_listening():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, f"Listening for {input_name}...")
            entry.config(state="readonly")
            self.root.bind_all("<KeyPress>", on_key_press)

        def on_key_press(event):
            key_name = event.keysym
            self.key_bindings[input_name] = key_name
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, key_name)
            entry.config(state="readonly")
            self.root.unbind_all("<KeyPress>")

        button = ttk.Button(row, text="Bind", command=start_listening)
        button.pack(side=tk.LEFT, padx=5)

        def save_binding(event):
            self.key_bindings[input_name] = entry.get()

        entry.bind("<FocusOut>", save_binding)

        clear_button = ttk.Button(row, text="Clear", command=lambda: self.clear_binding(entry, input_name))
        clear_button.pack(side=tk.LEFT, padx=5)

    def clear_binding(self, entry, input_name):
        # Clear the binding for a specific input
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.config(state="readonly")
        self.key_bindings[input_name] = ""

    def poll_controller(self):
        # Poll the controller for input
        if self.joystick:
            pygame.event.pump()
            output_lines = []
            # Handle button inputs
            for i in range(self.joystick.get_numbuttons()):
                button_name = self.button_names[i]
                if self.joystick.get_button(i):
                    output_lines.append(f"{button_name} button pressed.")
                    self.simulate_input(button_name)
                else:
                    self.simulate_input(button_name, release=True)

            # Handle axis inputs (joysticks)
            for i in range(self.joystick.get_numaxes()):
                axis_name = self.axis_names[i]
                axis_value = self.joystick.get_axis(i)
                if i >= 4:
                    axis_value += 1
                if abs(axis_value) > 0.1:  # Deadzone
                    if i >= 4:
                        axis_value -= 1
                    output_lines.append(f"{axis_name} moved to {axis_value:.2f}.")
                    self.simulate_input(axis_name, axis_value)
                else:
                    self.simulate_input(axis_name, axis_value, release=True)

            # Display input in the test screen
            self.test_output.config(state=tk.NORMAL)
            self.test_output.delete(1.0, tk.END)
            self.test_output.insert(tk.END, "\n".join(output_lines))
            self.test_output.config(state=tk.DISABLED)
        else:
            self.test_output.config(state=tk.NORMAL)
            self.test_output.delete(1.0, tk.END)
            self.test_output.insert(tk.END, "No controller detected.")
            self.test_output.config(state=tk.DISABLED)

        # Schedule the next poll
        self.root.after(50, self.poll_controller)
    
    def simulate_input(self, input_name, value=None, release=False):
        # Simulate the input on the keyboard or mouse
        if input_name in self.axis_names.values():
            if input_name == "Left Stick X":
                input_name = "Left Left" if value < 0 else "Left Right"
            elif input_name == "Left Stick Y":
                input_name = "Left Up" if value < 0 else "Left Down"
            elif input_name == "Right Stick X":
                input_name = "Right Left" if value < 0 else "Right Right"
            elif input_name == "Right Stick Y":
                input_name = "Right Up" if value < 0 else "Right Down"
        
        action = self.key_bindings[input_name].lower()
        if action:
            try:
                key = Keybind.tkinter_key_to_pynput_key(action)
                if release and input_name in self.pressed_keys:
                    self.keyboard.release(key)
                    self.pressed_keys.discard(input_name)
                elif not release and not input_name in self.pressed_keys:
                    self.keyboard.press(key)
                    self.pressed_keys.add(input_name)
            except Exception as e:
                print(f"Error simulating input: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ControllerMapperApp(root)
    root.mainloop()
