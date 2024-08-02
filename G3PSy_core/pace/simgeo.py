import struct
import numpy as np
from pathlib import Path
import sys
sys.path.append('/data/nilsb/Version_2.0_G3PSy_lokal/G3PSy_core')
from phase_field_simulation import PhaseFieldSimulation

class Simgeo():
    """
    This class represents the p3simgeo file of a PACE3D simulation
    """
    # File header in hexadecimal format
    FILEHEADER = bytes.fromhex("252550414345334401000000000000000100000000000000")#ffffffffffffffff00000000000000000000000000000000") don't know what it encodes

    def __init__(self, grid_shape, grid_spacing, phase_names, component_names, si_scaling_factors=(1,1,1,1,1,1,1), filename_prefix="phi"):
        """
        Initialize a Simgeo object with the given parameters.

        Parameters:
        - grid_shape: Tuple of three integers representing the grid dimensions.
        - grid_spacing: Tuple of three floats representing the spacing in each dimension.
        - si_scaling_factors: Tuple of seven floats for scaling factors.
        - phase_names: List of phase names.
        - component_names: List of component names.
        - filename_prefix: String prefix for the filename.
        """
        self.grid_shape = grid_shape# + 2
        self.grid_spacing = grid_spacing
        self.si_scaling_factors = si_scaling_factors
        self.phase_names = phase_names
        self.phase_num = len(phase_names)
        self.component_names = component_names
        self.component_num = len(component_names)
        self.filename_prefix = filename_prefix
        
    def save(self, filepath, writemodus='f'):
        """
        Save object as p3simgeo file. 
        writemodus='f' forces override.
        """
        filepath = Path(filepath)
        if filepath.suffix.lower() != '.p3simgeo':
            filepath = filepath.with_suffix('.p3simgeo')
        self.filepath = filepath
        
        if filepath.is_file() and writemodus != 'f':
            raise FileExistsError(f"File {filepath} already exists.")
        
        with filepath.open('wb') as f:
            f.write(self.FILEHEADER)
            f.write(bytes(bytearray(24))) # In theory here Algorithmus-Feature would be encoded
            f.write(struct.pack("3i", *self.grid_shape))
            f.write(struct.pack("3f", *self.grid_spacing))
            f.write(struct.pack("7f", *self.si_scaling_factors))
            f.write(self.filename_prefix.encode('ascii') + b"\n")
            f.write(struct.pack("i", self.phase_num))
            f.write('\n'.join(self.phase_names).encode('ascii') + b'\n')
            f.write(b"component\n" + struct.pack("i", len(self.component_names)))
            f.write('\n'.join(self.component_names).encode('ascii') + b'\n')
        
    def create_simulation(self):
        """
        Create a simulation instance based on the parameters of the Simgeo object.

        Returns:
        - simulation_instance (PhaseFieldSimulation): A simulation instance with the same grid shape, phase names, and component names as the Simgeo object.

        This method creates a new simulation instance using the grid shape, phase names, and component names from the Simgeo object. It also sets the grid spacing and physical length of the simulation instance based on the grid shape and grid spacing of the Simgeo object.
        """
        simulation_instance = PhaseFieldSimulation(grid_shape=self.grid_shape, phase_class_names=self.phase_names, phase_class_num=np.ones(self.phase_num), component_names=self.component_names)
        simulation_instance.parameters["grid_spacing"] = self.grid_spacing
        simulation_instance.parameters["phys_length"] = self.grid_shape * self.grid_spacing
        simulation_instance.parameters["filename_prefix"] = self.filename_prefix
        simulation_instance.phase_names = self.phase_names
        simulation_instance.component_names = self.component_names
        return simulation_instance
    
    @classmethod
    def create_from_simulation(cls, simulation_instance):
        """
        Create a Simgeo object from a simulation instance.
        """
        grid_shape = simulation_instance.parameters["grid_shape"]
        grid_spacing = simulation_instance.parameters["grid_spacing"]
        si_scaling_factors = simulation_instance.parameters.get('si_scaling_factors', (1,1,1,1,1,1,1))
        phase_names = simulation_instance.phase_names
        component_names = simulation_instance.component_names
        filename_prefix = simulation_instance.parameters.get('filename_prefix', 'phi')
        
        # Create and return a Simgeo object with the extracted parameters
        simgeo_file = cls(grid_shape, grid_spacing, phase_names, component_names, si_scaling_factors, filename_prefix)
        return simgeo_file
    
    @classmethod
    def load_from_file(cls, filepath):
        """
        Load a Simgeo object from a p3simgeo file. Returns a Simgeo instance if successful
        """
        filepath = Path(filepath)
        if not filepath.is_file():
            raise FileNotFoundError(f"File {filepath} does not exist.")
        
        with filepath.open('rb') as f:
            data = f.read()

        if data[:24] != cls.FILEHEADER:
            raise ValueError("File is not a .p3simgeo type")

        # Unpacking data from the file
        try:
            unpacked_data = struct.unpack_from("3i 3f 7f 2i", data, offset=48)
            phase_num = unpacked_data[14]
            unpacked_fields = data[108:].decode('ascii').split('\n')
            
            # Extract start of component section
            component_start_index = data.find(b"component") + 10
            if component_start_index == -1:
                raise ValueError("Component section not found.")
            
            # Create Simgeo object
            simgeo_file = cls(
                grid_shape=np.array(unpacked_data[:3], dtype=int),
                grid_spacing=np.array(unpacked_data[3:6], dtype=float),
                si_scaling_factors=np.array(unpacked_data[6:13], dtype=float),
                phase_names=unpacked_fields[:phase_num],
                component_names=data[component_start_index + 4:-1].decode('ascii').split('\n'),
                filename_prefix=data[100:103].decode('ascii') #Todo only works for phi
            )
        except (struct.error, UnicodeDecodeError) as e:
            raise ValueError(f"Error unpacking or decoding simgeo file data: {e}")

        return simgeo_file
