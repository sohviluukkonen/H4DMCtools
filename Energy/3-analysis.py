import csv
import os
import shutil
import argparse
import random
import H4Dtools_functions as tools
import json
"""

Accumulation of ins/des for a set of solutes

    Input files :

        solute directory : {solute_name}
            acc_{solute_name}_ins{i}, r_{solute_name}_ins{i}, acc_{solute_name}_des{i}, r_{solute_name}_des{i}
            + other files from initialisation 
        database file (.csv) with 3 columns : solute_name \t solute's PMV \t refence HFE
        input-files directory : containing files for launching H4D-MC 

    Input parameters :

        --load_json : read paremeters from json_file (if not uses default parameters or paremeters defined in the commond line)
        -s, --solutes : database file name
        -pid : save ins and des distributions
        -e, --evol : evolution of HFE as a function of accumulations
        -auto : automatic determination of the starting index i
        -i : manual determination of the starting index

    Output :

        solute directory : {solute_name}
            input-ana
            pinsdes_{solute_name}_{i}.csv (optional)
        HFE-{i}.csv or HFE_evol.csv

"""



# Parse input params #

parser = argparse.ArgumentParser()
parser.add_argument('--load_json', help="read paremeters from json_file (if not : uses default parameters or paremeters defined in the commond line)" )
parser.add_argument('-s','--solutes', default='FreeSolv-nm-V0-mu0.csv', help="File containing solute's name, volume and referce HFE (default: %(default)s)" )
parser.add_argument('-pid', action='store_true', help="save ins and des distributions (default: %(default)s)" )
parser.add_argument('-e','--evol', action='store_true', help="save evolution of HFE in a single file (default: %(default)s)" )
parser.add_argument('-i', type=int,  help="index of starting file (default: %(default)s)" )
parser.add_argument('-auto','--auto_continue', action='store_true', help="automatic determination of starting index (default: %(default)s)" )
parser.add_argument('-j', default="slurm", help=" Job handeling system : slumr or loadleveler  (default: %(default)s)" )
args = parser.parse_args()
print(args)

# Read parameters from .json file if given
if args.load_json: args = tools.json2args(args.load_json)

# Load solutes with their volumes and reference HFEs
data = tools.from_file_to_dict(args.solutes,'\t')
keys = ['V0','mu0']
dict_solutes = dict(zip(keys,data))

# Paths
home_dir = "%s" % os.getcwd()
input_dir = os.path.join(home_dir,'input-files')

if args.evol == True:
    dict_HFE = {}
# Iterate over solutes
j = 0
for mol,mu0 in dict_solutes['mu0'].items():

    mol_dir = os.path.join(home_dir,mol)

    # Determine index
    if j == 0 :
        # if auto continuation determine starting index
        if args.auto_continue == True :
            args.i = tools.auto_sim_index(mol,mol_dir=mol_dir)            
        # Check that index have been defined
        if args.i == None:
            print('No staring index : add manually with -i or automatic determination with -auto')

    # Print single HFE
    if args.evol == False :
        # Create input-ana
        tools.create_analysis_input(args,solute=mol,mu0=mu0,mol_dir=mol_dir)
        # Run analysis
        os.system("cd {0}; pwd; ./mc_h2o_isobar_hybrid_0_gf-260620.x < input-ana > out-ana; cd ..".format(mol_dir))
        out_file = os.path.join(mol_dir,'out-ana')
        
        # Collect HFE from out-ana
        with open(out_file,'r') as f :
            lines = f.readlines()
            for index,line in enumerate(lines):
                # Create output file
                if 'Nombre d\'accumulations' in line :
                    nacc = lines[index].split()[-1]
                if 'BAR' in line :
                    hfe=lines[index+9].split()[1]
                    err=lines[index+9].split()[2]
        if j == 0 :
            f1 = open('HFE-{}.csv'.format(nacc),'w')
            f1.write('Name\t HFE\t err\n')
            j = 100
        f1.write('{}\t {}\t {}\n'.format(mol,hfe,err))

    # Print evolution of HFEs
    if args.evol == True :
        imax = args.i
        for i in range(1,imax+1):
            args.i = i
            # Create input-ana
            tools.create_analysis_input(args,solute=mol,mu0=mu0,mol_dir=mol_dir)
            # Run analysis
            os.system("cd {0}; pwd; ./h4dmc.x < input-ana > out-ana; cd ..".format(mol_dir))
            out_file = os.path.join(mol_dir,'out-ana')
            
            # Collect HFE from out-ana
            with open(out_file,'r') as f :
                lines = f.readlines()
                for index,line in enumerate(lines):
                    # Create output file
                    if 'Nombre d\'accumulations' in line :
                        nacc = lines[index].split()[-1]
                    if 'BAR' in line :
                        hfe=lines[index+9].split()[1]
                        err=lines[index+9].split()[2]
            if j == 0 :
                dict_HFE['HFE-{}'.format(nacc)] = {}
                dict_HFE['err-{}'.format(nacc)] = {}

            dict_HFE['HFE-{}'.format(nacc)][mol] = hfe
            dict_HFE['err-{}'.format(nacc)][mol] = err
        
        j = 100

if args.evol == True :
    # json file
    with open('HFE_evol.json', 'w') as fp:
        json.dump(dict_HFE, fp)
    # csv file
    f2 = open('HFE_evol.csv','w')
    f2.write('name\t')
    for k in dict_HFE.keys():
        f2.write('{}\t'.format(k))
    f2.write('\n')
    
    for mol in dict_HFE['HFE-{}'.format(nacc)].keys():
        f2.write('{}\t'.format(mol))
        for k in dict_HFE.keys():
            f2.write('{}\t'.format(dict_HFE[k][mol]))
        f2.write('\n')
