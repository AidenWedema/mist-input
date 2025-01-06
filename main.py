import tkinter as tk
from tkinter import ttk
import pygame
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController
import VirtualController
from KeyConfigWindow import KeyConfigWindow

class ControllerMapperApp:
    def __init__(self, root):
        # Initialize the main application
        self.root = root
        self.root.title("Mist Input")

        # Initialize pygame for controller input handling
        pygame.init()
        
        # Initialize keyboard and mouse controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        self.joystick = None
        self.all_joysticks = []
        self.controller = VirtualController.Controller()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_input_screen()
        self.create_keybind_screen()
        
        # Check for connected controllers
        self.check_connected_controllers()
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Refresh rate in milliseconds
        self.refresh_rate = 10
        
        self.poll_controller()
        
    def check_connected_controllers(self):
        """Check for connected controllers and display them in the text box."""
        self.joystick = None
        self.all_joysticks = []
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete(1.0, tk.END)
        if pygame.joystick.get_init():
            pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            self.input_text.insert(tk.END, "No controllers detected.")
        names = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            names.append(joystick.get_name())
            self.all_joysticks.append(joystick)
            self.input_text.insert(tk.END, f"Detected controller: {joystick.get_name()}\n")
        self.joystick_picker.config(values=names)
        self.input_text.config(state=tk.DISABLED)
        
    def set_joystick(self, event):
        """Set the joystick to the selected one."""
        name = self.joystick_picker.get()
        self.joystick = self.all_joysticks[self.joystick_picker.current()]
        self.controller.set_joystick(self.joystick)
        for key, value in self.controller.inputs.items():
            if hasattr(value, "pressed"):
                self.create_keybind_row(self.notebook.winfo_children()[1], key, value.keybind)
            else:
                for k, v in value.keybind.items():
                    self.create_keybind_row(self.notebook.winfo_children()[1], f"{key} {k}", v)
    
    def create_input_screen(self):
        """Create the input screen for the application."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Input")
        
        self.joystick_title = ttk.Label(frame, text="Controller:", font=("Arial", 14))
        self.joystick_title.pack(pady=5)
        self.joystick_picker = ttk.Combobox(frame, values=self.all_joysticks)
        self.joystick_picker.pack(pady=5)
        self.joystick_picker.bind("<<ComboboxSelected>>", self.set_joystick)
        self.refresh_button = ttk.Button(frame, text="Refresh", command=self.check_connected_controllers)
        self.refresh_button.pack(pady=5)

        label = ttk.Label(frame, text="Controller Input Test", font=("Arial", 14))
        label.pack(pady=5)

        self.input_text = tk.Text(frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, padx=10, pady=5)
        
    def create_keybind_screen(self):
        """Create the keybind screen for the application."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Keybinds")
        
    def create_keybind_row(self, frame, name, keybind):
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=10, pady=2)

        label = ttk.Label(row, text=name, width=15)
        label.pack(side=tk.LEFT)

        entry = ttk.Entry(row, width=15, state="readonly", justify="center")
        entry.pack(side=tk.LEFT, padx=5)
    
        def start_listening():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, f"...")
            entry.config(state="readonly")
            self.root.bind_all("<KeyPress>", on_key_press)

        def on_key_press(event):
            key_name = event.keysym
            keybind.bind_key(key_name)
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, key_name)
            entry.config(state="readonly")
            self.root.unbind_all("<KeyPress>")

        button = ttk.Button(row, text="Bind", command=start_listening)
        button.pack(side=tk.LEFT, padx=5)
        
        def clear_binding():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.config(state="readonly")
            keybind.clear_key()

        clear_button = ttk.Button(row, text="Clear", command=clear_binding)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        def open_advanced_keybind_window(input):
            adv_window = tk.Toplevel(self.root)
            adv_window.grab_set()
            adv_window.transient(self.root)
            KeyConfigWindow(adv_window, input, entry)
        
        edit_button = ttk.Button(row, text="Edit", command=lambda: open_advanced_keybind_window(keybind))
        edit_button.pack(side=tk.LEFT, padx=5)
        
        while_pressed_var = tk.BooleanVar(value=False)
        def toggle_while_pressed():
            keybind.while_pressed = while_pressed_var.get()

        while_pressed_check = ttk.Checkbutton(row, text="Turbo", variable=while_pressed_var, command=toggle_while_pressed)
        while_pressed_check.pack(side=tk.LEFT, padx=5)
        
    def poll_controller(self):
        """Poll the controller for input and send it to the keyboard and mouse."""
        if self.joystick:
            pygame.event.pump()
            output_lines = []
            
            # Poll the controller for input
            self.controller.poll()
            
            for button in self.controller.pressed:
                pass
                
            for button in self.controller.released:
                pass
                
            for button in self.controller.held:
                output_lines.append(f"Button {button} held")
                
            # Display the controllers internal button number of the input
            # for i in range(self.joystick.get_numbuttons()):
            #     if self.joystick.get_button(i):
            #         output_lines.append(f"Button {i} pressed")
            
            for axis in self.controller.sticks:
                output_lines.append(f"{axis.name} at position {axis.X:.2f}, {axis.Y:.2f} {axis.direction}")
            
            # Display input in the test screen
            self.input_text.config(state=tk.NORMAL)
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, "\n".join(output_lines))
            self.input_text.config(state=tk.DISABLED)
        
        self.root.after(self.refresh_rate, self.poll_controller)

if __name__ == "__main__":
    root = tk.Tk()
    app = ControllerMapperApp(root)
    root.mainloop()
