#!/usr/bin/env python
# encoding: utf-8
"""
isec.py
Version 1.0
2/24/2011

Interface to the EGR 102 intersection hardware.
There are three possible scenarios:
If global variable simulate_hardware is True:
    simulate the hardware function
else:
    If global variable use_one_intersection is True:
        interface with a single hardware intersection
        (only intersection 1 will be valid)
    else:
        interface with all five hardware intersections
"""

import sys
import random

class InvalidIntersection(Exception):
    """An invalid intersection number was passed to an isec function"""
    pass

class InvalidLightLabel(Exception):
    """An invalid light label was passed to an isec function"""
    pass

class InvalidSensorLabel(Exception):
    """An invalid sensor label was passed to the isec.sense function"""
    pass

# Global variables (ewwww, gross)
simulate_hardware = True
use_one_intersection = True # only matters when simulate_hardware is False
sensor_value_from_user = False # only matters when simulate_hardware is True
_intersect_object = None

def hw_init():
    """Initialize the intersection hardware. Must be called before any setting of lights or use of sensors.
    
    Requires no arguments.
    Exits the program if there is an error initializing the hardware,
        because this means that the hardware cannot be used.
    Exits the program if the hardware is already initialized.
    """
    global _intersect_object
    if _intersect_object != None:
        raise SystemExit
    if simulate_hardware:
        _intersect_object = IntersectionSim()
    else:
        import hw_interface as hw_interface
        if use_one_intersection:
            _intersect_object = IntersectionHw(1, hw_interface)
        else:
            _intersect_object = IntersectionHw(5, hw_interface)            
    
def light_on(intersect_number, light_label):
    """Turn on the light given by intersection_number and light_label.
    
    Arguments:
    intersect_number: integer in range 1-5
    light_label: one of the following strings: "AR", "AY", "AG", "BR", "BY", "BG"
    Throws exception if arguments are not in these values.
    """
    _check_init()
    _intersect_object.set_light(intersect_number, light_label, True)

def light_off(intersect_number, light_label):
    """Turn off the light given by intersection_number and light_label.
    
    Arguments:
    intersect_number: integer in range 1-5
    light_label: one of the following strings: "AR", "AY", "AG", "BR", "BY", "BG"
    Throws exception if arguments are not in these values.
    """
    _check_init()
    _intersect_object.set_light(intersect_number, light_label, False)

def sense(intersect_number, sensor_label):
    """Returns True if a car is at the sensor given by intersection_number and sensor_label.
    
    Arguments:
    intersect_number: integer in range 1-5
    sensor_label: one of the following strings: "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"
    Throws exception if arguments are not in these values or if "D1" or "D2" is specified for
        a three-way intersection (#s 2-5).
    Returns:
        True if a car is present at the sensor.
        False if no car is present at the sensor.
    """
    _check_init()
    return _intersect_object.get_sense(intersect_number, sensor_label)

def hw_close():
    """Close the intersection hardware. Must be called at the end of the program.
    
    Requires no arguments.
    """
    global _intersect_object
    if _intersect_object != None:
        _intersect_object.hw_close()
        _intersect_object = None

def print_lights():
    """Prints the status of the lights to the command line
    
    Requires no arguments.
    """
    _check_init()
    _intersect_object.print_lights()

def _check_init():
    """Checks to make sure the hardware has been initialized"""
    if _intersect_object is None:
        print "Attempt to use the hardware without first initializing it"
        print "Epic Fail"
        raise SystemExit

class Intersection(object):
    """Intersection: virtual base class for simulated and hardware intersections
    
    Intersection encapsulates the interface to the hardware/simulated hw
    """
    _light_dict_on = {"AR": 0x01, "AY": 0x02, "AG": 0x04, "BR": 0x08, "BY": 0x10, "BG": 0x20}
    _light_dict_off = {"AR": 0x3e, "AY": 0x3d, "AG": 0x3b, "BR": 0x37, "BY": 0x2f, "BG": 0x1f}
    _light_labels = ["AR", "AY", "AG", "BR", "BY", "BG"]
    _sense_labels_four = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
    _sense_labels_three = ["A1", "A2", "B1", "B2", "C1", "C2"]
    
    def _check_intersect(self, intersect_number):
        """check intersection number"""
        if intersect_number not in self._valid_intersections:
            raise InvalidIntersection
    
    def _check_light(self, light_label):
        """check light label"""
        if light_label not in self._light_labels:
            raise InvalidLightLabel
        
    def _check_sensor_label(self, intersect_number, sensor_label):
        """check sensor label"""
        if (intersect_number == 1 and sensor_label not in self._sense_labels_four) or \
                (intersect_number > 1 and sensor_label not in self._sense_labels_three):
            raise InvalidSensorLabel
            
    def set_light(self, intersect_number, light_label, value):
        """After checking the arguments' validity, set the light at intersect_number, light_label to value"""
        self._check_intersect(intersect_number)
        self._check_light(light_label)
        intersect_index = intersect_number-1
        if value:
            new_state = self._light_state[intersect_index] | self._light_dict_on[light_label]
        else:
            new_state = self._light_state[intersect_index] & self._light_dict_off[light_label]
        self._light_state[intersect_index] = new_state

    def print_lights(self):
        """print the light status-no op except for simulated hw"""
        pass
        
    def hw_close(self):
        """shut down the hardwore"""
        pass

        
class IntersectionSim(Intersection):
    """Implements the simulated hardware
    """
    
    def __init__(self):
        self._light_state = [0, 0, 0, 0, 0]
        self._valid_intersections = [1, 2, 3, 4, 5]
        random.seed()
        
        # hw_set_lights(intersect_index, new_state) # The "hardware" call would go here

    def get_sense(self, intersect_number, sensor_label):
        """After checking the arguments' validity, get the value of the sensor at intersect_number, sensor_label"""
        self._check_intersect(intersect_number)
        self._check_sensor_label(intersect_number, sensor_label)
        if sensor_value_from_user:
            in_string = "Input value for intersection %s sensor value %s (T or F): " % (intersect_number, sensor_label)
            in_value = raw_input(in_string)
            while in_value not in ("T", "F"):
                in_value = raw_input("T or F please: ")
            if in_value == "T":
                return True
            else:
                return False
        else:
            if random.randint(0, 99) < 20:
                return True
            else:
                return False
            
    def _get_light_state(self, intersect_number):
        """return the state of the lights at intersect_number"""
        result = []
        for light_label in self._light_labels:
            result.append((self._light_state[intersect_number-1] & self._light_dict_on[light_label]) > 0)
        return result

    def print_lights(self):
        """print the light status"""
        print self._ascii_light_status()

    def _ascii_light_row(self, color_letter):
        """returns a string of ascii art light status for 'R', 'Y', or 'G'"""
        row = [" "]
        for i in range(5):
            for light_label in ["A"+color_letter, "B"+color_letter]:
                if self._light_state[i] & self._light_dict_on[light_label]:
                    row.append(color_letter)
                else:
                    row.append("O")
                if i != 4 or light_label != "B"+color_letter:
                    row.append("  ")
            if i != 4:
                row.append("    ")
        return "".join(row)

    def _ascii_light_status(self):
        """returns a string of ascii art showing the light status"""
        last_rows = """AC  BD    AC  B     AC  B     AC  B     AC  B
 # 1       # 2       # 3       # 4       # 5"""

        red_row = self._ascii_light_row("R")
        yellow_row = self._ascii_light_row("Y")
        green_row = self._ascii_light_row("G")
        rows = [red_row, yellow_row, green_row, last_rows]
        result = "\n".join(rows)
        return result

class IntersectionHw(Intersection):
    """IntersectionHw implements the hw interface"""

    _sensor_mask = {"A1": 0x1, "A2": 0x2, "B1": 0x4, "B2": 0x8, "C1": 0x10, "C2": 0x20, "D1":0x40, "D2":0x80}

    def __init__(self, number_of_intersections, hw_module):
        self.hw_interface = hw_module
        if number_of_intersections == 1:
            self._light_state = [0]
            self._valid_intersections = [1]
            hw_module.hw_init_one()
        else:
            self._light_state = [0, 0, 0, 0, 0]
            self._valid_intersections = [1, 2, 3, 4, 5]
            hw_module.hw_init_five()
    
    def set_light(self, intersect_number, light_label, value):
        """After checking the arguments' validity, set the light at intersect_number, light_label to value"""
        super(IntersectionHw, self).set_light(intersect_number, light_label, value)
        self.hw_interface.hw_set_lights(intersect_number-1, self._light_state[intersect_number-1])

    def get_sense(self, intersect_number, sensor_label):
        """After checking the arguments' validity, get the value of the sensor at intersect_number, sensor_label"""
        self._check_intersect(intersect_number)
        self._check_sensor_label(intersect_number, sensor_label)
        if self.hw_interface.hw_sensors(intersect_number-1) & self._sensor_mask[sensor_label]:
            return True
        else:
            return False

    def hw_close(self):
        """shut down the hardware"""
        self.hw_interface.hw_close()
        