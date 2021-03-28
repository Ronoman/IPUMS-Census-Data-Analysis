import pickle, os

# List of all maps between number and data
# Each key is one of the first elements in each mapTypes list
# Each value is a dict, which maps numbers (keys) to their human-readable value
maps = {}

# The different variable types we care about.
# [variable name, col_start - 1, col_end]
mapTypes = [["building_material", 70, 73], ["ethnicity", 113, 115], ["general_religion", 108, 109], ["location", 65, 68], ["religion", 109, 113], ["structure_age", 77, 80], ["structure_age_no_interval", 80, 83]]

# Load a passed in map file to the maps dict
def loadMap(mapType):
    with open(mapType + "_map.txt") as f:
        mappings = f.readlines()
        mappings = [m.split("\t\t") for m in mappings]
        mappings = [[m[0],  m[1].strip("\n")] for m in mappings]

        thisMap = {}
        
        for (k,v) in mappings:
            thisMap.setdefault(k,v)
        
        maps.setdefault(mapType, thisMap)

# A single entry from the data file.
class Entry:
    def __init__(self, props):
        # self.props is a dictionary which maps a variable name to a value
        self.props = props

    # If this person has all of the properties in props, return true
    def hasProps(self, props):
        for k in props:
            if not self.props[k] == props[k]:
                return False
        return True

    # Returns true if any of the elements values exist as a k,v pair in self.props
    # Used to find if this entry is one of a group for a single variable
    def hasOneOf(self, var_name, values):
        for v in values:
            if self.hasProps({var_name: v}):
                return True
        return False

# Creates an Entry object from a line in the data file
def createEntry(line):
    props = {}
    for m in mapTypes:
        props[m[0]] = maps[m[0]][line[m[1]:m[2]]]

    entry = Entry(props)

    return entry

#def calculateEthnicityDistribution(entries):
    #ethnicities = {}

    #for e in maps["ethnicities"].keys():
        #count = 

# All lines from the data file
lines = []
entries_in_bucharest = []

if os.path.exists("bucharest_entries.dat"):
    print("Data has been processed, loading .dat")
    entries_in_bucharest = pickle.load(open("bucharest_entries.dat", "rb"))
else:
    print("Loading from IPUMS data")
    with open("ipumsi_00001.dat") as data:
        lines = data.readlines()

    print(f"Data length: {len(lines)}")

    # Create an entry for each data line
    all_people = [createEntry(line) for line in lines]

    print("Created data set. Pulling all in Bucharest...")

    in_bucharest = ["Bucharest Sector 1", "Bucharest Sector 2", "Bucharest Sector 3", "Bucharest Sector 4", "Bucharest Sector 5", "Bucharest Sector 6"]
    entries_in_bucharest = [p for p in filter(lambda p: p.hasOneOf("location", in_bucharest), all_people)]

    pickle.dump(entries_in_bucharest, open("bucharest_entries.dat", "wb+"))

for m in mapTypes:
    loadMap(m[0])

print("Pulled all Bucharest data. Entering interactive terminal to check different parameters for those in Bucharest")
print(f"Entries in bucharest: {len(entries_in_bucharest)}")

while True:
    var_name = input("Variable name (? for all): ")

    if var_name == "?":
        for m in mapTypes:
            print(m[0])
        continue

    if var_name not in [m[0] for m in mapTypes]:
        print("Invalid variable name.")
        continue

    val = input("Value (? for possible values): ")

    if val == "?":
        m = maps[var_name]
        for k in m:
            print(m[k])
        continue
    
    if val not in maps[var_name].values():
        print("Invalid value.")
        continue
    

    matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: val}), entries_in_bucharest)]

    print(f"Total count: {len(matching_entries)}")
    print(f"Total percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")
