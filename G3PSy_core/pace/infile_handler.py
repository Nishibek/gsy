import re
import numpy as np

class InfileHandler:    
    def __init__(self):
        self.constants = {}
        self.DefineFunction = {}
        self.PACE_MetaData = {}
        self.header = "#Created with G3PSy in python\n############################"
        self.text = ""
        
        self.ConcentrationTypeMap = {0: 'disabled',
                          1: 'constant',
                          2: 'extern',
                          3: 'standard',
                          4: 'advective'}
        self.EnergyTypeMap = {0: "disabled",
                                1: "constant",
                                2: "extern",
                                3: "standard",
                                4: "advective",
                                5: "temperature_advective",
                                6: "temperature_no_detour",
                                7: "temperature_only",
                                8: "brake"}
        self.EnergyKSpatialTypeMap = {0: 'arithmetic',
                                      1: 'harmonic'}
        
        self.PhasefieldTypeMap = {1: "constant",
                                    3: "standard",
                                    4: "advective"}
        
        self.Pace_to_G3PSy = {'Settings.Domain.NumX': 'NumX', 
                          'Settings.Domain.NumY': 'NumY', 
                          'Settings.Domain.NumZ': 'NumZ', 
                          'Phasefield.Classes.Names': 'PhaseClassesNames',
                          'Phasefield.Classes.Sizes': 'PhaseClassesNum',
                          'Phasefield.N': 'PhaseNum',
                          'Settings.NumberOfTimesteps': 'NumTimesteps',
                          'Settings.Time.delta_t': 'delta_t',
                          'Settings.RandomGenerator.Type': 'RandomGeneratorType',
                          'Settings.RandomGenerator.manualSeed': 'RandomSeed',
                          'Settings.Time.Skip': 'TimeStepWidths',
                          'Settings.Domain.delta_x': 'delta_x',
                          'Settings.Domain.delta_y': 'delta_y',
                          'Settings.Domain.delta_z': 'delta_z'}
        self.G3PSy_to_Pace = {v: k for k, v in self.Pace_to_G3PSy.items()}
        super().__init__()
        
    def ReadInfile(self, Read_file_path):
        with open(Read_file_path, 'r') as file:
            text = file.read()
            self.header = text[:text.find("##       main list        ##")].strip()
            
            for line in text[text.find("## Evaluate functions")+52:].splitlines():
                line = line.strip()
                if line == '':
                    break
                if ':' in line:
                    self.DefineFunction[line.split(':')[0]] = line.split(':')[1]
                else:
                    line = line.split('=')[1]
                    self.constants[line.split(',')[0]] = line.split(',')[1]
                
            for line in text[text.find("##       main list        ##")+59:].splitlines():
                line = line.strip()
                if line == '':
                    break
                self.PACE_MetaData[line.split('=')[0]] = line.split('=')[1]
        
        """self.file_path = Read_file_path
        with open(self.file_path, 'r') as file:
            self.text = file.read()
            
        header_end_index = self.text.find("##       main list        ##")
        self.header = self.text[:header_end_index].strip()
        
        for line in self.text[self.text.find("## Evaluate functions"):].splitlines():
            if '=' in line:
                if not ':' in line:
                    self.constants[line[line.find('=')+1:line.find(',')].strip()] = line[line.find(',')+1:].strip()
                else:
                    self.DefineFunction[line[:line.find(':')].strip()] = line[line.find(':')+1:].strip()"""
        
        for i in range(10):
            self.constants = self.ConvertStrInfile(self.constants)
        
        """PACE_MetaData = {}
        for line in self.text[header_end_index:self.text.find("## Evaluate functions")].splitlines():
            eq_index = line.find('=')
            if eq_index != -1:
                PACE_MetaData[line[:eq_index].strip()] = line[eq_index+1:].strip()
        print(PACE_MetaData)"""
        
        """#get some default values
        if not 'PhysicalProperty.IdealGasConstant' in self.PACE_MetaData:
            self.PACE_MetaData['PhysicalProperty.IdealGasConstant'] = 8.3144621"""
            
        #Achtung unbedingt überprüfen, nur zu testzwecken implementiert!!!
        #self.PACE_MetaData['FunctionF'] = 'constant'
        #self.PACE_MetaData['La.Type'] = 'MATRIX_CONST'
        #self.PACE_MetaData['La.Const'] = 0
        #self.PACE_MetaData['FunctionW'] = 'obstacle'
        
        
        self.meta_data = {self.Pace_to_G3PSy.get(key, key): value for key, value in self.PACE_MetaData.items()}
        for key, value in self.meta_data.items():
            if key in {'Concentration.Boundary', 'Energy.Boundary', 'Phasefield.Boundary', 'Phasefield.Classes.Names'}:
                value = value.strip('()').split(',')
            self.meta_data = self.ConvertStrInfile(self.meta_data)
        #self.transform_Paul_infile_to_Stand_beta()
            
                
    def ConvertStrInfile(self, unresolved):
        for key, value in unresolved.items():
            #value = str(value)
            if isinstance(value, str):
                for const_key, const_value in self.constants.items():
                    value = re.sub(r'\b{}\b'.format(re.escape(const_key)), str(const_value), value)
                    unresolved[key] = value
                try:
                    unresolved[key] = eval(value)
                except:
                    pass#unresolved[key] = value  # Belasse den Wert als String
        return unresolved
                
    def WriteInfile_saved(self, save_path):
        self.text = self.header
        self.text += "\n##       main list        ##\n"
        self.text += "############################\n\n"
        PACE_MetaData = {}
        PACE_MetaData = {self.G3PSy_to_Pace.get(key, key): value for key, value in self.meta_data.items()}
        #Transform some values so Pace can read them:
        PACE_MetaData['Settings.RandomGenerator.manualSeed'] = hex(PACE_MetaData['Settings.RandomGenerator.manualSeed'])
        #if 'Settings.writeTimesteps.Const' in PACE_MetaData:
            #PACE_MetaData['Settings.writeTimesteps.Type'] = 'constant'
        
        for key, value in PACE_MetaData.items():
            self.text += f"{key}={value}\n"
        
        #make filling for test purpose:
        self.text += "\n############################\n"
        self.text += "## Fillings\n"
        self.text += "############################\n\n"
        self.text += f"FillCube=({self.Phasefields[0]}),[(0,0,0),{self.meta_data['NumZ'], self.meta_data['NumX'], self.meta_data['NumY']}]\n"
        
        self.text += "\n############################\n"
        self.text += "## Evaluate functions\n"
        self.text += "############################\n\n"
        for key, value in self.constants.items():
            self.text += f"DefineConst={key},{value}\n"
        for key, value in self.DefineFunction.items():
            self.text += f"{key}:{value}\n"
                
        with open(save_path, 'w') as file:
            file.write(self.text)
            
    def transform_Paul_infile_to_Stand_beta(self):
        for key, value in self.meta_data.items():
            if key in {'Concentration.Type'}:
                self.meta_data[key] = self.ConcentrationTypeMap.get(value, 'unknown')
            if key in {'Energy.Type'}:
                self.meta_data[key] = self.EnergyTypeMap.get(value, 'unknown')
            if key in {'FunctionH'}:
                self.meta_data[key] = 'h' + str(value)
            if self.meta_data['Phasefield.tau.Type'] == 0:
                self.meta_data['Phasefield.tau.Type'] = 'isotropic'
            if key in {'Energy.k.SpatialInterpolation.Type'}:
                self.meta_data[key] = self.EnergyKSpatialTypeMap.get(value, 'unknown')
            if key in {'Phasefield.Type'}:
                self.meta_data[key] = self.PhasefieldTypeMap.get(value, 'unknown')
            """,
                          'PhysicalProperty.IdealGasConstant': 'R',
                          'PhysicalProperty.MolarVolume': 'V'"""
