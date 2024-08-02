import numpy as np
from .simgeo import Simgeo
from .scalar_data import ScalarData
import os

class Pace():
    """
    TODO#simulation_instance.parameters["grid_shape"]
    """
    def __init__(self, simulation_instance):
        self.simulation_instance = simulation_instance
    
    def init_dir(self, folder_path):
        self.folder_path = folder_path
        # Create Folder if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        self.base_path = folder_path + "/" + os.path.basename(folder_path)
        
        
    def save_scalar_data(self, folder_path):
        self.init_dir(folder_path)
        
        # Create p3simgeo file
        simgeo_file = Simgeo.create_from_simulation(self.simulation_instance)
        simgeo_file.save(self.base_path + ".p3simgeo")
        
        # Create a p3s data file for each phase in stored_phase_data dictonary
        self.simulation_instance.parameters['filename_prefix'] = simgeo_file.filename_prefix
        ScalarData.store_phases(self.simulation_instance, self.base_path)
