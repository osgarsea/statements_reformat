
import pandas as pd
import datetime
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil

from parameters import *


def print_start(txt):
      
    print('======================================')   
    print(f'{txt}\n')

def print_end():
    
    print('\n--------------------------------------')


def get_file_names():
    """
    List all the files in the input folder
    """
    print_start(f'List all files in the input folder : {INPUT_FOLDER}')
    list_of_files = [f for f in listdir(INPUT_FOLDER) if isfile(join(INPUT_FOLDER, f))]
    list_of_files = [os.path.splitext(x)[0] for x in list_of_files]
    
    if len(list_of_files)==0:
        print("There are no statements in the folder")
        sys.exit(1)

    return list_of_files


def archive_statements():
    """
    Move the input statements to an archive folder with the date and time when they are copied
    """
    print_start(f'Archive statements')

    # Create new folder named YYYYMMDD_HHMMSS
    new_directory = os.path.join(INPUT_FOLDER, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.mkdir(new_directory)
    
    # Move all files
    file_names = [f for f in listdir(INPUT_FOLDER) if isfile(join(INPUT_FOLDER, f))]
    
    for file_name in file_names:
        shutil.move(os.path.join(INPUT_FOLDER, file_name), os.path.join(new_directory, file_name))
        print(f"File {file_name} moved to folder {new_directory}")

    print_end()


def import_statement_table(account_name):
    """
    Import downloaded statements from each bank
    Each bank has it's format, format future statements here.
    The output format of these dataframes need to be pseudo-standard
    """
        
    print_start(f'Statement imported in: {account_name}')
    
    # Import statement
    print(f'\nImporting: {account_name}')
    try:
        if account_name in ['bankia', 'bankia1', 'bankia2']:
            stm = pd.read_csv(os.path.join(INPUT_FOLDER, f'{account_name}.txt'),\
                            sep='\t',\
                            skiprows=(0,1,2,3,4),\
                            header=(0),\
                            thousands='.',\
                            decimal=',')
            account_name = 'bankia'

        elif account_name in ['ing', 'ing1', 'ing2']:
            stm = pd.read_excel(os.path.join(INPUT_FOLDER, f'{account_name}.xls'),\
                            skiprows=(0,1,2,3,4),\
                            header=(0))
            account_name = 'ing'
            
        else:
            stm = pd.read_csv(os.path.join(INPUT_FOLDER, f'{account_name}.csv'), index_col = False)
        
    except Exception as e:
        print(f"Filed to import the statement. Error message was: {e}")
        sys.exit(1)
        
    print_end()
    
    return stm, account_name


def rename_columns(stm, account_name):
    """
    Rename dataframe columns in the same format
    """
    
    print_start(f'Columns renamed in: {account_name}')
    
    try:
        stm.columns = stm.columns.str.replace(" ", "")
        stm.columns = stm.columns.str.lower()
        stm.rename(columns=COLUMNS_RENAMING[account_name], inplace = True)
        
    except Exception as e:
        print(f"Filed to rename column. Error message was: {e}")
        sys.exit(1)
    
    
    print_end()
    
    return stm


def format_amount_column (stm, account_name):
    """
    Reformat the amount value so expenses are negative and incomes are positive
    Remove special characters
    New conditions need to be added for new accounts
    """
    
    print_start(f'Amount column reformatted in: {account_name}')
    
    if account_name in ['mands']:
        stm['amount'] = stm['amount'].str.replace('£', '').str.replace(',','').astype(float)
    
    elif account_name in ['amazon', 'amex']:
        stm['amount'] = stm['amount']*(-1)
    
    elif account_name in ['rbs', 'natwest']:
        stm.loc[stm['type'] == 'Purchase', ['amount']] = stm['amount']*(-1)
        
    elif account_name in ['lloyds']:
        stm['amount'] = stm['creditamount'].combine_first(stm['debitamount']*(-1))
    
    print_end()
    
    return stm
    

def format_currency_column(stm, account_name):
    """
    Add field with the currency name
    """
    
    print_start(f'Currency column created in: {account_name}')
    
    if account_name in IN_GBP:
        stm['currency'] = 'GBP'
    
    elif account_name in IN_EUR:
        stm['currency'] = 'EUR'
    
    print_end()
    
    return stm

def format_type_column (stm, account_name):
    """
    Reformat TYPE column
    """
    
    print_start(f'Type column created in: {account_name}')
    
    if 'type' in stm.columns.tolist():
         stm['type'] = stm['type'].str.lower()
    else:
        stm['type'] = ''
     
    print_end()
    
    return stm


def format_remaining_columns(stm, account_name):
    """
    Reformat all the remaining columns.
    Add new empty columns, change formats or split columns into 2
    """
    
    print_start(f'Other columns created in: {account_name}')
        
    stm = stm[['date', 'type', 'description', 'amount', 'currency']].copy()
    
    stm['date']= pd.to_datetime(stm['date'], dayfirst = True).dt.date
    stm['description'] = stm['description'].str.lower()
    stm['category'] = ''
    stm['sub_cat'] = ''
    stm['new_description'] = ''
    stm['expenses'] = stm[stm['amount'] < 0]['amount']*(-1)
    stm['income'] = stm[stm['amount'] >= 0]['amount']
    stm['account'] = account_name

    print_end()
    
    return stm

def remove_null_cols_and_rows(stm, account_name): 
    """
    When rows have nulls in any column (except expenses or income), they need to be deleted
    """   
    
    print_start(f'Select desired columns and remove null records in: {account_name}')
    
    stm2 = stm[['account', 'category', 'sub_cat', 'new_description', 'date', 'currency', 'expenses', 'income', 'description', 'type']]
    
    cols = stm2.columns.tolist() 
    cols = [c for c in cols if c not in ('expenses', 'income')] 
    stm2.dropna(inplace = True, subset = cols)
    print_end()
    
    return stm2


def drop_not_needed_records (stm):
    """
    Drop rows specified in the parameter RECORDS_TO_DROP
    """
    
    print_start('Not needed records dropped')
    
    stm_drop = pd.DataFrame()
    for key, value in RECORDS_TO_DROP.items():
        for i in value:
            stm_drop = stm_drop.append(stm[stm[key].str.contains(i)]).copy()
            stm = stm[~stm[key].str.contains(i)].copy()

    print_end()
    
    return stm, stm_drop
    

def fill_cat_and_description(stm):
    """
    Fill predifined category columns and description based on the parameter DESCRIPTION_DIC
    Some columns can be left empty
    """
    
    print_start('Categories and description filled')
    
    for col, dic2 in DESCRIPTION_DIC.items():
        for key, value in dic2.items():
            try:
                stm.loc[stm[col].str.contains(key), ['category', 'sub_cat', 'new_description']] = value[0], value[1], value[2]
            except:
                print(f'No column called {col}')
         
    print_end()
    
    return stm

    

def import_and_reformat_statements(products):
    """
    Import and reformat all stements specified in products
    """
    
    print_start('Import all statements')
    
    i = 0
    for account_name in products:
        i+=1
        stm, account_name = import_statement_table(account_name)
        stm = rename_columns(stm, account_name)
        stm = format_amount_column (stm, account_name)
        stm = format_currency_column(stm, account_name)
        stm = format_type_column (stm, account_name)
        stm = format_remaining_columns(stm, account_name)
        stm = remove_null_cols_and_rows(stm,account_name)
        
        if i == 1:
            stm_all = stm.copy()
        else:
            stm_all = stm_all.append(stm, ignore_index = True)
        
        
    print_end()
    
    return stm_all


def add_pensions_contributions(stm):
    """
    Automatically add pension contributions as income based on the attributes in PENSIONS
    Add 2 new records, 1 with the personal contribution based on the % specified in PENSIONS
    And a second one with the company contribution based on the % specified in PENSIONS
    """
    
    print_start('Add pension contributions')
    
    pensions_df_list = []
    for key, value in PENSIONS.items():
        for i in value[1]:

            pensions_df = stm[(stm['category']=='Nóminas')&(stm['sub_cat']==key)].copy()
         
            pensions_df['income']=value[0]*i[1]/12
            pensions_df['expenses']=np.nan
            pensions_df['category']='Nóminas'
            pensions_df['sub_cat']=f'Pensión {key}'
            pensions_df['new_description']=i[0]
           
            pensions_df_list.append(pensions_df)
        
    pensions_df_all = pd.concat(pensions_df_list)
    
    stm_all = pd.concat([stm, pensions_df_all])
    
    print_end()
    
    return stm_all
        

def add_salary_deductions(stm):
    """
    Add salary deductions to the salary income and deduct them as expenses
    So they are reflected in the statements
    Get data from SALARY_DEDUCTIONS
    """
     
    deductions_list = []
    
    for key, value in SALARY_DEDUCTIONS.items():
        
        from_dt = datetime.datetime.strptime(SALARY_DEDUCTIONS['Óscar'][0], '%Y-%m-%d').date()
        condition = (stm['category']=='Nóminas')&(stm['sub_cat']==key)&(stm['date']>=from_dt)
        
        deductions = stm[condition].copy()
        
        stm.loc[condition, ['income']] = stm.loc[condition, ['income']]+value[1][3]
        
        
        deductions['category']=value[1][0]
        deductions['sub_cat']=value[1][1]
        deductions['new_description']=value[1][2]
        deductions['expenses']=value[1][3]
        deductions['income']=np.nan
       
        deductions_list.append(deductions)
        
    deductions_all = pd.concat(deductions_list)
    
    stm_all = pd.concat([stm, deductions_all])
        
    print_end()
    
    return stm_all


def export_csv (df_all, to_drop = ''):
    """
    Export all data as CSV in the final format
    """
        
    
    df_all = df_all.replace('', np.NaN)
    df_all['description'] = df_all.new_description.combine_first(df_all.description)  
    
    df_all = df_all[['account', 'category', 'sub_cat', 'description', 'date', 'currency', 'expenses', 'income']].copy()
    
    
    if to_drop == '':
        df_all.sort_values(['date', 'category', 'sub_cat', 'description'], axis = 0, inplace = True)
    else:
        df_all.sort_values(by = ['description', 'date'], axis = 0, inplace = True)
        

    
    df_all.to_csv(os.path.join(OUTPUT_FOLDER, 'all_statements_{ts}{to_drop}.csv')\
                  .format(to_drop = to_drop,
                          ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')),
                  encoding = 'utf-8-sig',
                  index = False,
                  header = True)
        
    return df_all
        

def export_statements (stm_all, stm_drop_all):
    """
    Export all dataframes as CSV
    Export both, the reformatted statement and also the one with the deleted rows to manually inspect it
    """
    
    print_start('Statements exported')
    
    stm_all = export_csv (stm_all)
    stm_drop_all= export_csv (stm_drop_all, '_drop')
        
    print_end()
    
    return stm_all, stm_drop_all


def import_and_export_statements():
    """
    Run all the staps to import, reformat and export all the statements
    Return the statements as dataframe in case it needs to be used in Python
    """
    list_of_files = get_file_names()
    stm = import_and_reformat_statements(list_of_files)
    stm_all, stm_drop_all = drop_not_needed_records (stm)
    stm_all = fill_cat_and_description(stm_all)
    stm_all = add_pensions_contributions(stm_all)
    stm_all = add_salary_deductions(stm_all)
    stm_all, stm_drop_all = export_statements (stm_all, stm_drop_all)
    archive_statements()
    
    return stm_all, stm_drop_all
    
    