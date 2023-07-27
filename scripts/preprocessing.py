""" Base preprocessing of our data """

import os
import argparse
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess the falconcode dataset')
    parser.add_argument('-i', '--input-dir', required=True, help='the directory to save result.csv file')
    parser.add_argument('-c', '--config', help='the configuration', default='config/v1.json')
    parser.add_argument('-v', '--validity', help='the valid ones', default='config/validity.json')
    
    return parser.parse_args()

def find_skeletons(merged_df):
    df = merged_df.drop_duplicates("problem_id")
    id_to_skeleton = dict()
    for problem_id, sample in df[["problem_id", "source_code"]].to_numpy():
        skeleton, limit = "", "#Your code goes here."
        if limit in sample:
            skeleton = sample[:sample.find(limit) + len(limit)]
        id_to_skeleton[problem_id] = skeleton
        
    return id_to_skeleton

def process_merged_df(df):
    df["source_code"] = df["source_code"].fillna("")
    df["concept_list"] = df["concept_list"].fillna("")
    df["problem_id"] = [pid.replace("####", "_") for pid in df["problem_id"]]
    df["concept_list"] = [pid.replace("####", "_") for pid in df["concept_list"]]
    df = df.drop(columns=["id", "Unnamed: 0"])
    return df

def process_problems_df(df, problems_df):
    id_to_skeleton = find_skeletons(df)
    problems_df["skeleton"] = [id_to_skeleton.get(pid, "")
                               for pid in problems_df["id"]]
    return problems_df 

def load_datasets(args):
    path = os.path.join(args.input_dir, "falconcode_v1_merged.csv")
    merged_df = pd.read_csv(path)
    path = os.path.join(args.input_dir, "falconcode_v1_table_problems.csv")
    problems_df = pd.read_csv(path)
    
    return merged_df, problems_df

def save_datasets(args, df, problems_df):
    save_path = os.path.join(args.input_dir, "falconcode_v1_table_problems_updated.csv")
    problems_df.to_csv(save_path)
    
def main():
    args = parse_args()
    df, problems_df = load_datasets()
    df = process_merged_df(df)
    problems_df = process_problems_df(df, problems_df)
    save_datasets(df, problems_df)
    

if __name__ == "__main__":
    main()