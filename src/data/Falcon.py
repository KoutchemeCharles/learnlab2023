import os 
import re 
import pandas as pd
from copy import deepcopy 
from src.data.Dataset import Dataset
from src.utils.TableConverter import TableConverter

class Falcon(Dataset):

    def __init__(self, dir_path) -> None:
        self.dir_path = dir_path
        self._dataset = self._load_dataset()

    def _load_dataset(self):
        df = pd.read_csv(os.path.join(self.config.path))
        print("Original number of problems", len(df))
        # Remove duplicate ids for project (same content, multiple semesters)
        df = df.drop_duplicates("id")
        print("Number of problems after dropping duplicates", len(df))
        # Some columns have nan values
        df = df.fillna("")
        # Format the prompt for readability
        df["prompt"] = df["prompt"].apply(html_to_md)
        # We do not have access to the external ressources (all the projects full description)
        # for assignments of type project, and they will be graded manually by instructors anyway 
        df = df[df.type != "project"]
        s = "You have been provided with"
        mask = [s not in prompt for prompt in df["prompt"]]
        df = df[mask]
        print("Number of problems after droping unavailable ones", len(df))
        df = df.sort_values(by="id")
        df = df.reset_index(drop=True)

        return df

    @property
    def load_dataset(self):
        return deepcopy(self._dataset)
    
# Create shorthand method for conversion
def html_to_md(html, **options):
    mkdwn = TableConverter(**options).convert(html)
    return re.sub(r'\n\s*\n', '\n', mkdwn).strip()