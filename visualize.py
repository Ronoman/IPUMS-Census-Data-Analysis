from entry import Entry
from indicators import Indicators

import numpy as np
import itertools

from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

def getNumericHistogramVariable(entries, variable):
    data = []


    # TODO TODO TODO maybe don't assume int
    for e in entries:
        data.append(int(e.getProp(variable)))

    return data

def getAlphanumericHistogramVariable(entries, variable):
	data = []


	# TODO TODO TODO maybe don't assume int
	for e in entries:
		data.append(e.getProp(variable))

	return data

class Visualizer:
	def __init__(self):
		pass

	@classmethod
	def ageDistribution(cls, entries, ethnicities):
		ages = []
		colors = ["plum", "limegreen", "cornflowerblue", "palegoldenrod", "mediumvioletred"]

		# Age bins. Children, Adult, Elderly
		bins = [1, 18, 65, 100]

		for i,e in enumerate(ethnicities):
			var = "ro2011a_ethnic"

			if e == "Muslim":
				var = "religion"

			filtered_entries = list(filter(lambda p: p.getProp(var) == e, entries))
			print(len(filtered_entries))

			# Get age data
			ages.append(getNumericHistogramVariable(filtered_entries, "age"))

		percents = []

		for i,age in enumerate(ages):
			print(ethnicities[i])
			sum_children = len([x for x in age if x < 18])
			sum_adults = len([x for x in age if 18 <= x < 65])
			sum_elderly = len([x for x in age if x >= 65])

			print(f"Children: {sum_children/len(age)}\nAdults: {sum_adults/len(age)}\nElderly: {sum_elderly/len(age)}")

			percents.append([sum_children/len(age), sum_adults/len(age), sum_elderly/len(age)])

		categories = ["Children (<18)", "Adults (18-65)", "Elderly (>65)"]

		X = np.arange(len(categories))

		width = 0.8

		for i in range(len(ethnicities)):
			offset = X - width/2. + i/float(len(ethnicities)) * width

			plt.bar(offset, percents[i], color=colors[i], width=width/float(len(ethnicities)), align="edge", zorder=3)

		plt.xticks(X, categories)

		plt.legend([e + f" (n={len(ages[i])})" for i,e in enumerate(ethnicities)])

		plt.ylabel("Percentage of Population")
		plt.title("Age Distribution of Young and Old Demographics, Compared to Romanians")

		plt.grid()

		plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
		plt.show()

	@classmethod
	def ethnicDistribution(cls, entries, maps):
		pass

	# Display the top n unemployment rates
	@classmethod
	def unemploymentChart(cls, entries, maps, n):
		# Dict to store all {ethnicity/religion: unemployment_rate} pairs
		unemployment_stratified = {}

		# For each religion and ethnicity, if there are 20 or more entries, calculate that group's unemployment rate
		for r in maps["religion"].values():
			these_entries = list(filter(lambda e: e.getProp("religion") == r, entries))

			if len(these_entries) > 20:
				unemployment = Indicators.countUnemployed(these_entries) / len(these_entries)

				unemployment_stratified[r] = unemployment
		for e in maps["ro2011a_ethnic"].values():
			these_entries = list(filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries))

			if len(these_entries) > 20:
				unemployment = Indicators.countUnemployed(these_entries) / len(these_entries)

				unemployment_stratified[e] = unemployment

		# Sort the dict by highest unemployment rate
		sorted_unemployment = {k: v for k, v in sorted(unemployment_stratified.items(), key=lambda x: -x[1])}

		# Remove Romanian, since we want top 4 excluding Romanian
		romanian = sorted_unemployment.pop("Romanian", None)
		
		# Grab the top five unemployment rates
		top_five = {}
		for k,v in list(sorted_unemployment.items())[:n-1]:
			top_five[k] = v

		# Add Romanian back in, and sort the dict and put it back in sorted_unemployment
		top_five["Romanian"] = romanian
		sorted_unemployment = {k: v for k, v in sorted(top_five.items(), key=lambda x: -x[1])}

		print(sorted_unemployment)

		categories = list(sorted_unemployment.keys())
		values = sorted_unemployment.values()

		print(categories)

		Y = np.arange(len(categories))

		plt.barh(Y, values, align="center", zorder=3)
		plt.yticks(Y, categories)
		plt.gca().invert_yaxis()
		plt.xlabel("Unemployment rate (18 < age < 60)")

		plt.title(f"Top {n-1} Unemployment Rates, Compared to Romanians")

		plt.grid()

		plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
		plt.tight_layout()

		plt.show()

	@classmethod
	def incomeDistribution(cls, entries):
		entries = filter(lambda p: p.getProp("ro2011a_ethnic") == "Romanian", entries)

		incomes = [income for income in getNumericHistogramVariable(entries, "income") if not income == 0]

		plt.hist(incomes, bins=25, color="royalblue")
		plt.title("Income Distribution for Romanians")
		plt.ylabel("Count")
		plt.xlabel("Income (lei/yr)")
		plt.gca().ticklabel_format(useOffset=False, style="plain")
		plt.show()
	
	@classmethod
	def educationDistribution(cls, entries, ethnicities):
		educations = []
		colors = ["plum", "limegreen", "cornflowerblue", "palegoldenrod", "mediumvioletred"]

		for i,e in enumerate(ethnicities):
			var = "ro2011a_ethnic"

			if e in ["Unknown religion", "Muslim"]:
				var = "religion"

			filtered_entries = list(filter(lambda p: p.getProp(var) == e, entries))
			print(len(filtered_entries))

			# Get education data
			educations.append(getAlphanumericHistogramVariable(filtered_entries, "educro"))

		percents = []

		for ed in educations:
			sum_none = len([x for x in ed if x == "None"])
			sum_primary = len([x for x in ed if x in ["Primary", "Literacy courses"]])
			sum_secondary = len([x for x in ed if x == "Secondary"])
			sum_post = len([x for x in ed if x == "Post-secondary"])

			percents.append([sum_none/len(ed), sum_primary/len(ed), sum_secondary/len(ed), sum_post/len(ed)])

		categories = ["No education", "Primary", "Secondary", "Post-secondary"]

		X = np.arange(len(categories))

		width = 0.8

		for i in range(len(ethnicities)):
			offset = X - width/2. + i/float(len(ethnicities)) * width

			plt.bar(offset, percents[i], color=colors[i], width=width/float(len(ethnicities)), align="edge", zorder=3)

		plt.xticks(X, categories)

		plt.legend([e + f" (n={len(educations[i])})" for i,e in enumerate(ethnicities)])

		plt.ylabel("Percentage of Population")
		plt.xlabel("Level of Education Attained")
		plt.title("Education Attained by Low Education Demographics, Compared to Romanians")

		plt.grid()

		plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
		plt.show()

	# Display the top n population densities
	@classmethod
	def densityChart(cls, entries, maps, n):
		# Dict to store all {ethnicity/religion: population_density} pairs
		density_stratified = {}

		# For each religion and ethnicity, if there are 20 or more entries, calculate that group's pop density
		for r in maps["religion"].values():
			these_entries = list(filter(lambda e: e.getProp("religion") == r, entries))

			if len(these_entries) > 20:
				pop_density = len(these_entries) / Indicators.countHouseholds(these_entries)

				density_stratified[r] = pop_density
		for e in maps["ro2011a_ethnic"].values():
			these_entries = list(filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries))

			if len(these_entries) > 20:
				pop_density = len(these_entries) / Indicators.countHouseholds(these_entries)

				density_stratified[e] = pop_density

		# Sort the dict by highest pop density
		sorted_density = {k: v for k, v in sorted(density_stratified.items(), key=lambda x: -x[1])}

		# Remove Romanian, since we want top 4 excluding Romanian
		romanian = sorted_density.pop("Romanian", None)
		
		# Grab the top n-1 unemployment rates
		top_five = {}
		for k,v in list(sorted_density.items())[:n-1]:
			top_five[k] = v

		# Add Romanian back in, and sort the dict and put it back in sorted_density
		top_five["Romanian"] = romanian
		sorted_density = {k: v for k, v in sorted(top_five.items(), key=lambda x: -x[1])}

		print(sorted_density)

		categories = list(sorted_density.keys())
		values = sorted_density.values()

		print(categories)

		Y = np.arange(len(categories))

		plt.barh(Y, values, align="center", zorder=3)
		plt.yticks(Y, categories)
		plt.gca().invert_yaxis()
		plt.xlabel("Average People per Household (people/households)")

		plt.title(f"Highest People per Household")

		plt.grid()

		plt.tight_layout()

		plt.show()

	@classmethod
	def popChart(cls, entries, maps, category="ethnicity"):
		# Dict to store all {ethnicity/religion: len(pop)} pairs
		population_stratified = {}

		# For each religion and ethnicity, if there are 20 or more entries, calculate that group's pop density
		if category == "religion":
			for r in maps["religion"].values():
				these_entries = list(filter(lambda e: e.getProp("religion") == r, entries))

				if len(these_entries) > 20:
					population_stratified[r] = len(these_entries)
		elif category == "ethnicity":
			for e in maps["ro2011a_ethnic"].values():
				these_entries = list(filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries))

				if len(these_entries) > 20:
					population_stratified[e] = len(these_entries)
		else:
			print("popChart called, but category was not religion or ethnicity")

		# Sort the dict by highest pop density
		sorted_pop = {k: v for k, v in sorted(population_stratified.items(), key=lambda x: -x[1])}

		# Remove Romanian and Eastern orthodox
		sorted_pop.pop("Romanian", None)
		sorted_pop.pop("Unknown ethnicity", None)
		sorted_pop.pop("Christian", None)

		# Sort the dict and put it back in sorted_pop

		sorted_pop = {k: v for k, v in sorted(sorted_pop.items(), key=lambda x: -x[1])}

		print(sorted_pop)

		categories = list(sorted_pop.keys())
		values = sorted_pop.values()

		print(categories)

		Y = np.arange(len(categories))

		plt.barh(Y, values, align="center", zorder=3)
		plt.yticks(Y, categories)
		plt.gca().invert_yaxis()
		plt.xlabel("Population")

		plt.title(f"{category.capitalize()} Population Distribution in Census Data")

		plt.grid()

		plt.tight_layout()

		plt.show()