from shogun import RealFeatures, MulticlassLabels
from shogun import GaussianKernel
from shogun import GMNPSVM

import numpy as np
import gzip as gz
import pickle as pkl

TRAIN_SVM_FNAME_GZ = "data/ocr/ocr.svm.gz"

NEAR_ZERO_POS = 1e-8
NEAR_ONE_NEG = 1-NEAR_ZERO_POS

TRAIN_X_FNAME = "data/train_data_x.asc.gz"
TRAIN_Y_FNAME = "data/train_data_y.asc.gz"

MATIX_IMAGE_SIZE = 16
FEATURE_DIM = MATIX_IMAGE_SIZE * MATIX_IMAGE_SIZE

HISTORY_WIDTH = 5
HISTORY_HEIGHT = 2

FEATURE_RANGE_MAX = 1.0


class Ai:
    def __init__(self):
        self.x = None
        self.y = None

        self.x_test = None
        self.y_test = None

        self.svm = None

    def load_train_data(self, x_fname, y_fname):
        Ai.__init__(self)

        self.x = np.loadtxt(x_fname)
        self.y = np.loadtxt(y_fname) - 1.0

        self.x_test = self.x
        self.y_test = self.y

    def _svm_new(self, kernel_width, c, epsilon):
        if self.x == None or self.y == None:
            raise Exception("No training data loaded.")

        x = RealFeatures(self.x)
        y = MulticlassLabels(self.y)

        self.svm = GMNPSVM(c, GaussianKernel(x, x, kernel_width), y)
        self.svm.set_epsilon(epsilon)

    def write_classifier(self, fname=TRAIN_SVM_FNAME_GZ):
        gz_stream = gz.open(fname, 'wb', 9)
        pkl.dump(self.svm, gz_stream)
        gz_stream.close()

    def read_classifier(self, fname=TRAIN_SVM_FNAME_GZ):
        with gz.open(fname, 'rb') as gz_stream:
            try:
                self.svm = pkl.load(gz_stream)
            except ImportError as error:
                print("error loading model %s" % fname)
            except Exception as exception:
                print("error loading model %s" % fname)

    def enable_validation(self, train_frac):
        x = self.x
        y = self.y

        idx = np.arange(len(y))
        np.random.shuffle(idx)
        train_idx=idx[:np.floor(train_frac*len(y))]
        test_idx=idx[np.ceil(train_frac*len(y)):]

        self.x = x[:,train_idx]
        self.y = y[train_idx]
        self.x_test = x[:,test_idx]
        self.y_test = y[test_idx]

    def train(self, kernel_width, c, epsilon):
        self._svm_new(kernel_width, c, epsilon)

        x = RealFeatures(self.x)
        self.svm.io.enable_progress()
        self.svm.train(x)
        self.svm.io.disable_progress()

    def classify(self, matrix):
        cl = self.svm.apply(
            RealFeatures(
                np.reshape(matrix, newshape=(FEATURE_DIM, 1),
                           order='F')
                )
            ).get_label(0)

        return int(cl + 1.0) % 10

    def get_test_error(self):
        self.svm.io.enable_progress()
        l = self.svm.apply(RealFeatures(self.x_test)).get_labels()
        self.svm.io.disable_progress()

        return 1.0 - np.mean(l == self.y_test)
