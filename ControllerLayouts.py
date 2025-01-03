def GetControllerLayout(controller_name: str):
    """Get the controller layout for the given controller name."""
    match controller_name:
        case "PS4 Controller":
            return PS4ControllerLayout()
        case "Nintendo Switch Joy-Con (L)":
            return LeftJoyconLayout()
        case "Nintendo Switch Joy-Con (R)":
            return RightJoyconLayout()
        case "Nintendo Switch Joy-Con (L/R)":
            return DualJoyconLayout()
        
##########################
### CONTROLLER LAYOUTS ###
##########################

# Controller layouts are dictionaries that map button names to input types.
# The dictionaries are ordered in what the controller outputs as button 0, 1, 2, etc.
# This logic also applies to axis (and triggers), but they have their own output type.

def PS4ControllerLayout():
    inputs = {
        "x": 0,
        "circle": 0,
        "square": 0,
        "triangle": 0,
        "share": 0,
        "ps": 0,
        "options": 0,
        "l3": 0,
        "r3": 0,
        "l1": 0,
        "r1": 0,
        "up": 0,
        "down": 0,
        "left": 0,
        "right": 0,
        "touchpad": 0,
        "LeftStick": 1,
        "RightStick": 1,
        "l2": 2,
        "r2": 2
        }
    return inputs

def LeftJoyconLayout():
    inputs = {
        "right": 0,
        "down": 0,
        "up": 0,
        "left": 0,
        "DUMMY1": -3,
        "capture": 0,
        "minus": 0,
        "stick": 0,
        "DUMMY2": -3,
        "sl": 0,
        "sr": 0,
        "DUMMY3": -3,
        "DUMMY4": -3,
        "DUMMY5": -3,
        "DUMMY6": -3,
        "DUMMY7": -3,
        "DUMMY8": -3,
        "l": 0,
        "DUMMY9": -3,
        "zl": 0,
        "Stick": 1,
        }
    return inputs

def RightJoyconLayout():
    inputs = {
        "x": 0,
        "a": 0,
        "y": 0,
        "b": 0,
        "DUMMY1": -3,
        "home": 0,
        "plus": 0,
        "stick": 0,
        "DUMMY2": -3,
        "sl": 0,
        "sr": 0,
        "DUMMY3": -3,
        "DUMMY4": -3,
        "DUMMY5": -3,
        "DUMMY6": -3,
        "DUMMY7": -3,
        "r": 0,
        "DUMMY9": -3,
        "zr": 0,
        "Stick": 1,
        }
    return inputs

def DualJoyconLayout():
    inputs = {
        "a": 0,
        "b": 0,
        "x": 0,
        "y": 0,
        "minus": 0,
        "home": 0,
        "plus": 0,
        "stick (L)": 0,
        "stick (R)": 0,
        "l": 0,
        "r": 0,
        "up": 0,
        "down": 0,
        "left": 0,
        "right": 0,
        "capture": 0,
        "sr (R)": 0,
        "sr (L)": 0,
        "sl (R)": 0,
        "sl (L)": 0,
        "LeftStick": 1,
        "RightStick": 1,
        "zl": 2,
        "zr": 2,
        }
    return inputs