import tkinter as tk
from tkinter import ttk

class KeyConfigWindow:
    def __init__(self, root, keybind, entry):
        self.root = root
        self.root.title("Config")
        self.root.bind("<Destroy>", self.on_destroy)
        
        self.keybind = keybind
        self.entry = entry
        
        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        
        # Create a scrollable frame for all_inputs
        self.all_inputs_frame = ttk.Frame(self.root, width=10, borderwidth=2, relief="groove")
        self.all_inputs_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.all_inputs_frame, width=10)
        self.scrollbar = ttk.Scrollbar(self.all_inputs_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, width=10)

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
        
        self.create_special_inputs()
        
        # Frame for buttons
        self.buttons_frame = ttk.Frame(self.root, borderwidth=2, relief="groove")
        self.buttons_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.listen_button = ttk.Button(self.buttons_frame, text="Listen", command=self.listen)
        self.listen_button.pack(pady=10)
        
        self.save_button = ttk.Button(self.buttons_frame, text="Save", command=self.save)
        self.save_button.pack(pady=10)

        # Input text area
        self.input_text = tk.Text(self.root, height=10, wrap=tk.WORD)
        self.input_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        for key in keybind.bound_keys:
            output = ""
            if len(self.input_text.get("1.0", "end-1c")) != 0:
                output += " + "
            output += f"'{key}'"
            self.input_text.insert(tk.END, output)
    
    def _on_mousewheel(self, event):
        """Scroll the canvas with the mouse wheel."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        
    def on_destroy(self, event):
        if event.widget != self.root:
            return
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        for key in self.keybind.bound_keys:
            self.entry.insert(tk.END, key)
        self.entry.config(state="readonly")
        
    def create_special_inputs(self):
        self.special_inputs = {
            "mouse left": "m_left",
            "mouse right": "m_right",
            "mouse middle": "m_middle",
            "cursor up": "m_move_up",
            "cursor down": "m_move_down",
            "cursor left": "m_move_left",
            "cursor right": "m_move_right",
            "scroll up": "m_scroll_up",
            "scroll down": "m_scroll_down",
            "scroll left": "m_scroll_left",
            "scroll right": "m_scroll_right",
            "Tab": "tab",
            "Enter": "return",
            "Alt": "alt",
        }
        
        for key, value in self.special_inputs.items():
            button = ttk.Button(self.scrollable_frame, text=key, command=lambda value=value: self.insert_key(value))
            button.config(width=20)
            button.pack(pady=0)
            
    def insert_key(self, key):
        output = ""
        if len(self.input_text.get("1.0", "end-1c")) != 0:
            output += " + "
        output += f"'{key}'"
        self.input_text.insert(tk.END, output)
            
    def listen(self):
        def on_key_press(event):
            self.insert_key(event.keysym)
            self.root.unbind_all("<KeyPress>")
        self.root.bind_all("<KeyPress>", on_key_press)
        
    def save(self):
        inputs = self.input_text.get("1.0", "end-1c")
        inputs = inputs.strip().replace("'", "")
        keys = inputs.split(" + ")
        self.keybind.clear_key()
        for key in keys:
            self.keybind.bind_key(key)
        
