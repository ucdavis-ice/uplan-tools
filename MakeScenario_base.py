__author__ = 'roth'

"""
This script takes a folder with existing uplan.mdb files for each county, makes a copy of them to a new run folder and modifies the settings to match those of the source table.

Inputs: 
basepath : a folder with a copy of the uplan.mdb for each county, in which the uplan.mdb has been renamed to the fips code (eg 06001) for the county.
outfolder: the folder that will contain the new run folders
srcdbpath: an access database with a table called srcdata that has the demographic and employment settings for the runs by county.
scenarionumber: a number for your use in identifying the scenario numbers. 

Note, you must install pyodbc on your computer before this will run.

The only changes you should need to make are at the very bottom.

"""
import sys, string, os, datetime, pyodbc, shutil

class MakeScenarioDBs():
    """
    Broadcast the changes for a scenario into uplan.mdbs for a new scenario
    """
    def __init__(self):
        self.startpath = ""
        self.templatepath = ""
        self.templatedb = ""
        self.srcbasepath = ""
        self.srcdbpath = ""
        self.srcuplanmdbname = ""
        self.outfolder = ""
        self.scenarionum = ""
        self.runorder = 1
        self.errorlist = []

    def RunSQL(self, sqlstat):
        try:
            c = self.destconn.cursor()
            c.execute(sqlstat)
            self.destconn.commit()
            c = None
        except Exception, e:
            self.errorlist.append(str(e))

    def PrintErrors(self):
        print "Error list: /n"
        for e in self.errorlist:
            print str(e) + "/n"

    def fixcnty(self,n):
        if n < 10:
            return "00"+str(n)
        elif n <100:
            return "0" + str(n)
        else:
            return str(n)

    def OpenSrcDB(self):
        try:
            self.srcconn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+ self.srcdbpath )
        except Exception, e:
            self.errorlist.append(str(e))

    def CloseSrcDB(self):
        try:
            self.srcconn.close()
            return True
        except Exception, e:
            self.errorlist.append(str(e))

    def OpenDestDB(self, path):
        try:
            self.destconn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+ path )
            return True
        except Exception, e:
            self.errorlist.append(str(e))

    def CloseDestDB(self):
        try:
            self.destconn.close()
            return True
        except Exception, e:
            self.errorlist.append(str(e))

    def PadNumStr(self,i, l):
        try:
            num = str(i)
            if len(num) < l:
                num = "0"+num
            elif len(num) > l:
                return "-1"
            return num
        except Exception, e:
            self.errorlist.append(str(e))

    def BuildFolderName(self, cnty):
        try:
            if self.startpath == "":
                flder = self.outfolder + "\\" + cnty
            else:
                flder = self.startpath + "\\" + self.outfolder + "\\" + cnty
            return flder
        except  Exception, e:
            self.errorlist.append(str(e))

    def MakeFolder(self, path):
        try:
            os.makedirs(path)
            return 1
        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateGeoid(self, row):
        try:

            sqlstat = "UPDATE GEOID SET GEOID='" + row[2] + "', GEONAME = '"+ row[1] + "', GEODESCRIPTION = '" + row[1] + " County';"
            self.RunSQL(sqlstat)
        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateRes(self, row):
        try:
            if row[6] is None:
                vi = 0
            else:
                vi = row[6]

            if row[7] is None:
                vo = 0
            else:
                vo = row[7]

            sqlstat = "UPDATE residential SET BASEPOP = " + str(round(row[3],0)) + ", FUTUREPOP = " + str(round(row[4],0)) + ", PPHH = " + str(row[5]) + ", VACANTINNER = "  + str(vi) + ", VACANTOUTER = " + str(vo) + ";"
            self.RunSQL(sqlstat)
        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateEmp(self, row):
        try:
            if row[9] > 0:
                sqlstat = "UPDATE employment SET EPHH = 0, BASEEMP = " + str(row[9]) + ", FUTUREEMP = " + str(row[10]) + ";"
            else:
                sqlstat = "UPDATE employment SET EPHH = " + str(row[6]) + ", BASEEMP = 0, FUTUREEMP = 0;"
            self.RunSQL(sqlstat)

        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateResiLU(self, row):
        try:
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[11]) + ", AVGLOTSIZE = " + str(row[18]) + " WHERE LANDUSE = 'R50';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[12]) + ", AVGLOTSIZE = " + str(row[19]) + " WHERE LANDUSE = 'R20';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[13]) + ", AVGLOTSIZE = " + str(row[20]) + " WHERE LANDUSE = 'R10';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[14]) + ", AVGLOTSIZE = " + str(row[21]) + " WHERE LANDUSE = 'R5';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[15]) + ", AVGLOTSIZE = " + str(row[22]) + " WHERE LANDUSE = 'R1';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[16]) + ", AVGLOTSIZE = " + str(row[23]) + " WHERE LANDUSE = 'R.5';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE resilanduse SET PROPORTION = " + str(row[17]) + ", AVGLOTSIZE = " + str(row[24]) + " WHERE LANDUSE = 'R.1';"
            self.RunSQL(sqlstat)

        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateEmpLU(self, row):
        try:
            sqlstat = "UPDATE emplanduse SET PROPORTION = " + str(row[25]) + ", AVGSQFT = " + str(row[28]) + ", FAR = " + str(row[31]) + "  WHERE LANDUSE = 'in';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE emplanduse SET PROPORTION = " + str(row[26]) + ", AVGSQFT = " + str(row[29]) + ", FAR = " + str(row[32]) + "  WHERE LANDUSE = 'ch';"
            self.RunSQL(sqlstat)
            sqlstat = "UPDATE emplanduse SET PROPORTION = " + str(row[27]) + ", AVGSQFT = " + str(row[30]) + ", FAR = " + str(row[33]) + "  WHERE LANDUSE = 'cl';"
            self.RunSQL(sqlstat)

        except  Exception, e:
            self.errorlist.append(str(e))

    def UpdateAll(self, row):
        try:
            self.UpdateGeoid(row)
            self.UpdateEmp(row)
            self.UpdateEmpLU(row)
            self.UpdateRes(row)
            self.UpdateResiLU(row)
        except Exception, e:
            self.errorlist.append(str(e))


    def CopyTemplateDB(self, path, geoid):
        try:
            shutil.copyfile(self.templatedb, path + "\\uplan.mdb")
            return 1
        except  Exception, e:
            self.errorlist.append(str(e))



    def MainProc(self):
        self.OpenSrcDB()
        cur = self.srcconn.cursor()
        sqlstat = "SELECT * FROM srcdata;"
        cur.execute(sqlstat)
        for row in cur:
            geoid = row[2]
            cnty = row[1]
            print "Working on: " + geoid
            fips = geoid[2:]
            fldr = self.BuildFolderName(cnty)
            self.MakeFolder(fldr)
            self.CopyTemplateDB(fldr, geoid)
            self.OpenDestDB(fldr + "\\uplan.mdb")
            self.UpdateAll(row)
            self.CloseDestDB()



    def Cleanup(self):
        try:
            self.CloseSrcDB()
        except:
            pass




if __name__ == "__main__": # All changes should happen below here
    print "Starting"
    ms = MakeScenarioDBs()
    #ms.startpath = "" #Leave this blank and all other paths are relative to this python file, other wise "\\<your folder here>"
    #ms.srcbasepath = "D:\\Data\\DWR_UPLAN_Scenarios\\Master2\\UPlan\\Scripts\\Broadcaster\\srcdata\\basetemplates" # the folder containing 06001.mdb, 006003.mdb etcc
    ms.templatedb = "\\exampledata\\example_uplan.mdb" # not used in this version
    ms.srcdbpath = "\\exampledata\\example_inputs.mdb" # The mdb containing the source data table
    ms.outfolder = "\\runs"  # output folder
    #ms.scenarionum = "01" # a scenario number used in creating the run folder name


    try:
        ms.MainProc()
    except Exception, e:
        ms.errorlist.append(str(e))

    finally:
        ms.PrintErrors()
        ms.Cleanup()
        ms = None


    print "Done"
