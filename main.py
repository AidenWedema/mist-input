import tkinter as tk
from tkinter import ttk
import pygame
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController
import VirtualController

class ControllerMapperApp:
    def __init__(self, root):
        # Initialize the main application
        self.root = root
        self.root.title("Mist Input")
        
        self.joystick = None
        self.all_joysticks = []
        self.controller = VirtualController.Controller()
        
        self.joystick_title = ttk.Label(self.root, text="Controller:", font=("Arial", 14))
        self.joystick_title.pack(pady=5)
        self.joystick_text = tk.Text(self.root, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.joystick_text.pack(fill=tk.BOTH, padx=10, pady=5)
        self.joystick_text.insert(tk.END, "Not set")
        self.joystick_picker = ttk.Combobox(self.root, values=self.all_joysticks)
        self.joystick_picker.pack(pady=5)
        self.joystick_picker.bind("<<ComboboxSelected>>", self.set_joystick)
        self.refresh_button = ttk.Button(self.root, text="Refresh", command=self.check_connected_controllers)
        self.refresh_button.pack(pady=5)

        self.create_input_screen()
        
        # Initialize pygame for controller input handling
        pygame.init()
        
        # Check for connected controllers
        self.check_connected_controllers()

        # Initialize keyboard and mouse controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
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
        self.joystick_text.config(state=tk.NORMAL)
        self.joystick_text.delete(1.0, tk.END)
        self.joystick_text.insert(tk.END, name)
        self.joystick_text.config(state=tk.DISABLED)
    
    def create_input_screen(self):
        """Create the input screen for the application."""
        # Create a frame for testing controller inputs
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        label = ttk.Label(input_frame, text="Controller Input Test", font=("Arial", 14))
        label.pack(pady=5)

        self.input_text = tk.Text(input_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, padx=10, pady=5)
        
    def poll_controller(self):
        """Poll the controller for input and send it to the keyboard and mouse."""
        if self.joystick:
            pygame.event.pump()
            output_lines = []
            
            # Poll the controller for input
            self.controller.poll()
                
            for button in self.controller.held:
                output_lines.append(f"Button {button} held")
                
            # Display the controllers internal button number of the input
            # for i in range(self.joystick.get_numbuttons()):
            #     if self.joystick.get_button(i):
            #         output_lines.append(f"Button {i} pressed")
            
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
