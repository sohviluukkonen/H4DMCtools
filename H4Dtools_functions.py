import os
import random 
import json

def json2args(file):
    ''' Read arguments from json file '''
    with open(file, 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        return  parser.parse_args(namespace=t_args)

def args2json(file,args):
    ''' Save arguments to json file '''
    with open(file, 'w') as f:
        json.dump(args.__dict__, f, indent=2)

def mkdir_p(dir):
    ''' Make a directory (dir) if it doesn't exist'''
    if not os.path.exists(dir):
        os.mkdir(dir)

def auto_sim_index(solute,mol_dir="%s" % os.getcwd()):
    ''' Find largest existing _des or _s files to automatically continue simulation '''
    i = 0
    while os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_des%d' % i )) :
        i += 1
    while os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_s%d' % i )):
        i += 1 
    return i-1

def from_file_to_dict(file,sep):
    ''' Create directory form a file n columns :
        1st column --> solutes --> keys
        Other columns --> V0 and mu0 --> subdirectories '''

    list_dict=[]
    with open(file,'r') as f :
        line = f.readline()
        cols = line.split(sep=sep)
        number_of_col=len(cols)
        for i in range(number_of_col-1):
            list_dict.append({})

        for l,line in enumerate(f) :
            cols = line.split(sep=sep)
            for i in range (1,number_of_col):
                #print(cols[i])
                list_dict[i-1][cols[0]] = float(cols[i])
    f.close()
    return tuple(list_dict) 

def create_structure_initialisation_input( args, solute='dummy', V0=0, mu0=0, mol_dir="%s" % os.getcwd() ):

    ''' Create initialisation input for structure
        Output : input-ini '''

    kT = args.T * 1.3806 * 10**-23 * 10**-3 * 6.0221409 * 10**23
    dict_water = {}
    dict_water['TIP3P'] = dict(sig = 3.15061, eps = 0.6364 / kT, l = 0.9572, ang = 104.52, qH = 0.4170, eps0=99)
    dict_water['SPCE'] = dict(sig = 3.166, eps = 0.65 / kT, l = 1.0000, ang = 109.47, qH = 0.4238, eps0=72)

    f = open(os.path.join(mol_dir,'input-ini'),'w')

    if args.create_box == False:

        # Open ref file
        if os.path.isfile(os.path.join(mol_dir,'acc_' + args.infile)) == True:
            f.write('53\n')
            f.write('{}\n 0 0\n \n'.format(args.infile))
        else:
            print('No refence files !')

    #Solute + solvent + box params
    f.write('1\n')
    f.write('{0}\n {1}\n {2}\n'.format(args.N,args.T,args.P))
    f.write('{0}\n {1}\n {2} {3}\n {4}\n'.format( dict_water[args.water]['sig'], dict_water[args.water]['eps'],
                                           dict_water[args.water]['l'], dict_water[args.water]['ang'],
                                           dict_water[args.water]['qH']) )
    f.write('{0}\n {1} {2}\n'.format(args.Ewald[0],args.Ewald[1],args.Ewald[2]))
    f.write('{0}\n'.format(dict_water[args.water]['eps0']))
    f.write('{0}\n 0\n'.format(args.nmax0))
    f.write('{0}.in \n 1 \n 0\n'.format(solute))
    if os.path.isfile(os.path.join(mol_dir,'{}.top'.format(solute))) == True:
        f.write('{}.top\n'.format(solute))
    else :
        f.write('dummy.top \n')
        print('Solute specific top file does not exist. Using dummy file.')
    f.write('{0}\n\n'.format(args.C))

    # Ins/des params
    f.write('4\n')
    f.write('{0} \n {1} \n 0.1 0.1 \n 1 1\n'.format(args.nr,args.dr))
    f.write('0\n')
    f.write('3 0.05 \n 0 1 \n 0.02 \n 0 \n')
    f.write('1\n 1 1 1 \n')
    f.write('8 3 3 \n')
    f.write('2000 \n 0.5 \n 0 \n 0 \n 1e20 \n 1 \n \n')

    #If no refence file create box
    if args.create_box == True:
        f.write('2 \n {}\n \n'.format(random.randint(1,10000)))

    #Simulation
    f.write('8\n')
    f.write('00\n {}\n'.format(random.randint(1,10000)))
    if args.create_box == True: # equilibrate box
        f.write('10000 \n 10000 \n 0\n')
        f.write('0.3 \n 30 \n 0.5 0.5 \n 0 \n 0.2 \n 0.05 \n 0 \n 1 1 \n 0 \n')
    else: # if starting with equilibrated water box
        f.write('0\n \n')
    f.write('4\n 0\n')
    # Add solute for des + equil
    f.write('7\n 0\n {}\n\n'.format(random.randint(1,10000)))
    f.write('8\n {}\n'.format(random.randint(1,10000)))
    f.write('{0} \n {1} \n 0\n'.format(args.equil,args.equil))
    f.write('0.3 \n 30 \n 0.5 0.5 \n 0 \n 0.2 \n 0.05 \n 0 \n 1 1 \n 0 \n \n')

    # Save des0 file
    f.write('4\n 2\n 12 \n')
    f.write('{}_s0'.format(solute))


def create_structure_input(args,solute='dummy',mol_dir="%s" % os.getcwd() ):

    f = open(os.path.join(mol_dir,'input-str'),'w') 
    if os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_s%d' % args.i)) == True:
        f.write('53\n')
        f.write('{}\n 1 0\n \n'.format(solute + '_s%d' % args.i))
    else:
        print('No accumulation file corresponding to starting index !')

    f.write('8\n {}\n'.format(random.randint(1,10000)))
    n = args.nacc*args.nint_ins
    f.write('{0}\n 0\n {1}\n'.format(n,args.nint_ins))
    f.write('{0}\n {1}\n {2}\n {3}\n 0\n'.format(args.dw,args.rw,args.force_bias[0],args.force_bias[1]))
    f.write('{0}\n {1}\n'.format(args.vol_ex_prob,args.lnV))
    f.write('{0}\n 1 1\n {1}\n\n'.format(args.ds,args.ngen_vac))
    f.write('4\n 2\n 12\n{0}_s{1}'.format(solute,args.i+1))


def create_initialisation_input( args, solute='dummy', V0=0, mu0=0, mol_dir="%s" % os.getcwd() ):

    ''' Create initialisation input for H4D 
        Output : input-ini '''

    kT = args.T * 1.3806 * 10**-23 * 10**-3 * 6.0221409 * 10**23
    dict_water = {}
    dict_water['TIP3P'] = dict(sig = 3.15061, eps = 0.6364 / kT, l = 0.9572, ang = 104.52, qH = 0.4170, eps0=99)
    dict_water['SPCE'] = dict(sig = 3.166, eps = 0.65 / kT, l = 1.0000, ang = 109.47, qH = 0.4238, eps0=72)

    f = open(os.path.join(mol_dir,'input-ini'),'w')

    if args.create_box == False:

        # Open ref file
        if os.path.isfile(os.path.join(mol_dir,'acc_' + args.infile)) == True:
            f.write('53\n')
            f.write('{}\n 0 0\n \n'.format(args.infile))
        else:
            print('No refence files !')

    #Solute + solvent + box params
    f.write('1\n')
    f.write('{0}\n {1}\n {2}\n'.format(args.N,args.T,args.P))
    f.write('{0}\n {1}\n {2} {3}\n {4}\n'.format( dict_water[args.water]['sig'], dict_water[args.water]['eps'],
                                           dict_water[args.water]['l'], dict_water[args.water]['ang'],
                                           dict_water[args.water]['qH']) )
    f.write('{0}\n {1} {2}\n'.format(args.Ewald[0],args.Ewald[1],args.Ewald[2]))
    f.write('{0}\n'.format(dict_water[args.water]['eps0']))
    f.write('4\n 0\n')
    f.write('{0}.in \n 1 \n 0\n'.format(solute))
    if os.path.isfile(os.path.join(mol_dir,'{}.top'.format(solute))) == True:
        f.write('{}.top\n'.format(solute))
    else :
        f.write('dummy.top \n')
        print('Solute specific top file does not exist. Using dummy file.')
    f.write('{0}\n\n'.format(args.C))

    # Ins/des params
    f.write('4\n')
    f.write('500 \n 0.025 \n 0.1 0.1 \n 1 1\n')
    f.write('1\n')
    f.write('{0} {1} \n 0 1 \n {2} \n 0 \n'.format(args.wmax,args.v,args.dt))
    f.write('1\n 1 1 1 \n')
    f.write('{0} {1} {2} \n'.format(args.Ewald2[0],args.Ewald2[1],args.Ewald2[2] ))
    f.write('{0} \n {1} \n {2} \n {3} \n {4} \n 1 \n \n'.format(args.Hrange,args.dH,mu0,V0,args.mass))

    #If no refence file create box
    if args.create_box == True:
        f.write('2 \n {}\n \n'.format(random.randint(1,10000)))

    #Simulation
    f.write('8\n')
    f.write('00\n {}\n'.format(random.randint(1,10000)))
    if args.create_box == True: # equilibrate box
        f.write('10000 \n 10000 \n 0\n')
        f.write('0.3 \n 30 \n 0.5 0.5 \n 0 \n 0.2 \n 0.05 \n 0 \n 1 1 \n 0 \n')

    else: # if starting with equilibrated water box
        f.write('0\n \n')

    # Save ins0 file
    f.write('4\n 2\n 12 \n')
    f.write('{}_ins0 \n 0 \n \n'.format(solute))

    # Add solute for des + equil
    f.write('7\n 0\n {}\n\n'.format(random.randint(1,10000)))
    f.write('8\n {}\n'.format(random.randint(1,10000)))
    f.write('{0} \n {1} \n 0\n'.format(args.equil,args.equil))
    f.write('0.3 \n 30 \n 0.5 0.5 \n 0 \n 0.2 \n 0.05 \n 0 \n 1 1 \n 0 \n \n')

    # Save des0 file
    f.write('4\n 2\n 12 \n')
    f.write('{}_des0'.format(solute))


def create_ins_input(args,solute='dummy',mol_dir="%s" % os.getcwd() ):
    
    f = open(os.path.join(mol_dir,'input-ins'),'w')
    if os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_ins%d' % args.i)) == True:
        f.write('53\n')
        f.write('{}\n 0 0\n \n'.format(solute + '_ins%d' % args.i))
    else:
        print('No ins file corresponding to starting index !')

    f.write('8\n00\n {}\n'.format(random.randint(1,10000)))
    n = args.nacc*args.nint_ins
    f.write('{0}\n 0\n {1}\n'.format(n,args.nint_ins))
    f.write('{0}\n {1}\n {2}\n {3}\n 0\n'.format(args.dw,args.rw,args.force_bias[0],args.force_bias[1]))
    f.write('{0}\n {1}\n'.format(args.vol_ex_prob,args.lnV))
    f.write('{0}\n 1 1\n {1}\n\n'.format(args.ds,args.ngen_vac))
    f.write('4\n 2\n 12\n{0}_ins{1}'.format(solute,args.i+1))

def create_des_input(args,solute='dummy',mol_dir="%s" % os.getcwd() ):

    f = open(os.path.join(mol_dir,'input-des'),'w')
    if os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_des%d' % args.i)) == True:
        f.write('53\n')
        f.write('{}\n 1 0\n \n'.format(solute + '_des%d' % args.i))
    else:
        print('No des file corresponding to starting index !')

    f.write('8\n {}\n'.format(random.randint(1,10000)))
    n = args.nacc*args.nint_des
    f.write('{0}\n 0\n {1}\n'.format(n,args.nint_des))
    f.write('{0}\n {1}\n {2}\n {3}\n 0\n'.format(args.dw,args.rw,args.force_bias[0],args.force_bias[1]))
    f.write('{0}\n {1}\n'.format(args.vol_ex_prob,args.lnV))
    f.write('{0}\n {1} {2}\n 0\n\n'.format(args.ds,args.prob_wat_sol[0],args.prob_wat_sol[1]))
    f.write('4\n 2\n 12\n{0}_des{1}'.format(solute,args.i+1))

def create_analysis_input(args,solute='dummy',mu0=0,mol_dir="%s" % os.getcwd() ):

    f = open(os.path.join(mol_dir,'input-ana'),'w')
    if os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_ins%d' % args.i)) == True:
        f.write('53\n')
        f.write('{}\n 0 0\n \n'.format(solute + '_ins%d' % args.i))
    else:
        print('No ins file corresponding to starting index : {} !'.format(args.i))
    f.write('8\n00\n 90\n 0\n 4\n 0\n')
    
    if os.path.isfile(os.path.join(mol_dir,'acc_' + solute + '_des%d' % args.i)) == True:
        f.write('53\n')
        f.write('{}\n 1 0\n \n'.format(solute + '_des%d' % args.i))
    else:
        print('No ins file corresponding to index : {} !'.format(args.i))
    f.write('8\n 90\n 0\n 4\n')

    if args.pid == True:
        f.write('2\n 15\n')
        f.write('pinsdes_{0}_{1}'.format(solute,args.i))
    
    f.write('1\n 6\n 1\n -50\n 1\n -400 400\n 6\n {}\n'.format(mu0))

if __name__ == "__main__":
    mkdir_p()
    from_file_to_dict()
