from pickle import load

file1 = "./fae00b960cbd4c70ba179428a2cb21a3.pickle"
file2 = "./fae00b960cbd4c70ba179428a2cb21a3-2.pickle"

files = [file1, file2]

for i, file_i in enumerate(files):
    print("#######################################")
    with open(file_i, "rb") as file:
        print(load(file))