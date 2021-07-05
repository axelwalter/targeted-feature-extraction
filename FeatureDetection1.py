from featurefunctions import *

# /media/axel/Elements/Simon/SF_P7/SF_P7_MassesMM.csv
# /media/axel/Elements/Simon/SF_P7/20210305_mzML
# /home/axel/Downloads/test_mzML_files/
# /home/axel/OneDrive/projects/FeaturFinder/chitin.csv
inputFolderLocation = "/media/axel/Elements/Simon/SF_P7/20210305_mzML"
massTableLocation = "/media/axel/Elements/Simon/SF_P7/SF_P7_MassesMM.csv"
mz_window = 20
peak_width = 60
n_isotopes = 2
minFeatureQuality = 1
charge = 1
columnName = "C18"

extractFolder(inputFolderLocation,
              massTableLocation,
              mz_window = mz_window,
              peak_width=peak_width,
              n_isotopes = n_isotopes,
              minFeatureQuality = minFeatureQuality,
              charge = charge,
              columnName = columnName
              )
