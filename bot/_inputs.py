# A method of class Bot - derived from __init__

# Global imports
import json,time

# Global variables
default_input = {"A": False, "B": False, "L": False, "R": False, "Up": False, "Down": False, "Left": False,
            "Right": False, "Select": False, "Start": False, "Light Sensor": 0, "Power": False, "Tilt X": 0,
            "Tilt Y": 0, "Tilt Z": 0, "SaveRAM": False}


def HoldButton(self, button: str):
    """
    Function to update the hold_input object
    :param button: Button to hold
    """
    self.logger.debug(f"Holding: {button}...")

    self.hold_input[button] = True
    self.hold_input_mmap.seek(0)
    self.hold_input_mmap.write(bytes(json.dumps(self.hold_input), encoding="utf-8"))

def ReleaseButton(self, button: str):
    """
    Function to update the hold_input object
    :param button: Button to release
    """
    self.logger.debug(f"Releasing: {button}...")

    self.hold_input[button] = False
    self.hold_input_mmap.seek(0)
    self.hold_input_mmap.write(bytes(json.dumps(self.hold_input), encoding="utf-8"))


def ReleaseAllInputs(self):
    """Function to release all keys in all input objects"""
    self.logger.debug(f"Releasing all inputs...")

    for button in ["A", "B", "L", "R", "Up", "Down", "Left", "Right", "Select", "Start", "Power"]:
        self.hold_input[button] = False
        self.hold_input_mmap.seek(0)
        self.hold_input_mmap.write(bytes(json.dumps(self.hold_input), encoding="utf-8"))


def PressButton(self,button: str):
    
    match button:
        case 'Left':
            button = 'l'
        case 'Right':
            button = 'r'
        case 'Up':
            button = 'u'
        case 'Down':
            button = 'd'
        case 'Select':
            button = 's'
        case 'Start':
            button = 'S'
        case 'SaveRAM':
            button = 'x'

    index = self.g_current_index
    self.input_list_mmap.seek(index)
    self.input_list_mmap.write(bytes(button, encoding="utf-8"))
    self.input_list_mmap.seek(100)  # Position 0-99 are inputs, position 100 keeps the value of the current index
    self.input_list_mmap.write(bytes([index + 1]))

    self.g_current_index += 1
    if self.g_current_index > 99:
        self.g_current_index = 0

def ButtonCombo(self, sequence: list):
    """
    Function to send a sequence of inputs and delays to the emulator
    :param sequence: List of button/wait inputs to execute
    """
    for k in sequence:
        if type(k) is int:
            self.WaitFrames(k)
        else:
            self.PressButton(k)
            self.WaitFrames(1)

def WaitFrames(self,frames: float):
    time.sleep(max((frames / 60.0) / self.GetEmu()["speed"], 0.02))
