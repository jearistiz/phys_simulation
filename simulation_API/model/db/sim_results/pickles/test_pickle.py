from pickle import load

file1 = "./aadd3df27e3a4dd1849668015323b790.pickle"
file2 = "./aadd3df27e3a4dd1849668015323b790-2.pickle"

files = [file1, file2]

for i, file_i in enumerate(files):
    print("#######################################")
    with open(file_i, "rb") as file:
        print(load(file))