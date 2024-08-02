from pypace import core as pace
import numpy as np
import os
from pathlib import Path
import struct

class ScalarData():
    FILEHEADER1 = bytes.fromhex("252550414345334401000000000000000400000000000000000000000000000100000000000000000000000000000000")
    FILEHEADER2 = bytes.fromhex("000000000000803f000000000000000000000000000000000000000000000000")
    
    def __init__(self, data, offset=(0,0,0), grid_shape=None):
        self.data = data
        self.offset = offset
        if grid_shape is None:
            self.grid_shape = data.shape 
    
    def save(self, filepath, writemodus='f'):
        """
        Save object as p3s data file. 
        writemodus='f' forces override.
        """
        filepath = Path(filepath)
        if filepath.suffix.lower() != '.p3s':
            filepath = filepath.with_suffix('.p3s')
        self.filepath = filepath
        
        if filepath.is_file() and writemodus != 'f':
            raise FileExistsError(f"File {filepath} already exists.")
        
        #Use pypace, properly should look into it and write it myself
        file_path = str(filepath.with_suffix('')) + ".p3simgeo"
        filepath = str(filepath)
        out_frame = pace.ScalarData(self.data.astype(np.float32), file = "test.p3s", offset=self.offset, domain_size=self.grid_shape) #file = filepath
        writer = pace.PaceWriter(file_path, write_mode="f")
        writer.add_field(out_frame)
        writer.write()
        os.remove(file_path)

    def write_frame(self, file_path, frame_data, frame_type=0, simulation_time=0):
        # Compute the size of the frame data in bytes
        frame_byte_size = 4 * np.prod(frame_data.shape)
        
        # Create the frame header and footer
        frame_header = struct.pack("=Q q f 12x", frame_byte_size + 64, frame_type, simulation_time)
        frame_footer = struct.pack("=4f 8x Q", 0, 1, np.min(frame_data), np.max(frame_data), frame_byte_size + 64)
        
        # Write header, data, and footer to file
        with open(file_path, 'wb') as file:
            file.write(frame_header)
            frame_data.tofile(file)
            file.write(frame_footer)
            
    def save_test(self, file_path, writemodus='f'):
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
            file.write(FILEHEADER1)
            file.write(FILEHEADER2)
            self.write_frame(file_path, self.data)
        
        

