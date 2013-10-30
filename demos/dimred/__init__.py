import modshogun as sg
import numpy as np
import difflib
import settings

#prepare the dataset for tapkee word
words = []
with open(settings.TAPKEE_WORD_FNAME) as f:
    words.extend([str.rstrip() for str in f.readlines()])
N = len(words)
dist_matrix = np.zeros([N,N])
for i in xrange(N):
    for j in xrange(i,N):
        s = difflib.SequenceMatcher(None, words[i], words[j])
        dist_matrix[i,j] = s.ratio()
dist_matrix = 0.5*(dist_matrix+dist_matrix.T)
word_kernel = sg.CustomKernel(dist_matrix)

#prepare the dataset for tapkee promotion
strings = []
with open(settings.TAPKEE_MML_FNAME) as f:
    strings = [s.rstrip() for s in f.readlines()]
