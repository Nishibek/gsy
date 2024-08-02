from .infile_handler import InfileHandler
from pypace import core as pace
import numpy as np
import os
import subprocess
import sys

class PaceHandler(InfileHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # Weitere Methoden und Attribute von PaceHandler
    
    def Pace_findFiles(self, folder_path):
        folder_name = os.path.basename(folder_path)
        self.basefile_path = os.path.join(folder_path, f'{folder_name}')
        infile_path = os.path.join(folder_path, f'{folder_name}.infile_saved')
        simgeo_path = os.path.join(folder_path, f'{folder_name}.p3simgeo')
    
    def Pace_LoadSimgeo(self, folder_path):
        self.ListOfPhases = {}
        self.Pace_findFiles(folder_path)
        self.ReadInfile(self.basefile_path + '.infile_saved')
        self.Phasefields = np.array([f"{name}{i}" for name, num in zip(self.meta_data['PhaseClassesNames'], self.meta_data['PhaseClassesNum']) for i in range(num)], dtype='str')
        ps = pace.PaceSimulation(self.basefile_path + '.p3simgeo')
        
        self.Phasefields = np.array(['phiindex'])
        for phase in self.Phasefields:
            ps.add_field("phi_" + phase,"p3s")            
            
            ts = pace.TimeSeries(ps,[0])
            self.meta_data['NumTimesteps'] = ts._frame_count
            for frame in ts:
                self.meta_data['NumZ'], self.meta_data['NumX'], self.meta_data['NumY'] = frame["phi_" + phase].shape
            self.ListOfPhases[phase] = np.empty((self.meta_data['NumTimesteps'], self.meta_data['NumZ'], self.meta_data['NumX'], self.meta_data['NumY']), dtype=float)
            
            ts = pace.TimeSeries(ps,range(self.meta_data['NumTimesteps']))
            for frame_number, frame in enumerate(ts):
                self.ListOfPhases[phase][frame_number] = frame["phi_" + phase]
        
        return self.ListOfPhases
    
    def Pace_WriteSimgeo(self, folder_path):
        base_path = folder_path + "/" + os.path.basename(folder_path)
        writer = pace.PaceWriter(base_path + ".p3simgeo", write_mode="f")
        for field in {self.Phasefields[0]}:
            for frame_number in range(len(self.ListOfPhases[field][:,0,0,0])):
                print(self.ListOfPhases[field].shape)
                frame = pace.ScalarData(self.ListOfPhases[field][frame_number].astype(np.float32), file = 'base_path' + '.phiindex.p3s', offset = (0,0,0), domain_size = self.ListOfPhases[field][frame_number].shape)
                writer.add_field(frame)
                writer.write()
                
    def Pace_Create_Phiindex_Simulation(self, folder_path):
        file_path = folder_path + "/" + os.path.basename(folder_path) + ".phiindex" + ".p3simgeo"
        writer = pace.PaceWriter(file_path)
        out_frame = pace.ScalarData(self.PhaseMap.astype(np.float32), file = file_path, offset = (0,0,0), domain_size = self.PhaseMap.shape())
        writer.add_field(out_frame)
        writer.write()
        os.remove(file_path)
        simgeo_file = SimgeoHandler.Create_Simgeo_from_Metadata(self.meta_data)
        simgeo_file.Write_Simgeo(file_path)


    def Pace_CreateSimgeo(self, folder_path, PaceVersion = "pace3D-nightly"):
        """#Erzeuge Ordner:
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Ordner '{folder_path}' wurde erstellt.")
            else:
                print(f"Ordner '{folder_path}' existiert bereits.")
        except Exception as e:
            print(f"Fehler beim Erstellen des Ordners '{folder_path}': {e}")
            
        self.meta_data['NumTimesteps'] = 1
        #können in python nicht mpi rechnen
        self.meta_data['Settings.MPI.DomainDecomposition.Partitions'] = (1,1,1)
        # Liste an Zeug das Pace braucht:
        self.meta_data.setdefault('RandomGeneratorType', 0)
        self.meta_data.setdefault('RandomSeed', 0)
        self.meta_data.setdefault('delta_t', 0.1)
        self.meta_data.setdefault('TimeStepWidths', (1,1,1))
        self.meta_data.setdefault('delta_x', 1)
        self.meta_data.setdefault('delta_y', 1)
        self.meta_data.setdefault('delta_z', 1)
        
        self.WriteInfile_saved(folder_path + '/From_G3PSy.infile_saved')
        
        #Creating Pace Files with Pace nightly
        try:
            # Ausführen des Befehls und Einfangen der Ausgabe
            PaceVersion = "/data/groups/public/paul/Nils/dewetting/software/pacexd/vectorized_mpipace3D.20240419"
            result = subprocess.run([PaceVersion, "-I", folder_path + '/From_G3PSy.infile_saved', "-P", folder_path + "/tutorial-003", "-f"], capture_output=True, text=True, check=True)
            #print(result.stdout)
        except subprocess.CalledProcessError as e:
            # Bei einem Fehler die Fehlermeldung ausgeben und das Programm beenden
            print("Error:")
            print(e.stderr)
            sys.exit(1)"""
        
        self.Pace_WriteSimgeo(folder_path + "/tutorial-003")
    

