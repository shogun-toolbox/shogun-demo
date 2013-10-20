from Ai import Ai
from LanguageClassifier import LanguageClassifier
import settings

ai = Ai()
ai.read_classifier(settings.OCR_DATA_FNAME_GZ)

lc = LanguageClassifier()
lc.load_classifier(settings.LC_DATA_FNAME_GZ)
