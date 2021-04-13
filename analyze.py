import pickle, os
from collections import defaultdict

# List of all maps between number and data
# Each key is one of the first elements in each mapTypes list
# Each value is a dict, which maps numbers (keys) to their human-readable value
maps = {}

# The different variable types we care about.
# [variable name, col_start - 1, col_end]
# mapTypes = [["building_material", 70, 73], 
#             ["ethnicity", 113, 115], 
#             ["general_religion", 108, 109], 
#             ["location", 65, 68], 
#             ["religion", 109, 113], 
#             ["structure_age", 77, 80], 
#             ["structure_age_no_interval", 80, 83]]

# The different variable types we care about.
# [variable name, col_start - 1, col_end]
mapTypes = [["serial", 16, 28],
            ["gq", 36, 38],
            ["regnro", 38, 39],
            ["ownership", 39, 40],
            ["rooms", 43, 45],
            ["hhtype", 48, 50],
            ["ro2011a_livarea", 50, 53],
            ["age", 65, 68],
            ["sex", 68, 69],
            ["chborn", 69, 71],
            ["religion", 71, 72],
            ["educro", 76, 79],
            ["empstat", 79, 80],
            ["eempstat", 83, 86],
            ["ro2011a_ethnic", 86, 88]]

# Load a passed in map file to the maps dict
def loadMap(mapType):
    # If it is serial, it does not have a lookup table. Otherwise, pull its lookup table, and load it into the `maps` variable
    if not mapType == "serial":
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

    def getProp(self, key):
        return self.props[key]

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

    def __repr__(self):
        out = "Entry:"

        for k,v in self.props.items():
            out = out + f"\n\t{k}:\t{v}"

        return out

# Creates an Entry object from a line in the data file
def createEntry(line):
    props = defaultdict(dict)
    for m in mapTypes:
        if m[0] == "serial":
            props[m[0]] = line[m[1]:m[2]]
        else:
            props[m[0]] = maps[m[0]][line[m[1]:m[2]]]

    entry = Entry(props)

    return entry

def getEntriesWithProps(entries, props):
    return [p for p in filter(lambda p: p.hasProps(props), entries)]

def calculateDistribution(entries, variable):
    regions = ["Bucharest Sector 1", "Bucharest Sector 2", "Bucharest Sector 3", "Bucharest Sector 4", "Bucharest Sector 5", "Bucharest Sector 6"]

    distributions = {}

    for r in regions:
        print(f"Region: {r}")
        distributions[r] = {}

        # Get all entries within that region
        in_region = getEntriesWithProps(entries, {"location": r})

        # For each possible ethnicity, calculate the fraction of that ethnicity over the total pop of that region
        for e in maps[variable].values():
            fraction_of_pop = len(getEntriesWithProps(in_region, {variable: e}))/len(in_region)

            # Add each value that is != 0 to distributions[region][ethnicity]
            if fraction_of_pop > 0:
                distributions[r][e] = fraction_of_pop

        # Sort the items in the dict by value, highest to lowest (reverse)
        sorted_distributions = sorted(distributions[r].items(), key=lambda item: item[1], reverse=True)

        for e,f in sorted_distributions:
            print(f"{variable}: {e}\t\t\t\t\t\t% Pop: {f*100:.3f}")
        
        print()

########################################
# BASE VARIABLES FOR ARMAS CALCULATION #
########################################

# Return number of unique SERIAL values
def countHouseholds(entries):
    # This is supposedly best practice, but is probably ridiculously slow
    serials = [e.getProp("serial") for e in entries]
    return len(set(serials))

# Return count of entries with age < 18
def countChildren(entries):
    children = filter(lambda p: int(p.getProp("age")) < 18, entries)

    return len(children)

# Return count of women
def countWomen(entries):
    women = filter(lambda p: p.hasProp({"sex": "Female"}))

    return len(women)

# Return count of men
def countMen(entries):
    men = filter(lambda p: p.hasProp({"sex": "Male"}))

    return len(men)

# Return count of women with 3 or more children
def countWomenWith3Children(entries):
    womenWithManyChildren = filter(lambda p: int(p.getProp("chborn")) > 2, entries)

    return len(womenWithManyChildren)

# Count the number of women who were 15 or older when they had a child
# ASSUMPTION: If any child was born when they were over 15, the qualify
#           Consider: Maybe if any child was had before 15, they are disqualified?
def countWomen15OlderWithChild(entries):
    # Find all with MOMLOC
    # Lookup mom
    # Subtract child age from mom age, if 15+, add to list
    # return len(list)
    pass

# Count the number of entries with education of Literacy Courses or Primary
# ASSUMPTION: Minimum education is up through primary, but does not include anything else
def countWithMinimumEducation(entries):
    minEducation = filter(lambda p: p.getProp("educro") in ["Primary", "Literacy Courses"], entries)
    
    return len(minEducation)

# Count the number of entries who are over 10 years old
def countAgeOver10(entries):
    overTen = filter(lambda p: int(p.getProp("age")) > 10, entries)

    return len(overTen)

# Count the total size of buildings in square meters
def countTotalLivingArea(entries):
    # Initialize living area to 0
    totalLivingArea = 0

    # Get each unique household
    # {serial: entry}
    households = {}

    # For each entry
    for e in entries:
        # If this household (by serial) isn't already in the dictionary
        if e.getProp("serial") not in households:
            # Add it to the dictionary
            households[e.getProp("serial")] = e

    # Iterate over the dictionary with s(eries) and e(ntry)
    for s,e in households.items():
        # Add this household's living area to the total
        totalLivingArea += int(e.getProp("ro2011a_livarea"))

    return totalLivingArea

########################################

# All lines from the data file
lines = []
entries_in_bucharest = []

for m in mapTypes:
    loadMap(m[0])

if os.path.exists("bucharest_entries.dat"):
    print("Data has been processed, loading .dat")
    entries_in_bucharest = pickle.load(open("bucharest_entries.dat", "rb"))
else:
    print("Loading from IPUMS data")
    with open("ipumsi_00002.dat") as data:
        lines = data.readlines()

    print(f"Data length: {len(lines)}")

    # Create an entry for each data line
    all_people = [createEntry(line) for line in lines]

    print("Created data set. Pulling all in Bucharest...")

    entries_in_bucharest = [p for p in filter(lambda p: p.hasProps({"regnro": "Bucharest"}), all_people)]

    pickle.dump(entries_in_bucharest, open("bucharest_entries.dat", "wb+"))

print("Pulled all Bucharest data. Entering interactive terminal to check different parameters for those in Bucharest")
print(f"Entries in bucharest: {len(entries_in_bucharest)}")

# while True:
#     var_name = input("Variable name (? for all): ")

#     if var_name == "?":
#         for m in mapTypes:
#             print(m[0])
#         continue

#     if var_name not in [m[0] for m in mapTypes]:
#         print("Invalid variable name.")
#         continue

#     val = input("Value (? for possible values): ")

#     if val == "?":
#         m = maps[var_name]
#         for k in m:
#             print(m[k])
#         continue
    
#     if val not in maps[var_name].values():
#         print("Invalid value.")
#         continue
    

#     matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: val}), entries_in_bucharest)]

#     print(f"Total count: {len(matching_entries)}")
#     print(f"Total percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")