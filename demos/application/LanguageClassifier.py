from modshogun import MulticlassLibLinear
from numpy import array

import json
import sys
import gzip as gz
import pickle as pkl

default_filepath = "data/lang_detection/default.svm.gz"

id_to_lang = {0 : "English", 1 : "Greek", 2 : "German",
				3 : "Spanish", 4 : "Italian"}

class LanguageClassifier:
	def __init__(self):
		self.svm = None

	def load_classifier(self):
		gz_stream = gz.open(default_filepath, 'rb')
		self.svm = pkl.load(gz_stream)
		gz_stream.close()

	def load_svm(self, filepath):
		from modshogun import SerializableAsciiFile
	
		print("Attempting to load a multiclass liblinear svm from \"" +
					filepath +"\"")	
		self.svm = MulticlassLibLinear()
		loader = SerializableAsciiFile(filepath, "r")
		self.svm.load_serializable(loader)
		print("Svm succesfully loaded")


	def classify_doc(self, doc):
		from modshogun import StringCharFeatures, RAWBYTE
		from modshogun import HashedDocDotFeatures
		from modshogun import NGramTokenizer
		from modshogun import MulticlassLabels
	
		docs = [doc]
		string_feats = StringCharFeatures(docs, RAWBYTE)
		tokenizer = NGramTokenizer(4)
		normalize = True
		num_bits = 18
	
		hashed_doc_feats = HashedDocDotFeatures(num_bits, string_feats,
					tokenizer, normalize, 3, 2)
		
		labels = self.svm.apply(hashed_doc_feats).get_labels()
	
		return id_to_lang[labels[0]]

if __name__=='__main__':
	lc = LanguageClassifier()
	if len(sys.argv)==1:
		lc.load_classifier()
	else:
		lc.load_svm(sys.argv[1])
	
	while True:
		print("Enter a sentence to classify or type \"!quit\" to quit")
		sentence = raw_input()
		if sentence=='!quit':
			break
 
		lang = lc.classify_doc(sentence) 
		print("Your sentence \"" + sentence +"\" was classified as : " + lang)
