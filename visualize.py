from entry import Entry
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

def getNumericHistogramVariable(entries, variable):
    data = []


    # TODO TODO TODO maybe don't assume int
    for e in entries:
        data.append(int(e.getProp(variable)))

    return data

class Visualizer:
	def __init__(self):
		pass

	@classmethod
	def ageDistribution(cls, entries, ethnicities):
		ages = []
		colors = ["coral", "limegreen", "cornflowerblue", "palegoldenrod"]

		# Age bins. Children, Adult, Elderly
		bins = [1, 18, 65, 100]

		for i,e in enumerate(ethnicities):
			filtered_entries = list(filter(lambda p: p.getProp("ro2011a_ethnic") == e, entries))

			print(e)
			print(len(filtered_entries))

			# Get age data
			ages.append(getNumericHistogramVariable(filtered_entries, "age"))

		percents = []

		for age in ages:
			sum_children = len([x for x in age if x < 18])
			sum_adults = len([x for x in age if 18 <= x < 65])
			sum_elderly = len([x for x in age if x >= 65])

			percents.append([sum_children/len(age), sum_adults/len(age), sum_elderly/len(age)])

		categories = ["Children (<18)", "Adults (18-65)", "Elderly (>65)"]

		X = np.arange(len(categories))

		width = 0.8

		for i in range(len(ethnicities)):
			offset = X - width/2. + i/float(len(ethnicities)) * width

			plt.bar(offset, percents[i], color=colors[i], width=width/float(len(ethnicities)), align="edge")

		plt.xticks(X, categories)

		plt.legend(ethnicities)

		plt.ylabel("Percentage of population")
		plt.title("Age distribution of demographics")

		plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
		plt.show()