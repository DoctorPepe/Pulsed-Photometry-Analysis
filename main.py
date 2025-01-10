import tkinter
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import pandas as pd
import PhotometryStruct
from PhotometryStruct import PhotometryData

root = tkinter.Tk()
root.withdraw()

#dictionary of events in Med-Pc timestamp data
eventDict = {"id_sessionStart": 1,
             "id_sessionEnd": 2,
             "id_recordingStart": 5,
             "id_recordingStop": 6}

def getFile():
    try:
        currdir = os.getcwd()
        tempdir = filedialog.askopenfilename(parent=root, initialdir=currdir,
                                             title='Please select photometry data file',
                                             filetypes=[('Excel', '*.xlsx')])
        if len(tempdir) > 0:
            print("You chose: %s" % tempdir)
        else:
            raise Exception("Error: No file was selected")
    except:
        tempdir = getFile()
    return tempdir


def main():
    print("\n==Fiber Photometry Analysis for Pulsed Recordings==")
    print("Note: Currently, this program only accepts Doric Neuroscience Studio v5 type .xlsx files\n")
    #get path to .xlsx file
    fpath = getFile()
    #instantiate data structure
    channel1 = PhotometryStruct.PhotometryData(type="pulsed", id_sessionStart = 1, id_sessionEnd = 2)
    channel1.readData(fpath)
    channel1.clean()
    print("Select a paradigm to analyze (default = 1):")
    print("1. Open Field")
    while True:
        val = input("> ")
        if val == "1":
            choice = 1
            break
        elif val == "":  #default option
            choice = 1
            break
        else:
            print("Incorrect input")

    #normalize and bin data
    channel1.normalize()
    channel1.binData()

    #plot results
    fig, axes = plt.subplots(2,2)
    channel1.cleanedptDf.plot(ax= axes[0,0], x="Time", y=["_465", "_405"], kind="line", figsize=(10, 5))
    axes[0,0].set_title("Raw 405 and 465 Data")
    axes[0,0].set_ylabel("Current")
    channel1.cleanedptDf.plot(ax = axes[0,1], x="Time", y=["norm"], kind="line", figsize=(10, 5))
    axes[0,1].set_title("Normalized 465 Signal")
    axes[0,1].set_ylabel("f/f")
    channel1.binnedPtDf.plot(ax = axes[1,0], x="Time", y=["norm"], kind="line", figsize=(10, 5))
    axes[1,0].set_title("Binned Normalized 465 Signal")
    axes[1,0].set_ylabel("f/f")
    fig.tight_layout()

    #get name of original xlsx file for plot names
    name = fpath.split("/")
    name = name[len(name) - 1].split(".")
    name = name[0]
    figName = name + "_Signal.png"
    excelName = name + "_Processed.xlsx"
    #save plots and data
    plt.savefig(figName)
    writer = pd.ExcelWriter(excelName, engine="xlsxwriter")
    channel1.cleanedptDf.to_excel(writer, sheet_name="Data", index=False)
    channel1.binnedPtDf.to_excel(writer, sheet_name="Binned Data", index=False)
    channel1.mpcDf.to_excel(writer, sheet_name="Med-Pc", index=False)
    writer.close()

    #scatter plot of 465 vs 405 data
    channel1.photometryDf.plot(x="_405", y="_465", c="Time", kind="scatter", colormap="viridis")
    #save
    figName = name + "_Scatter.png"
    plt.savefig(figName)

    #display graphs
    plt.show()

main()