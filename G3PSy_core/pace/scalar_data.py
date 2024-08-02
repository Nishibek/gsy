import numpy as np
import os
from pathlib import Path
import struct

class ScalarData():
    FILEHEADER1 = bytes.fromhex("252550414345334401000000000000000400000000000000000000000000000100000000000000000000000000000000")
    FILEHEADER2 = bytes.fromhex("000000000000803f000000000000000000000000000000000000000000000000")
    
    def __init__(self, data, frame_type=0, simulation_time=0):
        self.data = data
        self.frame_type = frame_type
        self.simulation_time = simulation_time 

    def append_frame(self, file_path, frame_data, frame_type=0, simulation_time=0):
        # Compute the size of the frame data in bytes
        frame_byte_size = 4 * np.prod(frame_data.shape)
        
        # Create the frame header and footer
        frame_header = struct.pack("=Q q f 12x", frame_byte_size + 64, frame_type, simulation_time)
        frame_footer = struct.pack("=4f 8x Q", np.min(frame_data), np.max(frame_data), np.min(frame_data), np.max(frame_data), frame_byte_size + 64)
        
        # Write header, data, and footer to file
        with open(file_path, 'ab') as file:
            file.write(frame_header)
            file.write(frame_data.tobytes('F'))
            file.write(frame_footer)
            
    def save(self, file_path, writemodus='f'):
        """
        Save object as p3s data file. 
        writemodus='f' forces override.
        """
        file_path = Path(file_path)
        if file_path.suffix.lower() != '.p3s':
            file_path = file_path.with_suffix('.p3s')
        self.file_path = file_path
        
        if file_path.is_file() and writemodus != 'f':
            raise FileExistsError(f"File {file_path} already exists.")
        
        #
        with open(file_path, 'wb') as file:
            file.write(self.FILEHEADER1)
            file.write(self.FILEHEADER2)
        self.append_frame(file_path, self.data, self.frame_type, self.simulation_time)
        
    @classmethod
    def store_phases(cls, simulation_instance, base_path):
        # Create a p3s data file for each phase in stored_phase_data dictonary
        for phase_name, phase_data in simulation_instance.stored_phase_data.items():
            scalar_data_file = ScalarData(phase_data)#fehlt
            scalar_data_file.save(base_path + "." + simulation_instance.parameters['filename_prefix'] + "_" + phase_name + ".p3s")
        
        #Only necessary because stupid pypace
        if phase_name == "phiindex":
            os.rename(base_path + "." + simulation_instance.parameters['filename_prefix'] + "_" + phase_name + ".p3s", base_path + ".phiindex.p3s")
            
    @classmethod
    def load_phases(cls, base_path, simulation_instance):
        # Get the list of files in the directory
        file_list = os.listdir(base_path)
        
        # Check if the directory is empty
        if not file_list:
            raise FileNotFoundError(f"No files found in directory: {base_path}")
    
        # Iterate through the files and load phase data
        for file_name in file_list:
            if file_name.endswith(".p3s"):
                phase_name = file_name.split(".")[-2]
                if '_' in phase_name:
                    phase_name = phase_name.split("_", 1)[1]
                file_path = os.path.join(base_path, file_name)
                
                file_size = os.path.getsize(file_path)
                frame_size = 4 * np.prod(simulation_instance.parameters["grid_shape"]) + 64
                num_frames = (file_size - 80) // frame_size
                # Load the phase data from the p3s file
                with open(file_path, 'rb') as file:
                    file.read(48)  # Skip the file header
                    file.read(32)  # Skip the file header
                    
                    simulation_instance.stored_phase_data[phase_name] = np.empty((num_frames, *simulation_instance.parameters["grid_shape"]), dtype=np.float32)
                    for frame_num in range(num_frames):
                        # Read the frame header
                        frame_size, frame_type, simulation_time = struct.unpack("=Q q f 12x", file.read(32))
                        
                        # Read the frame data and store it in the simulation instance
                        simulation_instance.stored_phase_data[phase_name][frame_num] = np.frombuffer(file.read(frame_size - 64), dtype=np.float32).reshape(simulation_instance.parameters["grid_shape"])
                        
                        # Read the frame footer
                        _ = struct.unpack("=4f 8x Q", file.read(32))
        print(simulation_instance.stored_phase_data["phiindex"].shape)
        