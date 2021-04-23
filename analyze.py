import pickle, os, math
from collections import defaultdict

# Local libraries, used so that this file isn't a million lines long
from loader import DataLoader
from entry import Entry
from visualize import Visualizer
from indicators import Indicators

# Completely arbitrary, will be decided based on real info soon
LOW_SALARY = 20000
HIGH_SALARY = 60000

# List of all maps between number and data
# Each key is one of the first elements in each mapTypes list
# Each value is a dict, which maps numbers (keys) to their human-readable value
maps = {}

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
            ["hrsmain", 99, 102],
            ["ro2011a_ethnic", 102, 104],
            ["income"]]

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

# See indicators.py

########################################

########################################
#        INDICATOR PROCESSING          #
########################################

# indicatorMap = {"elderly": 0,
#                 "female": 1,
#                 "children": 2,
#                 "widows": 3,
#                 "wage_earners": 4,
#                 "minimum_education": 5,
#                 "women_with_3_children": 6,
#                 "unemployed": 7,
#                 ""}

def getIndicators(entries, all):
    indicators = []

    ### SOCIAL ###
    # 0: Ratio elderly
    indicators.append(Indicators.countElderly(entries) / len(entries))

    # 1: Ratio female
    indicators.append(Indicators.countWomen(entries) / len(entries))

    # 2: Ratio children
    indicators.append(Indicators.countChildren(entries) / len(entries))

    # 3: Ratio widows in female population
    indicators.append(Indicators.countWidows(entries) / Indicators.countWomen(entries))

    # Skipped housing density, since it is 1/avg room area per person from our calculations

    # 4: Average wage earners per household
    indicators.append(Indicators.countEconomicallyActive(entries) / Indicators.countHouseholds(entries))

    # 5: Minimum level of education
    indicators.append(Indicators.countWithMinimumEducation(entries) / len(entries))

    # 6: Ratio of women with 3 children and more to women
    # In some reports it is 3, others 5. Chose 3 here, but can be changed (pass in as parameter?)
    indicators.append(Indicators.countWomenWith3Children(entries) / Indicators.countWomen(entries))
    ##############

    ### ECONOMIC ###
    # 7: Ratio of unemployed
    indicators.append(Indicators.countUnemployed(entries) / len(entries))

    # 8: Ratio of low income
    indicators.append(Indicators.countLowIncome(entries) / len(entries))

    # 9: Ratio of high income women
    indicators.append(Indicators.countHighIncomeWomen(entries) / Indicators.countWomen(entries))

    # 10: Ratio of high income men
    indicators.append(Indicators.countHighIncomeMen(entries) / Indicators.countMen(entries))
    ################

    ### HOUSING ###
    # 11: Room occupancy per household
    indicators.append(len(entries) / Indicators.countRooms(entries))

    # 12: Average household room area
    indicators.append(Indicators.countTotalLivingArea(entries) / Indicators.countRooms(entries))

    # 13: Household population density
    indicators.append(len(entries) / Indicators.countHouseholds(entries))

    # 14: Avg no. of private/owned households w/ 5 or more rooms
    indicators.append(Indicators.countPrivateWith5Rooms(entries) / Indicators.countPrivateHomes(entries))

    # 15: Average room area per person
    indicators.append(Indicators.countTotalLivingArea(entries) / len(entries))
    ###############

    return indicators

########################################

########################################
###         INTERFACE MODES          ###
########################################

# Run armas analysis and save data to indicators.csv
def analyze():
    with open("indicators.csv", "w") as f:
        print(maps["religion"])

        cols = ["", "Count", "Ratio elderly", "Ratio female", "Ratio children", "Ratio widows in female population", "Average wage earners per household", 
        "Minimum level of education", "Ratio of women with 3 children and more to women", "Ratio of unemployed", "Ratio of low income", "Ratio of high income women",
        "Ratio of high income men", "Room occupancy per household", "Average household room area", "Household population density", "Avg no. of private/owned households w/ 5 or more rooms",
        "Average room area per person"]

        f.write(",".join(cols) + "\n")

        # For each religion, get their indicators and write to file
        for _,r in maps["religion"].items():
            entries = list(filter(lambda p: p.getProp("religion") == r, entries_in_bucharest))

            if len(entries) > 20:
                indicators = getIndicators(entries, entries_in_bucharest)
                indicator_str = ",".join(str(i) for i in indicators)
                indicator_str = r + "," + str(len(entries)) + "," + indicator_str + "\n"

                f.write(indicator_str)
                print(f"Got indicators for {r}")
            else:
                print(f"Skipped {r} due to no entries")

        # For each ethnicity, get their indicators and write to file
        for _,e in maps["ro2011a_ethnic"].items():
            entries = list(filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries_in_bucharest))

            if len(entries) > 20:
                indicators = getIndicators(entries, entries_in_bucharest)
                indicator_str = ",".join(str(i) for i in indicators)
                indicator_str = e + "," + str(len(entries)) + "," + indicator_str + "\n"

                f.write(indicator_str)
                print(f"Got indicators for {e}")
            else:
                print(f"Skipped {e} due to no entries")

    print("Wrote to indicators.csv, go see if it worked!")

# Run the interactive data explorer
def interactive():
    done = False

    while not done:
        var_name = input("Variable name (? for all, q to quit): ")

        if var_name == "q":
            done = True
            continue

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
        
        if val not in maps[var_name].values() and not val == "all":
            print("Invalid value.")
            continue

        if val == "all":
            print(f"All % for {var_name}:")
            for v in maps[var_name].values():
                print(v)
                matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: v}), entries_in_bucharest)]

                print(f"\tTotal count: {len(matching_entries)}")
                print(f"\tTotal percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")
        else:
            matching_entries = [p for p in filter(lambda p: p.hasProps({var_name: val}), entries_in_bucharest)]

            print(f"Total count: {len(matching_entries)}")
            print(f"Total percent: {len(matching_entries)/len(entries_in_bucharest)*100:.3f}%")

# Run an interactive plotting tool
def graph(entries_in_bucharest):
    done = False

    while not done:
        mode = input("Religion or ethnicity? (r or e, q to quit): ")

        entries = []
        title = ""

        if mode == "q":
            done = True
            continue
        elif mode == "r":
            religion = input("Which religion: ")
            title = religion

            entries = [e for e in entries_in_bucharest if e.getProp("religion") == religion]
        elif mode == "e":
            ethnicity = input("Which ethnicity: ")
            title = ethnicity

            entries = [e for e in entries_in_bucharest if e.getProp("ro2011a_ethnic") == ethnicity]

        if len(entries) == 0:
            print("Invalid identifier, or empty set. Try again.")
            continue

        variable = input("Which variable: ")

        if variable not in [m[0] for m in mapTypes]:
            print("Invalid variable.")
            continue

        if variable == "hrsmain":
            entries = [e for e in entries if e.getProp("eempstat") == "Employed"]

        title += f": {variable} (n={len(entries)})"

        graph_type = input("What type of graph (help for all types): ")

        if graph_type == "help":
            print("Supported types: histogram")
            continue
        elif graph_type == "histogram":
            data = getNumericHistogramVariable(entries, variable)

            plt.hist(data, bins=25, color="royalblue")
            plt.title(title)
            plt.ylabel("Count")
            plt.xlabel(f"{variable.capitalize()}")
            plt.show()
        else:
            print("Invalid graph type.")

def graphAge():
    ethnicities = ["Romanian", "Armenian", "Ukranian"]
    religions = ["Jewish", ""]

########################################

# All lines from the data file
lines = []
entries_in_bucharest = []
all_people = []
entries_by_pernum = defaultdict(dict)

maps = DataLoader.loadMaps(mapTypes)

if os.path.exists("bucharest_entries.dat"):
    print("Data has been processed, loading .dat")
    entries_in_bucharest = pickle.load(open("bucharest_entries.dat", "rb"))
else:
    print("Loading from IPUMS data")
    with open("ipumsi_00006.dat") as data:
        lines = data.readlines()

    print(f"Data length: {len(lines)}")

    # Create an entry for each data line
    all_people = [Entry.createEntry(line, mapTypes, maps) for line in lines]

    print("Created data set. Pulling all in Bucharest...")

    entries_in_bucharest = [p for p in filter(lambda p: p.hasProps({"regnro": "Bucharest"}), all_people)]

    pickle.dump(entries_in_bucharest, open("bucharest_entries.dat", "wb+"))

print("Pulled all Bucharest data. Entering interactive terminal to check different parameters for those in Bucharest")
print(f"Entries in bucharest: {len(entries_in_bucharest)}")

# Create dict indexed by pernum, for speedy lookups when connecting mother and children
for person in entries_in_bucharest:
    entries_by_pernum[person.getProp("pernum")] = person

while True:
    mode = input("What would you like to do? Type `help` for all modes: ")

    if mode == "help":
        print("Different modes: help, analyze, graph, age, interactive")
    elif mode == "analyze":
        analyze()
    elif mode == "graph":
        graph(entries_in_bucharest)
    elif mode == "interactive":
        interactive()
    elif mode == "age":
        Visualizer.ageDistribution(entries_in_bucharest, ["Romanian", "Jewish", "Armenian", "Roma", "Muslim"])
    elif mode == "unemployment":
        Visualizer.unemploymentChart(entries_in_bucharest, maps, 5)
    elif mode == "income":
        Visualizer.incomeDistribution(entries_in_bucharest)
    elif mode == "education":
        Visualizer.educationDistribution(entries_in_bucharest, ["Roma", "Unknown ethnicity", "Aromanian", "Muslim", "Romanian"])
    elif mode == "density":
        Visualizer.densityChart(entries_in_bucharest, maps, 5)
    elif mode == "median":
        print("Calculating income median across the country.")

        print("Extracting incomes")
        incomes = [int(p.getProp("income")) for p in all_people if int(p.getProp("income")) > 0]

        print("Sorting")
        incomes.sort()

        print(f"Median income: {incomes[math.floor(len(incomes)/2)]}")
    elif mode == "ethnicity":
        Visualizer.popChart(entries_in_bucharest, maps)
    elif mode == "religion":
        Visualizer.popChart(entries_in_bucharest, maps, category="religion")
    else:
        print("Try again.")
