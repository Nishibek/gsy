import numpy as np
from filling import Filling

class CoreSimulation:
    """
    Core class to create a simulation instance
    grid_shape convention is right hand system, i.e. Z,Y,X direction in this order
    """
    def __init__(self, grid_shape, phase_class_names, phase_class_num, component_names=["component"]):
        if len(phase_class_names) != len(phase_class_num):
            raise ValueError("The number of phase class names must match the number of phase class counts. Please ensure both lists have the same length.")
        
        self.parameters = {
            "grid_shape": np.array([grid_shape[0], grid_shape[1], grid_shape[2]], dtype='int'),
            "phase_class_names": phase_class_names,
            "phase_class_num": np.array(phase_class_num, dtype='int'),
            "phase_num": np.sum(phase_class_num)
        }
        #self.simulation_settings = {}
        
        self.phase_index_map = np.zeros(self.parameters['grid_shape'], dtype=np.float32)
        self.phase_names = np.array([f"{name}_{i}" for name, num in zip(self.parameters["phase_class_names"], self.parameters["phase_class_num"]) for i in range(num)], dtype='str')
        self.component_names = np.array(component_names, dtype='str')#[f"{name}_{i}" for name, num in zip(phase_class_names, phase_class_num) for i in range(num)], dtype='str')
        self.stored_phase_data = {}
        

class PhaseFieldSimulation(CoreSimulation):
    """
    class for managing phase field simulations, takes grid_shape, phase class names & numbers
    """
    def __init__(self, grid_shape, phase_class_names, phase_class_num, component_names=["component"], phys_length=None, boundary_conditions=('isolate', 'isolate', 'isolate', 'isolate', 'isolate', 'isolate'), random_seed=None):
        super().__init__(grid_shape, phase_class_names, phase_class_num, component_names)
        if phys_length is None:
            phys_length = self.parameters["grid_shape"]
            
        self.parameters["phys_length"] = phys_length
        self.parameters["grid_spacing"] = phys_length/grid_shape
        self.parameters["boundary_conditions"] = boundary_conditions
        self.parameters["random_seed"] = random_seed
        
        self.filling = Filling(self)
