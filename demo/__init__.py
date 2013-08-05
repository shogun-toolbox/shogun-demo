from Ai import Ai
ai = Ai()
ai.load_classifier()

filename = "data/tapkee/words.dat"
words = []
with open(filename) as f:
    words.extend([str.rstrip() for str in f.readlines()])

filename = "data/tapkee/mml.txt"
strings = []
with open(filename) as f:
    strings = [s.rstrip() for s in f.readlines()]
