#!/usr/bin/env python

import os, argparse
import pandas as pd
import numpy as np
import html2text
import openai


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


def generatePropmt(problem_description, student_code, concepts):
    prompt = "You are a helpful Teaching Assistant in a CS1 programming course teaching the basics of python programming. Please provide a solution to this problem description:" 
    if student_code == "":
        prompt += f"{prompt} \nProblem description:\n{problem_description}\n"
    if concepts:
        prompt +=  f"Assume your python knowledge is within {str(concepts)}\n"
    prompt += "The answer should be code only, please do not provide explanations. Please put the answer within the fenced code block. "
#     else: 
#         prompt = f"{prompt} \nProblem description:\n{problem_description}\n Assume your python knowledge is within {str(concepts)}"

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

def generateGPTAnswer(prompt, api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo"):
    """
    input: prompt, problem_description, student_code
    output: gpt-genrated code
    """
    # openai.api_key = api_key
    openai.api_key = "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"
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

    
    if model in ["gpt-3.5-turbo"]: # endpoint is v1/chat/completions
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


def main():
    parser = argparse.ArgumentParser(description='Call chatGPT-3.5 api to generate code and save into a csv file.')
    parser.add_argument('-m', '--model', help='the model used to generate the code', default='gpt-3.5-turbo')
    parser.add_argument('-i', '--input-dir', required=True, help='the directory to save result.csv file')
    parser.add_argument('-o', '--output-dir', required=True, help='the directory to save result.csv file')
    parser.add_argument('-c', '--config', required=True, help='the configuration', default='config/v1.json')
    args = parser.parse_args()

    print(f'ensure that {args.output_dir} directory exists...')
    os.makedirs(args.output_dir, exist_ok=True)
    print(f'successfully ensured directory existence')
    
    problems_filename = os.path.join(args.input_dir, 'falconcode_v1_table_problems.csv')
    problems_df = pd.read_csv(problems_filename)
    
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
        prompt = generatePropmt(problem_description, "", concepts=[])
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
