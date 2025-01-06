# Mist Input

Mist Input is a Python application that allows users to map controller inputs to keyboard and mouse actions. It supports various controllers, including PS4 and Nintendo Switch Joy-Cons, and provides a graphical interface for configuring keybindings.
The name comes from steam input, since it is very similar to that and mist is a form of steam, and it sounds like 'missed input', which i think is funny. 

## Features

- Detect and display connected controllers
- Map controller buttons, axes, and triggers to keyboard and mouse inputs
- Support for special inputs like mouse buttons and cursor movements
- Turbo mode for repeated key presses while a button is held
- Advanced keybinding configuration window

## Roadmap
- More controller support. Currently only ps4 and switch joy-con are supported. Pygame does recognise other controllers, but no layout exists for them. This also brings me to the next feature:
- Customizable controller layouts. This would help suport all controllers pygame is able to detect, since if no layout is pressent you can just configure your own.
- Storing controller layouts in json. Currently all controller layouts are found in [ControllerLayouts.py](https://github.com/AidenWedema/mist-input/blob/main/ControllerLayouts.py), but it would be better to store these in json format. This would make editing layouts easier.
- Saving keybind configurations. Being able to save the current keybinds on a controller would mean you don't have to configure all keybinds everytime you start the program.
- Beter mouse movement. Currently the mouse can only be moved in 8 directions. This is kind of annoying if you bind the mouse to a joystick (axis). It would be great if the mouse would move relative to the sticks direction.
- Probably more as the project grows.

## Requirements

- Python 3.x
- `pygame` library
- `pynput` library
- `tkinter` library (usually included with Python)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/AidenWedema/mist-input.git
    cd mist-input
    ```

2. Install the required libraries:
    ```sh
    pip install pygame pynput
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. The main window will open, displaying the connected controllers and an input display. If no controllers are detected, click the "Refresh" button.

3. Select a controller from the dropdown menu.

4. Use the "Keybinds" tab to bind controller inputs to keyboard and mouse actions. Click "Bind" to start listening for a key press, "Clear" to remove a binding, and "Edit" to open the advanced keybind configuration window.

5. Use the advanced keydind configuration window to do multiple things from a single input, like binding the joy-con's `home` button to `alt + f4`. This window also contains some special inputs that aren't detected by the normal "Bind" button, such as all mouse functions and more.

## File Structure

- [main.py](https://github.com/AidenWedema/mist-input/blob/main/main.py): Main application file that initializes the GUI and handles controller input polling.
- [KeyConfigWindow.py](https://github.com/AidenWedema/mist-input/blob/main/KeyConfigWindow.py): Defines the [KeyConfigWindow](https://github.com/AidenWedema/mist-input/blob/cc04b03aadc11bf45e54fdc52a642d4c02d3f03e/KeyConfigWindow.py#L4) class for advanced keybinding configuration.
- [VirtualController.py](https://github.com/AidenWedema/mist-input/blob/main/VirtualController.py): Defines the [Controller](https://github.com/AidenWedema/mist-input/blob/cc04b03aadc11bf45e54fdc52a642d4c02d3f03e/VirtualController.py#L87) and [Keybind](https://github.com/AidenWedema/mist-input/blob/cc04b03aadc11bf45e54fdc52a642d4c02d3f03e/VirtualController.py#L6) classes for simulating keyboard and mouse inputs.
- [ControllerLayouts.py](https://github.com/AidenWedema/mist-input/blob/main/ControllerLayouts.py): Contains the controller layout definitions for supported controllers.
