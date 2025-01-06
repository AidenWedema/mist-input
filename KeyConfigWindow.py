import tkinter as tk
from tkinter import ttk

class KeyConfigWindow:
    def __init__(self, root, keybind):
        self.root = root
        self.root.title("Config")
        
        self.keybind = keybind
        
        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        
        # Create a scrollable frame for all_inputs
        self.all_inputs_frame = ttk.Frame(self.root)
        self.all_inputs_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.all_inputs_frame)
        self.scrollbar = ttk.Scrollbar(self.all_inputs_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scrollable area
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Frame for buttons
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.listen_button = ttk.Button(self.buttons_frame, text="Listen", command=self.listen)
        self.listen_button.pack(pady=10)

        # Input text area
        self.input_text = tk.Text(self.root, height=10, wrap=tk.WORD)
        self.input_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        self.input_text.insert(tk.END, keybind.bound_key)
    
    def _on_mousewheel(self, event):
        """Scroll the canvas with the mouse wheel."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def listen(self):
        def on_key_press(event):
            key_name = event.keysym
            output = ""
            if len(self.input_text.get("1.0", "end-1c")) != 0:
                output += " + "
            output += f"'{key_name}'"
            self.input_text.insert(tk.END, output)
            self.root.unbind_all("<KeyPress>")
        self.root.bind_all("<KeyPress>", on_key_press)
