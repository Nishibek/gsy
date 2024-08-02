import numpy as np
from .fill_voronoi import fill_voronoi

class Filling():
    """
    TODO
    """
    def __init__(self, simulation_instance):
        self.simulation_instance = simulation_instance
        
    def fill_cube(self, phase_index, lower_corner, upper_corner):
        # Check Dimensionality
        lower_corner = np.array(lower_corner)
        upper_corner = np.array(upper_corner)
        boxsize = np.maximum(upper_corner - lower_corner, 1)
        
        # Check input parameters
        if phase_index > self.simulation_instance.parameters["phase_num"]:
            raise ValueError(f"Phase index is out of bounds. Maximum number of phases: {self.simulation_instance.parameters['phase_num']}.")
        
        # Generate Cube
        box_map = phase_index * np.ones(boxsize)
        self.fill_phase_index_map(lower_corner, boxsize, box_map)
        return self.simulation_instance.phase_index_map
    
    def fill_voronoi(self, phase_weights, lower_corner, upper_corner, grid_shape=None, boundary_conditions=None, random_seed=None):
        # Check Dimensionality
        boxsize = np.maximum(upper_corner - lower_corner, 1)
        
        # Set default values for grid_shape, boundary_conditions, and random_seed if not provided
        if grid_shape is None:
            grid_shape = self.simulation_instance.parameters["grid_shape"]
        if boundary_conditions is None:
            boundary_conditions = self.simulation_instance.parameters["boundary_conditions"]
        if random_seed is None:
            random_seed = self.simulation_instance.parameters["random_seed"]
        
        # Check input parameters
        if len(phase_weights) != self.simulation_instance.parameters["phase_num"]:
            raise ValueError("Need to specify a phase weight for every phase")
        
        # Generate the Voronoi diagram
        box_map = fill_voronoi(phase_weights, lower_corner, boxsize, grid_shape, boundary_conditions, random_seed)
        self.fill_phase_index_map(lower_corner, boxsize, box_map)
        return self.simulation_instance.phase_index_map
    
    def fill_phase_index_map(self, lower_corner, boxsize, box_map):
        """
        Override the part of phase_index_map corresponding to a box spanned by boxsize
        """
        # Ensure the box fits into the larger array
        if not np.all(lower_corner + boxsize <= self.simulation_instance.phase_index_map.shape):
            raise ValueError("Boxsize is too big for the specified grid")
        
        # Override corresponding part of phase_index_map with Voronoi map
        self.simulation_instance.phase_index_map[lower_corner[0]:lower_corner[0] + boxsize[0], 
                                        lower_corner[1]:lower_corner[1] + boxsize[1], 
                                        lower_corner[2]:lower_corner[2] + boxsize[2]] = box_map
        
    
    
    """
    def FillPhasesfromPhaseMap(self):
        for k, phase in enumerate(self.ListOfPhases.values()):
            phase[0, self.PhaseMap == k] = 1
        return self.ListOfPhases
        
    def init_fill_method:
    """
