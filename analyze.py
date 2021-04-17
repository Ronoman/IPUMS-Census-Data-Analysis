import pickle, os
from collections import defaultdict

# Completely arbitrary, will be decided based on real info soon
SALARY_CUTOFF = 20000

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
            ["pernum", 53, 57],
            ["momloc", 65, 68],
            ["parrule", 68, 70],
            ["stepmom", 70, 71],
            ["age", 71, 74],
            ["sex", 74, 75],
            ["marst", 75, 76],
            ["chborn", 79, 81],
            ["religion", 81, 82],
            ["educro", 86, 89],
            ["empstat", 89, 90],
            ["eempstat", 93, 96],
            ["indgen", 96, 99],
            ["hrsmain", 99, 102]
            ["ro2011a_ethnic", 102, 104],
            ["income"]]

# Load a passed in map file to the maps dict
def loadMap(mapType):
    # If it is serial, it does not have a lookup table. Otherwise, pull its lookup table, and load it into the `maps` variable
    if not mapType in ["serial", "pernum", "momloc", "hrsmain"]:
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
        # Skip over all variables that do not have a lookup table
        if m[0] in ["serial", "pernum", "momloc", "hrsmain"]:
            props[m[0]] = line[m[1]:m[2]]
        # All others, except income (not in dataset) have a map lookup
        elif not m[0] == "income":
            props[m[0]] = maps[m[0]][line[m[1]:m[2]]]

    entry = Entry(props)

    # Get salary by indgen (reduce to salary/wk)
    salary = int(maps["income"][entry.getProp("indgen")]) / 52.0

    # Get hours by hrsmain
    hours = int(entry.getProp("hrsmain"))

    # Multiply together, convert hrs/wk to hrs/yr (*52), set to entry["income"]
    entry["income"] = salary * hours * 52

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

# Helper fn: Returns all unique household entries.
def getUniqueHouseholds(entries):
    serials = {}
    households = []
    
    for e in entries:
        if e.getProp("serial") not in serials:
            serials.add(e.getProp("serial"))
            households.append(e)

    return households

# Return number of unique SERIAL values
def countHouseholds(entries):
    # This is supposedly best practice, but is probably ridiculously slow
    households = getUniqueHouseholds(entries)
    return len(households)

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
# ASSUMPTION: If any child was had before 15, they are disqualified (not part of the total)
def countWomen15OlderWithChild(all, entries):
    total_mothers = 0

    # Dict where entries are keyed by their pernum
    pernums = defaultdict(dict)

    # Women keyed by pernum. If value is true, they were >=15 when they had a child. If false, they were <15
    women = defaultdict(dict)

    for p in entries:
        pernums[p.getProp("pernum")] = p

    # Find all with MOMLOC
    with_mothers = filter(lambda p: not int(p.getProp("momloc")) == 0, all)

    # Lookup the mother of each child
    for p in with_mothers:
        num = p.getProp("momloc")
        child_age = int(p.getProp("age"))

        # If that mother is in this ethnic/religious group (in pernums from entries, not all)
        if num in pernums:
            # Calculate the mother's age
            mom_age = int(pernums[num].getProp("age"))

            age_at_birth = mom_age - child_age

            # If the difference in ages is at least 15 years, then this mother counts
            if(age_at_birth >= 15):
                women[num] = True
            else:
                # Otherwise, explicitly exclude. This is to catch mothers who had a single child when they were under 15
                women[num] = False

    # Return the length of the list of women who were set to True after all processing
    return len([m for m in women.items() if m])


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
    households = getUniqueHouseholds(entries)

    # Iterate over the dictionary with s(eries) and e(ntry)
    for e in households:
        # Add this household's living area to the total
        totalLivingArea += int(e.getProp("ro2011a_livarea"))

    return totalLivingArea

# Count the number of unemployed individuals
# ASSUMPTION: If not eempstat == Employed, they are not employed
#             (NIU, Unemployed, not economically active are all not employed)
def countUnemployed(entries):
    unemployed = filter(lambda p: not p.getProp("eempstat") == "Employed", entries)

    return len(unemployed)

# Count the total number of rooms across households
def countRooms(entries):
    rooms = 0

    # Get each unique household
    households = getUniqueHouseholds(entries)

    for e in households.items:
        rooms += int(e.getProp("rooms"))

    return rooms

# Count the number of privately owned households
def countPrivateHomes(entries):
    households = getUniqueHouseholds(entries)

    private = filter(lambda h: h.getProp("ownership") == "Owned", households)

    return len(private)

# Count the number of privately owned households with 5+ rooms
def countPrivateWith5Rooms(entries):
    households = getUniqueHouseholds(entries)

    large_households = filter(lambda h: h.getProp("ownership") == "Owned" and int(h.getProp("rooms")) > 4, entries)

    return len(large_households)

# Count the number of economically active individuals
# ASSUMPTION: Employed in EEMPSTAT is the only qualifier
#             This matches with how the unemployed and economically active variables are used in the Armas report
def countEconomicallyActive(entries):
    return len(filter(lambda e: e.getProp("eempstat") == "Employed", entries))

# Count the number of socially dependand individuals
# ASSUMPTION: Anyone younger than 12 or older than 80 are socially dependant. We could not find any discrete definitions
#             of how this value should be calculated, from either the Armas report or independent research. This is
#             as close to arbitrary as you can get.
def countSociallyDependant(entries):
    young = filter(lambda e: int(e.getProp("age")) < 12, entries)
    old   = filter(lambda e: int(e.getProp("age")) < 80, entries)

    return len(young) + len(old)

# Count the number of individuals over 65 years old
def countElderly(entries):
    return len(filter(lambda e: int(e.getProp("age")) > 65, entries))

# Count the number of high income earners
def countHighIncomeMen(entries):
    high = filter(lambda p: int(p.getProp("income")) > SALARY_CUTOFF and p.getProp("sex") == "Male", entries)

    return len(high)

def countHighIncomeWomen(entries):
    high = filter(lambda p: int(p.getProp("income")) > SALARY_CUTOFF and p.getProp("sex") == "Female", entries)

    return len(high)

# Count the number of low income earners
def countLowIncome(entries):
    low = filter(lambda p: int(p.getProp("income")) <= SALARY_CUTOFF, entries)

    return len(low)

# Count the number of widows
def countWidows(entries):
    widows = filter(lambda p: p.getProp("marst") == "Widowed", entries)

    return len(widows)

########################################

########################################
#  INDICATOR PROCESSING   #
########################################

def getIndicators(entries, all):
    indicators = []

    ### SOCIAL ###
    # 0: Ratio elderly
    indicators.append(countElderly(entries) / len(entries))

    # 1: Ratio female
    indicators.append(countWomen(entries) / len(entries))

    # 2: Ratio children
    indicators.append(countChildren(entries) / len(entries))

    # 3: Ratio widows in female population
    indicators.append(countWidows(entries) / countWomen(entries))

    # 4: Housing density
    indicators.append(len(entries) / countTotalLivingArea(entries))

    # 5: Average wage earners per household
    # Defined by Armas as number with min education / number population, which is weird
    # In my mind, it should be number employed / number population
    indicators.append(countWithMinimumEducation(entries) / len(entries))

    # 6: 
    ##############

    ### ECONOMIC ###
    # 7: Ratio of unemployed
    indicators.append(countUnemployed(entries) / len(entries))

    # 8: Ratio of low income
    indicators.append(countLowIncome(entries) / len(entries))

    # 9: Ratio of high income women
    indicators.append(countHighIncomeWomen(entries) / countWomen(entries))

    # 10: Ratio of high income men
    indicators.append(countHighIncomeMen(entries) / countMen(entries))
    ################

    ### HOUSING ###
    # 11: Room occupancy per household
    indicators.append(len(entries) / countRooms(entries))

    # 12: Average household room area
    indicators.append(countTotalLivingArea(entries) / countRooms(entries))

    # 13: Household population density
    indicators.append(len(entries) / countHouseholds(entries))

    # 14: Avg no. of private/owned households w/ 5 or more rooms
    indicators.append(countPrivateWith5Rooms(entries) / countPrivateHomes(entries))

    # 15: Average room area per person
    indicators.append(countTotalLivingArea(entries) / len(entries))
    ###############

    return indicators

########################################

# All lines from the data file
lines = []
entries_in_bucharest = []
entries_by_pernum = defaultdict(dict)

for m in mapTypes:
    loadMap(m[0])

if os.path.exists("bucharest_entries.dat"):
    print("Data has been processed, loading .dat")
    entries_in_bucharest = pickle.load(open("bucharest_entries.dat", "rb"))
else:
    print("Loading from IPUMS data")
    with open("ipumsi_00004.dat") as data:
        lines = data.readlines()

    print(f"Data length: {len(lines)}")

    # Create an entry for each data line
    all_people = [createEntry(line) for line in lines]

    print("Created data set. Pulling all in Bucharest...")

    entries_in_bucharest = [p for p in filter(lambda p: p.hasProps({"regnro": "Bucharest"}), all_people)]

    pickle.dump(entries_in_bucharest, open("bucharest_entries.dat", "wb+"))

print("Pulled all Bucharest data. Entering interactive terminal to check different parameters for those in Bucharest")
print(f"Entries in bucharest: {len(entries_in_bucharest)}")

# Create dict indexed by pernum, for speedy lookups when connecting mother and children
for person in entries_in_bucharest:
    entries_by_pernum[person.getProp("pernum")] = person

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
    
#     if val not in maps[var_name].values() and not val == "all":
#         print("Invalid value.")
#         continue

#     if val == "all":
#         print(f"All % for {var_name}:")
#         for v in maps[var_name].values():
#             print(v)
#             matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: v}), entries_in_bucharest)]

#             print(f"\tTotal count: {len(matching_entries)}")
#             print(f"\tTotal percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")
#     else:
#         matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: val}), entries_in_bucharest)]

#         print(f"Total count: {len(matching_entries)}")
#         print(f"Total percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")

with open("indicators.csv", "rw+") as f:
    # For each religion, get their indicators and write to file
    for r in maps["religion"]:
        entries = filter(lambda p: p.getProp("religion") == r, entries_in_bucharest)

        if len(entries) > 0:
            indicators = getIndicators(entries, entries_in_bucharest)
            indicator_str = ",".join(str(i) for i in indicators)
            indicator_str = r + "," + indicator_str + "\n"

            f.write(indicator_str)
            print(f"Got indicators for {r}")
        else:
            print(f"Skipped {r} due to no entries")

    # For each ethnicity, get their indicators and write to file
    for e in maps["ro2011a_ethnic"]:
        entries = filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries_in_bucharest)

        if len(entries) > 0:
            indicators = getIndicators(entries, entries_in_bucharest)
            indicator_str = ",".join(str(i) for i in indicators)
            indicator_str = r + "," + indicator_str + "\n"

            f.write(indicator_str)
            print(f"Got indicators for {e}")
        else:
            print(f"Skipped {e} due to no entries")

print("Wrote to indicators.csv, go see if it worked!")