class Indicators:
	def __init__(self):
		pass

	# Helper fn: Returns all unique household entries.
	@classmethod
	def getUniqueHouseholds(cls, entries):
		serials = set()
		households = []
		
		for e in entries:
			if e.getProp("serial") not in serials:
				serials.add(e.getProp("serial"))
				households.append(e)

		return households

	# Return number of unique SERIAL values
	@classmethod
	def countHouseholds(cls, entries):
		# This is supposedly best practice, but is probably ridiculously slow
		households = Indicators.getUniqueHouseholds(entries)
		return len(households)

	# Return count of entries with age < 18
	@classmethod
	def countChildren(cls, entries):
		children = list(filter(lambda p: int(p.getProp("age")) < 18, entries))

		return len(children)

	# Return count of women
	@classmethod
	def countWomen(cls, entries):
		women = list(filter(lambda p: p.hasProps({"sex": "Female"}), entries))

		return len(women)

	# Return count of men
	@classmethod
	def countMen(cls, entries):
		men = list(filter(lambda p: p.hasProps({"sex": "Male"}), entries_in_bucharest))

		return len(men)

	# Return count of women with 3 or more children
	@classmethod
	def countWomenWith3Children(cls, entries):
		womenWithManyChildren = list(filter(lambda p: int(p.getProp("chborn")) > 2, entries))

		return len(womenWithManyChildren)

	# Count the number of women who were 15 or older when they had a child
	# ASSUMPTION: If any child was had before 15, they are disqualified (not part of the total)
	@classmethod
	def countWomen15OlderWithChild(cls, all, entries):
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
	@classmethod
	def countWithMinimumEducation(cls, entries):
		minEducation = list(filter(lambda p: p.getProp("educro") in ["Primary", "Literacy Courses"], entries))
		
		return len(minEducation)

	# Count the number of entries who are over 10 years old
	@classmethod
	def countAgeOver10(cls, entries):
		overTen = list(filter(lambda p: int(p.getProp("age")) > 10, entries))

		return len(overTen)

	# Count the total size of buildings in square meters
	@classmethod
	def countTotalLivingArea(cls, entries):
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
	# ASSUMPTIONS: If not eempstat == Employed, they are not employed
	#              (NIU, Unemployed, not economically active are all not employed)
	#              Younger than 18 and older than 60 do not count towards unemployment
	@classmethod
	def countUnemployed(cls, entries):
		unemployed = list(filter(lambda p: not p.getProp("eempstat") == "Employed" and 18 < int(p.getProp("age")) < 60, entries))

		return len(unemployed)

	# Count the total number of rooms across households
	@classmethod
	def countRooms(cls, entries):
		rooms = 0

		# Get each unique household
		households = getUniqueHouseholds(entries)

		for e in households:
			rooms += int(e.getProp("rooms"))

		return rooms

	# Count the number of privately owned households
	@classmethod
	def countPrivateHomes(cls, entries):
		households = getUniqueHouseholds(entries)

		private = list(filter(lambda h: h.getProp("ownership") == "Owned", households))

		return len(private)

	# Count the number of privately owned households with 5+ rooms
	@classmethod
	def countPrivateWith5Rooms(cls, entries):
		households = getUniqueHouseholds(entries)

		large_households = list(filter(lambda h: h.getProp("ownership") == "Owned" and int(h.getProp("rooms")) > 4, entries))

		return len(large_households)

	# Count the number of economically active individuals
	# ASSUMPTION: Employed in EEMPSTAT is the only qualifier
	#             This matches with how the unemployed and economically active variables are used in the Armas report
	@classmethod
	def countEconomicallyActive(cls, entries):
		return len(list(filter(lambda e: e.getProp("eempstat") == "Employed", entries)))

	# Count the number of socially dependand individuals
	# ASSUMPTION: Anyone younger than 12 or older than 80 are socially dependant. We could not find any discrete definitions
	#             of how this value should be calculated, from either the Armas report or independent research. This is
	#             as close to arbitrary as you can get.
	@classmethod
	def countSociallyDependant(cls, entries):
		young = list(filter(lambda e: int(e.getProp("age")) < 12, entries))
		old   = list(filter(lambda e: int(e.getProp("age")) > 80, entries))

		return len(young) + len(old)

	# Count the number of individuals over 65 years old
	@classmethod
	def countElderly(cls, entries):
		return len(list(filter(lambda e: int(e.getProp("age")) > 65, entries)))

	# Count the number of high income earners
	@classmethod
	def countHighIncomeMen(cls, entries):
		high = list(filter(lambda p: int(p.getProp("income")) > HIGH_SALARY and p.getProp("sex") == "Male", entries))

		return len(high)

	@classmethod
	def countHighIncomeWomen(cls, entries):
		high = list(filter(lambda p: int(p.getProp("income")) > HIGH_SALARY and p.getProp("sex") == "Female", entries))

		return len(high)

	# Count the number of low income earners
	@classmethod
	def countLowIncome(cls, entries):
		low = list(filter(lambda p: int(p.getProp("income")) < LOW_SALARY, entries))

		return len(low)

	# Count the number of widows
	@classmethod
	def countWidows(cls, entries):
		widows = list(filter(lambda p: p.getProp("marst") == "Widowed", entries))

		return len(widows)