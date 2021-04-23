from collections import defaultdict

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

	# Creates an Entry object from a line in the data file
	@classmethod
	def createEntry(cls, line, mapTypes, maps):
		props = defaultdict(dict)
		for m in mapTypes:
			# Skip over all variables that do not have a lookup table
			if m[0] in ["serial", "pernum", "momloc", "hrsmain"]:

				# Need to set 998 and 999 to 0, not that many hours
				if m[0] == "hrsmain":
					val = line[m[1]:m[2]]

					if int(val) > 150:
						val = 0

					props[m[0]] = val
				else:
					props[m[0]] = line[m[1]:m[2]]
			# All others, except income (not in dataset) have a map lookup
			elif not m[0] == "income":
				props[m[0]] = maps[m[0]][line[m[1]:m[2]]]

		entry = Entry(props)

		# Get salary by indgen (reduce to salary/hr from salary/mo)
		# ASSUMPTION: 40 hrs/wk
		salary_mo = int(maps["income"][entry.getProp("indgen")])
		salary_hr = salary_mo / 4.3424 / 40

		# Get hours by hrsmain
		hours = int(entry.getProp("hrsmain"))

		# Multiply together, convert hrs/wk to hrs/yr (* ~52), set to entry["income"]
		entry.props["income"] = salary_hr * hours * 52.149

		return entry

	def __repr__(self):
		out = "Entry:"

		for k,v in self.props.items():
			out = out + f"\n\t{k}:\t{v}"

		return out