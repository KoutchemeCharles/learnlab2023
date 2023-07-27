#!/usr/bin/env python

import os, argparse
import pandas as pd
import numpy as np
import html2text
import openai
from utils.files import json2data


def getConcepts(problem_id, df):
    """ 
        return a list of concepts that required for solving this problem 
    """
    concept_list = ['input_str', 'input_cast', 'output', 'assignment', 'conditional',
       'function_call', 'function_def', 'function_return', 'loop_counting',
       'loop_until', 'loop_elements', 'loop_nested', 'stat_calculate',
       'file_read', 'file_write', 'list', 'list_2d', 'dictionary', 'item_set',
       'tuple']
    return [concept for concept in concept_list if (df[df['id']==problem_id][concept].iloc[0]==1)]


def generatePropmt(problem_description, skeleton_code, student_code, concepts):
    
    # prompt = "You are a helpful Teaching Assistant in a CS1 programming course teaching the basics of python programming."
    prompt = "You are given the following problem statement:"
    prompt += f"\n{problem_description}\n"
    if skeleton_code:
        prompt += f"\nWrite a solution (in Python) that solves the problem statement using the following skeleton code: \n{skeleton_code}\n"
        
    if concepts:
        prompt +=  f"Assume your python knowledge is within {str(concepts)}\n"
    prompt += "Put your code solution within the fenced code block, and do not provide explanations for your solution."

    return prompt

def extractResultCode(raw_result):
    """
    cleaning the generated code format
    """
    if raw_result[:9] == "```python":
        raw_result = raw_result.split("```python")[1]
    if raw_result[-3:] == "```":
        raw_result = raw_result.split("```")[0]
    return raw_result

def generateGPTAnswer(prompt, api_key=os.environ.get('OPEN_AI_KEY', None), model="gpt-3.5-turbo"):
    """
    input: prompt, problem_description, student_code
    output: gpt-genrated code
    """
    openai.api_key = api_key
    
    gpt_code  = ""
    
    if model in ["code-davinci-edit-001"]: # endpoint is v1/completions
        response = openai.Edit.create(
            model=model,
            input="",
            temperature=0,
            instruction=prompt
        )
        
        gpt_code = response.choices[0].text.strip()
        print(gpt_code)

    
    else: # endpoint is v1/chat/completions
        response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", 
            "content": prompt
            }
        ]
        )
        gpt_code = response["choices"][0]['message']['content']
        
    return gpt_code


def parse_args():
    parser = argparse.ArgumentParser(description='Call chatGPT-3.5 api to generate code and save into a csv file.')
    parser.add_argument('-m', '--model', help='the model used to generate the code', default='gpt-3.5-turbo')
    parser.add_argument('-i', '--input-dir', required=True, help='the directory to save result.csv file')
    parser.add_argument('-o', '--output-dir',  required=True, help='the directory to save result.csv file')
    parser.add_argument('-c', '--config', help='the configuration', default='config/v1.json')
    parser.add_argument('-v', '--validity', help='the valid ones', default='config/validity.json')
    

    return parser.parse_args()

def main():
    args = parse_args()
    print(f'ensure that {args.output_dir} directory exists...')
    os.makedirs(args.output_dir, exist_ok=True)
    print(f'successfully ensured directory existence')
    
    assert os.environ.get('OPEN_AI_KEY', None)

    problems_filename = os.path.join(args.input_dir, 'falconcode_v1_table_problems_updated.csv')
    problems_df = pd.read_csv(problems_filename)
    problems_df = problems_df.drop_duplicates(subset='id', keep='first')
    problems_df = problems_df.fillna("")
    
    config = json2data(args.config)
    problems_to_drop = json2data(args.validity)
    
    problems_df = problems_df[~problems_df['id'].isin(problems_to_drop)]
    print(len(problems_df))

    print("looping over the problems")
    
    """
    looping over all problems
    """
    problem_ids = []
    prompts = []
    codes = []
    for i in range(len(problems_df)):
    # for i in range(3):
        print(i)
        row = problems_df.iloc[i]
        problem_description = html2text.html2text(row['prompt'])
        skeleton_code = row['skeleton']
        prompt = generatePropmt(problem_description, skeleton_code, "", [])
        try: 
            code = extractResultCode(generateGPTAnswer(prompt, model=args.model))
        except openai.error.ServiceUnavailableError:
            break
        
        problem_ids.append(row['id'])
        prompts.append(prompt)
        codes.append(code)
        
    result_df = pd.DataFrame({"problem_id":problem_ids, "prompts": prompts, "code": codes})
    result_filename = os.path.join(args.output_dir, args.model+'_'+args.config.split("config/")[1].split(".json")[0]+'_result.csv')
    result_df.to_csv(result_filename)
    


if __name__ == '__main__':
    main()
