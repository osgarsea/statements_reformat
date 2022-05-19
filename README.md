
# Statements reformating


## Overview
Program to reformat, combine and export all the bank statements.
</br>
The structure of the table is the one used in my personal Excel spreadhseet.
</br>
The full information about the categories, sub-categories and description can be found in the Excel spredsheet (non included in this repo)
</br></br>
First you need to manually download the statements from your bank, these are some of the links

- [ING](https://ing.ingdirect.es/pfm/#movement-query-search/)
- [Bankia](https://www.bankia.es/oficina/particulares/#/cuentas/movimientos)
- [RBS](https://www.digitalbanking.rbs.co.uk/)
- [Amazon](https://portal.newdaycards.com/amazon/login)
- [NatWest](https://www.nwolb.com/default.aspx)


## Configuration
The parameters needed to reformat the statements and infill automatically the columns can be found in the file `parameters.py`.
</br>

__Parameters__
   - `IN_GBP`: List with the name of the accounts in Pounds. They need to match the name of the file.
   - `IN_EUR`: List with the name of the accounts in Euros. They need to match the name of the file.
   - `PENSIONS`: Dictionary with the pension details
     - < Name > (Subcategory name under category `Nóminas`)
       - Annual gross salary
       - Company contributions and % of gross salary
       - Personal contributions and % of gross salary 
  - `SALARY_DEDUCTIONS`: Dictionary with all the salary deductions applied in the payslip (i.e. PHI, transport loan...)
      - < Name > (Subcategory name under category `Nóminas`)
        - Date from which the deduction applies
        - List with the statement row
          - < Category >
          - < Sub-category >
          - < Description >
          - < Amount >
  - `INPUT_FOLDER`: name of the folder where the input statements are stored
  - `OUTPUT_FOLDER`: name of the folder where the formatted output statements are stored
  - `COLUMNS_RENAIMING`: Dictionary with the mpping of original to final column names per statement
    - < File name >
      - < Original column name > 
        - < Final column name >
  - `RECORDS_TO_DROP`: Dictionary with the list of strings used to remove non-wanted records. One list per each column.
    - < Column name >
      - < List of strings >
  - `DESCRIPTION_DIC`: Dictionary with the attribtes to use in the wanted records. One list per each column. The match is done using the dictionary key that contains the wanted string.
    - < Column name >
      - < String to match >
        - < Category >
        - < Sub-category >
        - < New description >

&#x26a0;&#xfe0f; If new statements are imported, the parameters `IN_GBP`, `IN_EUR`, `COLUMNS_RENAIMING` and `RECORDS_TO_DROP` need to be updated.
</br>
&#x26a0;&#xfe0f; If new records want to be classified automatically, new entries nned to be added to `DESCRIPTION_DIC`

## Maintenance and update of the functions and parameters
### Actions when a statement in a new format or from another bank is added
When a statement with a new format or from a new bank is added, the functions that reformat the input statements need to be modify to account for this new style
- Modify the following functions in the file `import_statements_lib.py` if needed
   - `import_statement_table`
   - `format_amount_column`
- Add values in the parameters file `parameters.py`
   - `IN_GBP`
   - `IN_EUR`
   - `COLUMNS_RENAMING`
### Actions to accomodate new categories or change Pensions or Deductions
- When contributions to pensions or salaries change, the values in `PENSIONS` (inside `parameters.py` need to be updated.
- When new salary deductions are added or updated, the parameter `SALARY_DEDUCTIONS` needs to be updated
- If we want to add new records to automatically classify entries from the statements, they need to be added in `DESCRIPTION_DIC`


## Ouputs
Two files are created, one with the desired records in the desired format, whihc is the statement that needs to be used in Excel.
</br>
A second statement with the discarded records, this file needs to be visualy inspected to detect possible uncorrectedly discarded records.

The input statements will be moved to a new folder with the name in the format **YYYYMMDD_HHMMSS** so they are kept for future reference if needed.
They can be manually deleted at any point.


## To execute it
1. Download the files from the bank accounts and copy them in `input` with the correct names
1. Run the file `import_statements.py`
1. The output statements are copied into `output`
1. Have an overview to make sure there are no needed records in the `_drop` file
1. Use them in the Excel spreadsheet (not included in this repo)
