from shogun import MulticlassLibLinear
from numpy import array

import json
import sys
import gzip as gz
import pickle as pkl

DEFAULT_FILEPATH = "data/lang_detection/default.svm.gz"

id_to_lang = {0 : "English", 1 : "Greek", 2 : "German",
				3 : "Spanish", 4 : "Italian"}

class LanguageClassifier:
	def __init__(self):
		self.svm = None

	def load_classifier(self, fname=DEFAULT_FILEPATH):
            with gz.open(fname, 'rb') as gz_stream:
                try:
                    self.svm = pkl.load(gz_stream)
                except ImportError as error:
                    print("error loading model %s" % fname)
                except Exception as exception:
                    print("error loading model %s" % fname)

	def load_svm(self, filepath):
		from shogun import SerializableAsciiFile
	
		print("Attempting to load a multiclass liblinear svm from \"" +
					filepath +"\"")	
		self.svm = MulticlassLibLinear()
		loader = SerializableAsciiFile(filepath, "r")
		self.svm.load_serializable(loader)
		print("Svm succesfully loaded")


	def classify_doc(self, doc):
		from shogun import StringCharFeatures, RAWBYTE
		from shogun import HashedDocDotFeatures
		from shogun import NGramTokenizer
		from shogun import MulticlassLabels
	
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
