#!/usr/bin/env python

import click
import pandas as pd
import re

# Hard-coded variables
investigation_type = 'metagenome'

# Function: return dataframe of environmental package-specific metadata items
# A single environmental package (soil) or list can be provided (soil,water).
def show_items_of_env_pkg(df_env_pkg, list_of_env_pkg):
    """Return dataframe of environmental package-specific metadata items"""
    df_items = df_env_pkg[df_env_pkg['Environmental package'].isin(list_of_env_pkg)]
    return df_items

# Function: return dataframe of metadata template
def create_template_for_env_pkg(df_QiitaEBI, df_MIMS, df_env_pkg, list_of_env_pkg, number_of_samples, sample_prefix):
    """Return dataframe of metadata template"""
    
    # get headers/requirement/example of Qiita-EBI/MIMS/env_pkg columns
    pkg_items = show_items_of_env_pkg(df_env_pkg, list_of_env_pkg)
    headers_env_pkg = pkg_items['Structured comment name'].values
    require_env_pkg = pkg_items['Requirement']
    example_env_pkg = pkg_items['Value syntax']
    headers_all = list(df_QiitaEBI.iloc[0]) + list(df_MIMS.iloc[0]) + list(headers_env_pkg)
    require_all = pd.concat([df_QiitaEBI.iloc[1], df_MIMS.iloc[1], require_env_pkg])
    example_all = pd.concat([df_QiitaEBI.iloc[2], df_MIMS.iloc[2], example_env_pkg])
    
    # populate template dataframe
    df_template = pd.DataFrame(columns=headers_all, dtype=object)
    df_template.loc['Requirement'] = require_all.values
    df_template.loc['Format'] = example_all.values
    string_of_env_pkg = re.sub(r'\W', '.', '.'.join(list_of_env_pkg))
    for i in range(0, number_of_samples):
        df_template.loc[i+1] = ['' for x in range(len(df_template.columns))]
        df_template.loc[i+1]['sample_name'] = '%s.%s.%s' % (sample_prefix, string_of_env_pkg, i+1)
        df_template.loc[i+1]['investigation_type'] = investigation_type
        df_template.loc[i+1]['env_package'] = ' or '.join(list_of_env_pkg)
    return df_template

@click.command()
@click.option('--qiita_ebi_mims_path', required=True, type=click.Path(resolve_path=True, readable=True, exists=True), help='Excel file with Qiita/EBI and MIMS required fields. Example: Qiita_EBI_MIMS_v1.xlsx')
@click.option('--migs_mims_path', required=True, type=click.Path(resolve_path=True, readable=True, exists=True), help='Excel file with MIxS standards. Example: MIGS_MIMS_v4.xls')
@click.option('--list_of_env_pkg', required=True, type=click.STRING, help="One (recommended) or more (separated by commas) environmental package. Choose from: air, built environment, host-associated, human-associated, human-skin, human-oral, human-gut, human-vaginal, microbial mat/biofilm, misc environment, plant-associated, sediment, soil, wastewater/sludge, water")
@click.option('--number_of_samples', required=True, type=click.INT, help='Number of samples (per environmental package) to create rows for in the template')
@click.option('--sample_prefix', required=True, type=click.STRING, help='Prefix string to prepend to sample numbers in row indexes. Example: Metcalf40 (EMP500 PI and study number)')

# Main function: generate metadata template and readme csv files
def generate_metadata_template(qiita_ebi_mims_path, migs_mims_path, list_of_env_pkg, number_of_samples, sample_prefix):
    """Generate metadata template and readme csv files"""
    
    # Qiita/EBI/MIMS Excel file to DataFrames
    df_QiitaEBI = pd.read_excel(qiita_ebi_mims_path, sheetname='QiitaEBI', header=None)
    df_MIMS = pd.read_excel(qiita_ebi_mims_path, sheetname='MIMS', header=None)
    list_of_env_pkg = list_of_env_pkg.split(",")
    
    # MIGS/MIMS Excel file to DataFrames
    df_README = pd.read_excel(migs_mims_path, sheetname='README', header=None)
    df_MIGS_MIMS = pd.read_excel(migs_mims_path, sheetname='MIGS_MIMS', header=0, index_col=0)
    df_env_pkg = pd.read_excel(migs_mims_path, sheetname='environmental_packages', header=0)
    
    # generate template file
    df_template = create_template_for_env_pkg(df_QiitaEBI, df_MIMS, df_env_pkg, list_of_env_pkg, number_of_samples, sample_prefix)
    string_of_env_pkg = re.sub(r'\W', '_', '_'.join(list_of_env_pkg))
    df_template.to_csv('%s_%s_%s_samples.csv' % (sample_prefix, string_of_env_pkg, number_of_samples), index_label='index')
    
    # generate info file
    df_MIMS_select = df_MIGS_MIMS[df_MIGS_MIMS.Section.isin(['investigation', 'environment', 'migs/mims/mimarks extension'])]
    df_MIMS_select.to_csv('README_MIMS_metadata.csv')
    df_env_pkg_select = show_items_of_env_pkg(df_env_pkg, list_of_env_pkg)
    del df_env_pkg_select['Environmental package']
    df_env_pkg_select.set_index('Structured comment name', inplace=True)
    string_of_env_pkg = re.sub(r'\W', '_', '_'.join(list_of_env_pkg))
    df_env_pkg_select.to_csv('README_%s_metadata.csv' % string_of_env_pkg)

# Execute main function
if __name__ == '__main__':
    generate_metadata_template()
