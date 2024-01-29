import os
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='IMU - data post processing and clean up.')

    # remote manager.
    parser.add_argument('-c', '--clean', type=bool, default=True,
                        help='Clean the input file..')

    # source file name.
    parser.add_argument('-s', '--src', type=str, default="",
                        help='Source file name.')

    args = parser.parse_args()

    return args 


def clean_log_file(inFileFullPath):
    processFileFullPath = inFileFullPath + ".pdimu"

    with open(processFileFullPath, 'w') as wfs:
        with open(inFileFullPath, mode='r') as fs:
            for line in fs:
                # line = fs.readline()
                if(len(line.lstrip()) > 0):
                    wfs.write(line)
    
    return processFileFullPath


def clean_log_dir(inFolder, ext):

    for file in os.listdir(inFolder):
        if file.endswith(ext):
            logFileFullPath = os.path.join(inFolder, file)
            print("Processing the file: " + logFileFullPath)
            clean_log_file(logFileFullPath)

def main():
    args = parse_arguments()
    if(args.clean == True and len(args.src) > 0):
        # clean_log_file(args.src)
        clean_log_dir(args.src, ".dimu")


if __name__ == "__main__":
    main()