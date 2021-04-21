# Helper class to load in different kinds of 
class DataLoader():
	def __init__(self):
		pass

	@classmethod
	def loadData(self, filename):
		pass

	@classmethod
	def loadMaps(self, mapTypes):
		maps = {}

		for mapType in mapTypes:
			# If it is serial, it does not have a lookup table. Otherwise, pull its lookup table, and load it into the `maps` variable
			if not mapType[0] in ["serial", "pernum", "momloc", "hrsmain"]:
				with open("./maps/" + mapType[0] + "_map.txt") as f:
					mappings = f.readlines()
					mappings = [m.split("\t\t") for m in mappings]
					mappings = [[m[0],  m[1].strip("\n")] for m in mappings]

					thisMap = {}
					
					for (k,v) in mappings:
						thisMap.setdefault(k,v)
					
					maps.setdefault(mapType[0], thisMap)
		
		return maps