import os 
import pandas as pd

from src.data.Falcon import Falcon 

class Experiment():

    def __init__(self, config) -> None:
        self.config = config 

    def run(self):
        dataset = self.load_dataset()
    
    def load_dataset(self):
        dataset_name = self.config.dataset.name
        # args.input_dir, 'falconcode_v1_table_problems_updated.csv'
        if dataset_name == "falcon":
            dataset = Falcon().dataset
        else:
            raise ValueError(f"Unkwown dataset {dataset_name}")
        return dataset
        # Load here the FalconCode dataset for instance 