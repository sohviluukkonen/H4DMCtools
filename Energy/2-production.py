import csv
import os
import shutil
import argparse
import random
import H4Dtools_functions as tools

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
        -flex : flexible solute or rigid solute during propogation
        -nacc : nb of accumulations
        -nii and -nid : insertion and destruction intervales
        -nvac : nb of cycles for conformer generation in vacuum
        -ds : maximum displacement of solute sites
        -pws : relative probablities to move a solute or a solute site
        -dw : maximum translation of a solvent molecule
        -rw : maximum rotation of a solvent molecule
        -fb : force bias parameters
        -Vxp : volume exchange probablity
        -lnV : maximum volume exchange
        -auto : automatic determination of the starting index i
        -i : manual determination of the starting index
        -j : job handeling system

    Output :

        solute directory : {solute_name}
            input-ins + input-des
            acc_{solute_name}_ins{j}, r_{solute_name}_ins{j}, acc_{solute_name}_des{j}, r_{solute_name}_des{j}
        params_run_{j}.json file : recapitulation of run parameters
"""



# Parse input params #

parser = argparse.ArgumentParser()
parser.add_argument('--load_json', help="read paremeters from json_file (if not : uses default parameters or paremeters defined in the commond line)" )
parser.add_argument('-s','--solutes', default='FreeSolv-nm-V0-mu0.csv', help="File containing solute's name, volume and referce HFE (default: %(default)s)" )
parser.add_argument('-nacc', type=int, default=1000, help="nb of accumulations (default: %(default)s)" )
parser.add_argument('-flex', action='store_true', help="solute flexibility (default: %(default)s)" )
parser.add_argument('-nii','--nint_ins', type=int, help="insertion interval  (default rigid/flex : 100/100)" )
parser.add_argument('-nid','--nint_des', type=int, help="destruction interval  (default rigid/flex: 100/10000)" )
parser.add_argument('-nvac','--ngen_vac', type=int, help="nb of cycles for conformer generation in vacuum  (default rigid/flex 100/10000)" )
parser.add_argument('-ds', type=int, help="maximum displacement of solute sites (default rigid/flex : 0/0.1 Å)" )
parser.add_argument('-pws','--prob_wat_sol', type=int, nargs=2, help="relative probablities to move a solute or a solute site (default rigid/flex: 1 1 / 1 5)" )
parser.add_argument('-dw', type=float, default=0.3, help="maximum trastation of a solvent molecule (default: %(default)s Å)" )
parser.add_argument('-rw', type=int, default=30, help="maximum rotation of a solvent molecule (default: %(default)s deg)" )
parser.add_argument('-fb','--force_bias', type=float, nargs=2, default=[0.5,0.5], help="Force bias parameters (default rigid/flex: 1 1 / 1 5)" )
parser.add_argument('-Vxp','--vol_ex_prob', type=float, default=0.2, help=" Volume exchange probability (default: %(default)s)" )
parser.add_argument('-lnV', type=float, default=0.05, help="maximum ln(volume) exchange (default: %(default)s)" )
parser.add_argument('-i', type=int,  help="index of starting file (default: %(default)s)" )
parser.add_argument('-auto','--auto_continue', action='store_true', help="automatic determination of starting index (default: %(default)s)" )
parser.add_argument('-j', default="slurm", help=" Job handeling system : slumr or loadleveler  (default: %(default)s)" )
parser.add_argument('-ns','--nostart', action='store_true', help="do not launch jobs (default: %(default)s)" )
args = parser.parse_args()
print(args)

# default parameters for single conformer solute
if args.flex == False :
    args.nint_ins = args.nint_ins if args.nint_ins else 100
    args.nint_des = args.nint_des if args.nint_des else 100
    args.ngen_vac = args.ngen_vac if args.ngen_vac else 0
    args.ds = args.ds if args.ds else 0
    args.prob_wat_sol = args.prob_wat_sol if args.prob_wat_sol else [1,1]
# default parameters for flexible solute
if args.flex == True :
    args.nint_ins = args.nint_ins if args.nint_ins else 100
    args.nint_des = args.nint_des if args.nint_des else 1000
    args.ngen_vac = args.ngen_vac if args.ngen_vac else 10000
    args.ds = args.ds if args.ds else 0.1
    args.prob_wat_sol = args.prob_wat_sol if args.prob_wat_sol else [1,5]
print(args)

# Read parameters from .json file if given
if args.load_json: args = tools.json2args(args.load_json)

# get solute names
with open(args.solutes,'r') as f:
    lines = f.readlines()
    molecules = []
    for line in lines:
        molecules.append(line.split('\t')[0])
molecules.remove('Name')

home_dir = "%s" % os.getcwd()
input_dir = os.path.join(home_dir,'input-files')
sol_dir = os.path.join(home_dir,'solutein')

# Iterate over solutes
for mol in molecules:

    mol_dir = os.path.join(home_dir,mol)

    shutil.copy(os.path.join(input_dir,'job-ins'),mol_dir)
    shutil.copy(os.path.join(input_dir,'job-des'),mol_dir)

    # if auto continuation determine starting index
    if args.auto_continue == True :
        args.i = tools.auto_sim_index(mol,mol_dir=mol_dir)    
    
    # Check that index have been defined
    if args.i == None:
        print('No staring index : add manually with -i or automatic determination with -auto')

    tools.create_ins_input(args,solute=mol,mol_dir=mol_dir)
    tools.create_des_input(args,solute=mol,mol_dir=mol_dir)

    if args.nostart == True :
        continue
    else :
        if args.j == "slurm" :
            shutil.copy(os.path.join(input_dir,'job-ins'),mol_dir)
            shutil.copy(os.path.join(input_dir,'job-des'),mol_dir)
            job_ins_file = os.path.join(mol_dir,'job-ins')
            job_des_file = os.path.join(mol_dir,'job-des')
            os.system('sed -i "s/YY/{0}/g" {1}'.format(args.i+1,job_ins_file))
            os.system('sed -i "s/YY/{0}/g" {1}'.format(args.i+1,job_des_file))
            os.system("cd {0}; sbatch {1}; sbatch {2};  cd ..".format(mol_dir,job_ins_file,job_des_file))
        if args.j == "loadleveler" :
            shutil.copy(os.path.join(input_dir,'job-ins'),mol_dir)
            shutil.copy(os.path.join(input_dir,'job-des'),mol_dir)
            job_ins_file = os.path.join(mol_dir,'job-ins')
            job_des_file = os.path.join(mol_dir,'job-des')
            os.system('sed -i "s/YY/{0}/g" {1}'.format(args.i+1,job_ins_file))
            os.system('sed -i "s/YY/{0}/g" {1}'.format(args.i+1,job_des_file))
            os.system("cd {0}; llsubmit {1}; sbatch {2};  cd ..".format(mol_dir,job_ins_file,job_des_file))

tools.args2json('params_run_{}.out'.format(args.i+1),args)    
