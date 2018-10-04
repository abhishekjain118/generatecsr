import subprocess
import time
from datetime import datetime, date, time
import re

def create_folder(folder_name): #done
    cmd_mkdir = "mkdir " +folder_name
    process = subprocess.Popen(cmd_mkdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if re.search(r'File exists',str(error)):
        print("Folder Exists: renaming existing "+folder_name+" folder and creating a new "+folder_name)
        cmd_mv = "mv "+folder_name+" "+folder_name+"_"+datetime.utcnow().strftime('%d%m%y_%H%M%S')
        #rename existing cnf folder as cnf_<today's date and time>
        process = subprocess.Popen(cmd_mv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(output, error)
        cmd_mkdir = "mkdir " + folder_name
        process = subprocess.Popen(cmd_mkdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #now makedir cnf
        output, error = process.communicate()
    else:
        print(folder_name+" folder created")
        print(output)

def read_config_files(): #done
        fqdn_file = open("fqdn.txt", "r")
        config_file = open("config.txt", "r")

        fqdns = []
        for line in fqdn_file:
            if (line.rstrip()):
                fqdns.append(line.strip())
        fqdn_file.close()

        fqdn_file = open("fqdn.txt", "r")
        kodiak_vms_in_fqdns = []
        for line in fqdn_file:
            if (line.rstrip()):
                kodiak_vms_in_fqdns.append((line.split('.')[0]))
        fqdn_file.close()

        values_in_config_files = []
        for line in config_file:
            values_in_config_files.append(line.split(':')[1].rstrip())
        config_file.close()

        return fqdns, kodiak_vms_in_fqdns, values_in_config_files

def generate_cnf_files(fqdn,values_in_config_files):

    out_cnf_file = open("cnf\\"+fqdn.split('.')[0]+".cnf", "x")
    out_cnf_file.write("[req]\nprompt = no\ndistinguished_name = dn\nreq_extensions = ext\n")
    out_cnf_file.write("[dn]\n" +
          "CN = " + fqdn
          + "\nOU = " + values_in_config_files[0]
          + "\nO = " + values_in_config_files[1]
          + "\nL = " + values_in_config_files[2]
          + "\nST = " + values_in_config_files[3]
          + "\nC = " + values_in_config_files[4]
          + "\n\n[ext]\n" +
          "subjectAltName=DNS:" + fqdn)
    print("cnf file generate for "+ fqdn)

def generate_private_key(kodiak_vm,base_path):
    key_path = "key_and_csr\\"
    cmd_genrsa = base_path+"openssl genrsa -out "+key_path+kodiak_vm+".key 2048"
    process = subprocess.Popen(cmd_genrsa.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if re.search(r'Generating RSA private key', str(error)):
        print("generate private key for "+kodiak_vm+": success")
    else:
        print("generate private key for "+kodiak_vm+": failed.")
        print(error)

def generate_csr(kodiak_vm, base_path):
    key_path = "key_and_csr\\"
    cmd_gencsr = base_path + "openssl req -new -sha256 -key "\
                 + key_path + kodiak_vm + ".key -config cnf/"+kodiak_vm+".cnf -out "+key_path+kodiak_vm+".csr"
    print(cmd_gencsr)
    process = subprocess.Popen(cmd_gencsr.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if (error):
        print("generate CSR for "+kodiak_vm+": failed.")
        print(error)
    else:
        print("generate CSR for "+kodiak_vm+": success")

def main():
    base_path = "C:\\OpenSSL-Win64\\bin\\"
    cnf_folder = "cnf"

    create_folder(cnf_folder) #create cnf folder. rename old cnf if exists.
    fqdns, kodiak_vms_in_fqdns, values_in_config_files = read_config_files() #read config and fqdns files.

    print(fqdns)
    print(kodiak_vms_in_fqdns)
    print(values_in_config_files)

    for fqdn in fqdns:
        generate_cnf_files(fqdn,values_in_config_files) #generate cnf files and put them in cnf folder

    create_folder("key_and_csr") # create folder called key_and_csr
    for kodiak_vm in kodiak_vms_in_fqdns:
        generate_private_key(kodiak_vm,base_path) # generate private keys for all entries in kodiak_vms.
        generate_csr(kodiak_vm, base_path) # generate CSRs for all entries in kodiak_vms.

if __name__ == "__main__":
    main()
    #print(output_error)
