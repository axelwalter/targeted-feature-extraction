from pyopenms import *
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt 

def extractFolderFromLibrary(path,libraryPath,
                mz_window = 20,
                peak_width = 60,
                n_isotopes = 2,
                minFeatureQuality = 1):

    featureDetectionDir = os.path.join(path,"FeatureDetection")
    featureXMLDir = os.path.join(featureDetectionDir,"featureXML")
    jsonDir = os.path.join(featureDetectionDir,"json")
    figureDir = os.path.join(featureDetectionDir,"figures")
    if not os.path.isdir(featureDetectionDir):
        os.mkdir(featureDetectionDir)
    if not os.path.isdir(featureXMLDir):
        os.mkdir(featureXMLDir)
    if not os.path.isdir(jsonDir):
        os.mkdir(jsonDir)
    if not os.path.isdir(figureDir):
        os.mkdir(figureDir)

    for filename in os.listdir(path):
        if filename.endswith(".mzML"):
            basename = filename.split(".")[0]
            featureXMLPath = os.path.join(featureXMLDir,basename+".featureXML")
            jsonPath = os.path.join(jsonDir,basename+".json")
            featureFinderMetaboIdent(os.path.join(path,basename+".mzML"),featureXMLPath,libraryPath,mz_window=mz_window,peak_width=peak_width,n_isotopes=n_isotopes)
            try:
                featureXML_to_json(featureXMLPath,jsonPath,minFeatureQuality=minFeatureQuality)

                with open(jsonPath) as json_file:
                    data = json.load(json_file)

                for name, values in data.items():
                    for n_isotopes, chrom in values["isotopes"].items():
                        if n_isotopes == "1":
                            plt.plot(chrom["rt"],chrom["intensity"],label=name)
                plt.title("{}\nmz_window={} peak_width={}\nn_isotopes={} minFeatureQuality={}".format(basename,mz_window,peak_width,n_isotopes,minFeatureQuality))
                plt.legend(loc=9,ncol=2)
                plt.ticklabel_format(axis="y",style="sci",scilimits=(0,0),useMathText=True)

                figPath = os.path.join(figureDir,basename+".png")
                while os.path.exists(figPath):
                    figPath = figPath[:-4]+"x.png"
                plt.tight_layout()
                plt.savefig(figPath,dpi = 100,format="png")
                plt.clf()
            except RuntimeError:
                print("FeatureFinderMetobolite crashed, no featureXML file created.")

def extractFolder(path,massTablePath,
                mz_window = 20,
                peak_width = 60,
                n_isotopes = 2,
                minFeatureQuality = 1,
                charge = 1,
                columnName = "C18"):
    featureDetectionDir = os.path.join(path,"FeatureDetection")
    featureXMLDir = os.path.join(featureDetectionDir,"featureXML")
    jsonDir = os.path.join(featureDetectionDir,"json")
    figureDir = os.path.join(featureDetectionDir,"figures")
    if not os.path.isdir(featureDetectionDir):
        os.mkdir(featureDetectionDir)
    if not os.path.isdir(featureXMLDir):
        os.mkdir(featureXMLDir)
    if not os.path.isdir(jsonDir):
        os.mkdir(jsonDir)
    if not os.path.isdir(figureDir):
        os.mkdir(figureDir)
    
    libraryPath = os.path.join(featureDetectionDir,"library.tsv")

    csv_to_lib(massTablePath,libraryPath,z=charge,column=columnName)

    for filename in os.listdir(path):
        if filename.endswith(".mzML"):
            basename = filename.split(".")[0]
            featureXMLPath = os.path.join(featureXMLDir,basename+".featureXML")
            jsonPath = os.path.join(jsonDir,basename+".json")
            featureFinderMetaboIdent(os.path.join(path,basename+".mzML"),featureXMLPath,libraryPath,mz_window=mz_window,peak_width=peak_width,n_isotopes=n_isotopes)
            try:
                featureXML_to_json(featureXMLPath,jsonPath,minFeatureQuality=minFeatureQuality)

                with open(jsonPath) as json_file:
                    data = json.load(json_file)

                for name, values in data.items():
                    for n_isotopes, chrom in values["isotopes"].items():
                        if n_isotopes == "1":
                            plt.plot(chrom["rt"],chrom["intensity"],label=name)
                plt.title("{}\nmz_window={} peak_width={}\nn_isotopes={} minFeatureQuality={}".format(basename,mz_window,peak_width,n_isotopes,minFeatureQuality))
                plt.legend(loc=9,ncol=2)
                plt.ticklabel_format(axis="y",style="sci",scilimits=(0,0),useMathText=True)

                figPath = os.path.join(figureDir,basename+".png")
                while os.path.exists(figPath):
                    figPath = figPath[:-4]+"x.png"
                plt.tight_layout()
                plt.savefig(figPath,dpi = 100,format="png")
                plt.clf()
            except RuntimeError:
                print("FeatureFinderMetobolite crashed, no featureXML file created.")

def csv_to_lib(csv,library,z=1,column="C18"):
    inputFile = csv

    df = pd.read_csv(inputFile)
    lib = pd.DataFrame()
    df.dropna()

    compoundNames = []
    sumFormulas = []
    masses = []
    charges = []
    retentionTimes = []
    retentionTimeRanges = []
    IsoDistributions = []

    for _,row in df.iterrows():
        if not isinstance(row["compound"], float) and row[column+"#####yes"] != "":
            compoundNames.append(row["name"])
            sumFormulas.append(row["compound"])
            masses.append(0)
            charges.append(str(z))
            retentionTimes.append(str(row[column+"#####yes"]).replace("-",","))
            retentionTimeRanges.append(0)
            IsoDistributions.append(0)

    lib["CompoundName"] = compoundNames
    lib["SumFormula"] = sumFormulas
    lib["Mass"] = masses
    lib["Charge"] = charges
    lib["RetentionTime"] = retentionTimes
    lib["RetentionTimeRange"] = retentionTimeRanges
    lib["IsoDistribution"] =  IsoDistributions

    lib.to_csv(library, sep="\t", index=False)

def featureFinderMetaboIdent(mzML, featureXML, library, n_isotopes = 2, mz_window = 10, peak_width = 60):
    
    args = ["FeatureFinderMetaboIdent","-in",mzML,"-out",featureXML,"-id",library,
            "-extract:mz_window",str(mz_window),"-extract:n_isotopes",str(n_isotopes),
            "-detect:peak_width",str(peak_width)]
    subprocess.call(args)

def featureXML_to_json(featureXML, jsonFileName = None, minFeatureQuality = 1, roundMassBy = 4):
    features = FeatureMap()
    features.setUniqueIds()
    fh = FeatureXMLFile()
    fh.load(featureXML, features)
    out = {}
    for f in features:
        if f.getOverallQuality() > minFeatureQuality:
            name = f.getMetaValue("label")
            area_all_isotopes = 0
            
            if name in out:
                for i in range(1, len(out[name])):
                    intensities = [int(x[1]) for x in f.getSubordinates()[i-1].getConvexHulls()[0].getHullPoints()]
                    out[name]["isotopes"][i]["intensity"] += intensities
                    out[name]["isotopes"][i]["rt"] += [x[0] for x in f.getSubordinates()[i-1].getConvexHulls()[0].getHullPoints()]
                    out[name]["isotopes"][i]["area"] += sum(intensities)
                    
            else:
                out[name] = {}
                out[name]["isotopes"] = {}
                masses = f.getMetaValue("masserror_ppm")[::2]
                for i in range(1, len(masses)+1):
                    intensities = [int(x[1]) for x in f.getSubordinates()[i-1].getConvexHulls()[0].getHullPoints()]
                    out[name]["isotopes"][i] = {"mass": round(masses[i-1], roundMassBy),
                                        "intensity": intensities,
                                        "rt": [x[0]/60 for x in f.getSubordinates()[i-1].getConvexHulls()[0].getHullPoints()],
                                        "area": sum(intensities)}
            area_all_isotopes += sum(intensities)
            out[name]["areaAllIsotopes"] = area_all_isotopes

    if jsonFileName:
        with open(jsonFileName, "w") as f:
            json.dump(out, f, indent = 4)
    else:
        return out

def json_to_dict(jsonFileName):
    with open(jsonFileName,"r") as f:
        data = json.load(f)
    return data