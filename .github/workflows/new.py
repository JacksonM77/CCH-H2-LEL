from drafter import *
from bakery import assert_equal
from dataclasses import dataclass

@dataclass
class State:
    volume: int
    volume_liters: int
    amps: int
    Liters_Hydrogen_Per_Minute: int
    history: list[str]
    
    
@route
def index(state: State) -> Page:
    '''
    State page
    
    Parameters: 
    State 
    
    Returns state page
    
    '''
     
    return Page(state,[
        "Welcome!",
        "This program calculates the amount of time it takes"
        " an electrolyzer to produce enough hydrogen to reach"
        " a specific LEL (Lethal Explosive Limit) in a room",
        "Your answer will require input of your room's dimensions, your electrolyzer's ampage,"
        " and the LEL you wish to find",
        Button("Start", meter_calculation),
        Button("History", calculation_history)
    ])

@route
def meter_calculation(state: State) -> Page:
    ''' User enters in dimensions of room in meters
    
    Parameters: 
    State 
    
    Returns page
    
    '''
    return Page(state, [
        "Please enter your room's dimensions in meters",
        TextBox("width", 0),
        TextBox("height", 0),
        TextBox("length", 0),
        Button("Submit", volume_calculation),
        Button("Cancel", index)
    ])

@route
def volume_calculation(state: State, width: str, length: str, height: str) -> Page:
    ''' Checks if the user's inputs are valid numbers (integers or floats) and calculates/returns volume of their room

    Parameters: 
    State
    width: str
    length: str
    height: str

    Returns page
    '''
    
    if width.replace('.', '', 1).isdigit() and length.replace('.', '', 1).isdigit() and height.replace('.', '', 1).isdigit():
        width, length, height = float(width), float(length), float(height)
        
        if width > 0 and length > 0 and height > 0:
            state.volume = width * length * height
            state.volume_liters = state.volume * 1000
            return Page(state, [ 
                "Your room's volume is " + str(state.volume) + " cubic meters",
                "Your room's volume in liters is " + str(state.volume_liters),
                Button("Continue Calculation", amps_input)              
            ])
        else:
            return Page(state, ["Error! Not a positive number!",
                                Button("Restart", index)])
    else:
        return Page(state, ["Error! Not a valid number!",
                            Button("Restart", index)])

@route
def amps_input(state: State) -> Page:
    ''' User enters in the amps of their electrolyzer '''
    return Page(state, [
        "Please enter the current (AMPS) of your electrolyzer",
        TextBox("amps", 0.0),
        Button("Submit", LEL_calculation),
        Button("Cancel", index)
    ])


@route
def LEL_calculation(state: State, amps: float) -> Page:
    ''' User enters the LEL level they'd like to find

    Parameters:
    State
    amps: float
    
    Returns page 
    '''
    if amps > 0:
        state.Liters_Hydrogen_Per_Minute = Calculation(state, amps)
        state.amps = amps
        
        return Page(state, [ 
            "You produce " + str(state.Liters_Hydrogen_Per_Minute * 1000) + " milliliters per minute",
            "Enter the LEL level you'd like to find! (50%LEL = 50)",
            TextBox("LEL", 0.0),
            Button("Continue Calculation", LEL_output)              
        ]) 
    else:
        return Page(state, [ 
            "Error! Not a positive number!",
            Button("Return to amp input screen", amps_input)
        ])


def Calculation(state: State, amps: float) -> float:
    ''' Helper function which calculates the electrochemical details
    
    Parameters:
    State
    amps: float
    
    Returns milliliters of hydrogen produced per minute
    '''
    f = 96485 # Faraday's Constant
    if amps > 0:
        L_per_minute = (amps / (2 * f)) * (22.4) * (60)
        return L_per_minute 
    else:
        return Page(state, [ 
            "Error! Not a positive number!",
            Button("Return to amp input screen", amps_input)
        ])

@route       
def LEL_output(state: State, LEL: int) -> float:
    ''' Takes liters of hydrogen produced per minute and returns
    how long it will take for the room to reach a LEL of hydrogen

    Parameters:
    State
    LEL: int
    
    Returns final result
    '''
    if int(LEL):
        mol_air = state.volume_liters / 22.4
        LEL_mol_hydrogen = mol_air * (LEL / 100 * .04)
        Time_To_LEL = (LEL_mol_hydrogen * 22.4) / state.Liters_Hydrogen_Per_Minute
    
        history_entry = "LEL: " + str(LEL) + "%, Time: " + str(Time_To_LEL) + " minutes, Amps: " + str(state.amps) + " A"
        state.history.append(history_entry)
    
    else:
        return Page(state, [ 
            "Error! Number is zero!",
            Button("Return to amp input screen", LEL_calculation)
        ])
    
    return Page(state, [ 
        "All done!",
        "The time to reach " + str(LEL) + "% LEL in your room with " + str(state.amps) + " amps is:",
        str(Time_To_LEL) + " minutes",
        Button("Another Calculation", index)
    ])

@route
def calculation_history(state: State) -> Page:
    ''' This function uses a loop to store calculations in a history page

    Parameters:
    State
    
    Returns history page
    '''
    if not state.history:
        return Page(state, [ 
            "No calculations",
            Button("Return", index)
        ])
   
    else:
        history_print = "Calculation History: "
        for calculation in state.history:
            history_print += " |" + calculation + "|"
        return Page(state, [ 
            history_print,
            Button("Return", index)
        ])
    
start_server(State(0, 0, 0, 0, []))

