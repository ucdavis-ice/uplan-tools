'''
Created on Feb 1, 2012

@author: Roth
'''
import arcpy, time


class FAConverter:
    def __init__(self,far):
        self.far = far
    
    def CheckForDataset(self,dsname, dstype, dspath):
        arcpy.env.workspace = dspath
        if dstype == "table":
            dss = arcpy.ListTables()
        else:
            dss = arcpy.ListDatasets()
        for ds in dss:
            if ds == dsname:
                return True
        
        return False

    def MainProc(self):
        try:
            print "Beginning Process"
            #get AOI
            #aoi = arcpy.GetParameterAsText(0)   
            
            #get final raster
        #    far = arcpy.GetParameterAsText(0) 
            #r"F:\iplace3s\Training_05142012\TulareUplan\Tulare\runs\r090114184704\finalalloc"
            
            arcpy.env.overwriteOutput = True
            
            #Describe final raster
            descfa = arcpy.Describe(self.far)
            catpath = descfa.catalogPath
            print catpath
            runpath = catpath[:catpath.rfind("\\")]
            print runpath
            uppath = runpath + "\\uplan.mdb"
            self.fgdbpath = runpath + "\\uplan.gdb"
            inipath = catpath[:catpath.rfind("\\runs")] + "\\ini\\initialization.mdb"
            datapath = catpath[:catpath.rfind("\\runs")] + "\\data"
            print inipath
            
            # Create File Geodatabase
            try:
                arcpy.CreateFileGDB_management(runpath, "uplan.gdb", "9.3")
            except Exception, e:
                arcpy.AddMessage("Failed to crate FGDB, assuming that it already exists and proceeding")
                pass
            
            #get variantid
            vcur =arcpy.SearchCursor(uppath + "\\variant")
            for vrow in vcur:
                varid = vrow.VARIANTID
                varname = vrow.VARIANTNAME
            print varid
            print type(varid)
            print varname
            
            #Get model type
            mcur = arcpy.SearchCursor(uppath +"\\modeltype")
            for mrow in mcur:
                mtype = mrow.MODELTYPE
                mtypename = mrow.MODELNAME
            print mtype
            print mtypename
            
            #Get Geoid
            geodcur = arcpy.SearchCursor(uppath + "\\geoid")
            for grow in geodcur:
                geoid = grow.GEOID
            
            if mtype == 2: #get subarea raster
                sacur1 = arcpy.SearchCursor(inipath + "\\modelparams", "VARIANTID = " + str(varid) + " AND modelparam = 'SUBAREA' AND GEOID = '" + geoid + "'")
                for sarow1 in sacur1:
                    saras = sarow1.modelvalue
                    
            
            #Get
            #dens config = ['luname', 'lutype', 'rlotsize','esf','efar', 'rdens', 'edens']
            ludens = {}
            if mtype in [1,3]:
                #Residential
                lucur = arcpy.SearchCursor(uppath + "\\resilanduse")
                for lurow in lucur:
                    if lurow.AVGLOTSIZE > 0:
                        ludvals = [lurow.LANDUSE, 1, lurow.AVGLOTSIZE, 0,0,1/lurow.AVGLOTSIZE, 0]
                    else:
                        ludvals = [lurow.LANDUSE, 1, lurow.AVGLOTSIZE, 0,0,0, 0]
                    ludens[lurow.LANDUSE] = ludvals
                
                #Employment
                lucur = arcpy.SearchCursor(uppath + "\\emplanduse")
                for lurow in lucur:
                    if lurow.AVGSQFT > 0 and lurow.FAR > 0:
                        ludvals = [lurow.LANDUSE, 2, 0, lurow.AVGSQFT,lurow.FAR,0, 43560/(lurow.AVGSQFT/lurow.FAR)]
                    else:
                        ludvals = [lurow.LANDUSE, 2, 0, lurow.AVGSQFT,lurow.FAR,0,0]
                    ludens[lurow.LANDUSE] = ludvals
                    
                    
            elif mtype == 2:
                #Residential
                lucur = arcpy.SearchCursor(uppath + "\\subarearesidential")
                for lurow in lucur:
                    if lurow.AVGLOTSIZE > 0:
                        ludvals = [lurow.LANDUSE, lurow.SUBAREAID, 1, lurow.AVGLOTSIZE, 0,0,1/lurow.AVGLOTSIZE, 0]
                    else:
                        ludvals = [lurow.LANDUSE, lurow.SUBAREAID, 1, lurow.AVGLOTSIZE, 0,0,0, 0]
                    ludens[lurow.LANDUSE, lurow.SUBAREAID] = ludvals
                
                #Employment
                lucur = arcpy.SearchCursor(uppath + "\\subareaemployment")
                for lurow in lucur:
                    if lurow.AVGSQFT > 0 and lurow.FAR > 0:
                        ludvals = [lurow.LANDUSE, lurow.SUBAREAID, 2, 0, lurow.AVGSQFT,lurow.FAR,0, 43560/(lurow.AVGSQFT/lurow.FAR)]
                    else:
                        ludvals = [lurow.LANDUSE, lurow.SUBAREAID, 2, 0, lurow.AVGSQFT,lurow.FAR,0, 0]
                    ludens[lurow.LANDUSE, lurow.SUBAREAID] = ludvals
        #        print "Subarea not yet implemented"
        #        arcpy.AddError("Subarea is not yet implemented")
                
           
            #get land uses
            lucur = arcpy.SearchCursor(inipath + "\\landuses", "[VARIANTID] = " + str(varid))
            lu = {}
            lus = []
            for lurow in lucur:
                #get densities
                dlu = {}
                if mtype in [1,3]:
                    lus.append(lurow.landuse)
                    lu[lurow.landuse] = [lurow.landuse, lurow.landusename, lurow.landusetype, lurow.landid, ludens[lurow.landuse][5],ludens[lurow.landuse][6]]
                        
                        
                elif mtype ==2:
                    # Get subareas too
                    sacur = arcpy.SearchCursor(uppath + "\\subareas")
                    for sarow in sacur:
                        lus.append((lurow.landuse, sarow.SUBAREAID))
        #                lid = [lurow.landuse,sarow.SUBAREAID]
                        lu[lurow.landuse,sarow.SUBAREAID] = [lurow.landuse, sarow.SUBAREAID, lurow.landusename, lurow.landusetype, lurow.landid, ludens[lurow.landuse, sarow.SUBAREAID][6],ludens[lurow.landuse,sarow.SUBAREAID][7]]
                        
            
        #    print lu
            
            if self.CheckForDataset("updensities","table", self.fgdbpath) == False:
                print "creating updensities table"
                arcpy.CreateTable_management(self.fgdbpath, "updensities")
                arcpy.AddField_management(self.fgdbpath + "\\updensities", "landid", "LONG")
                arcpy.AddField_management(self.fgdbpath + "\\updensities", "landuse", "TEXT", "#", "#", "25")
                arcpy.AddField_management(self.fgdbpath + "\\updensities", "landname", "TEXT", "#", "#", "100")
                arcpy.AddField_management(self.fgdbpath + "\\updensities", "rdens", "DOUBLE")
                arcpy.AddField_management(self.fgdbpath + "\\updensities", "edens", "DOUBLE")
                if mtype == 2:
                    arcpy.AddField_management(self.fgdbpath + "\\updensities", "subarea", "LONG")
                time.sleep(5)
                irows = arcpy.InsertCursor(self.fgdbpath + "\\updensities")
                for l in lus:
        #            print "Inserting: " + l
                    if mtype in [1,3]:
                        irow = irows.newRow()
                        irow.landid = lu[l][3]
                        irow.landuse = l
                        irow.landname = lu[l][1]
                        irow.rdens = lu[l][4]
                        irow.edens = lu[l][5]
                        #time.sleep(0.1)
                        irows.insertRow(irow)
                        time.sleep(0.1)
                    elif mtype == 2:
                        irow = irows.newRow()
                        print l[0] + ":"+ str(l[1])
                        lut = lu[l]
                        irow.landid = lut[4] + 100*l[1]
                        irow.subarea = lut[1]
                        irow.landuse = l[0]
                        irow.landname = lut[2]
                        irow.rdens = lut[5]
                        irow.edens = lut[6]
                        
                        #time.sleep(0.1)
                        irows.insertRow(irow)
                        time.sleep(0.1)
                del irow
                del irows
            else:
                print "updensities already exists"
                
            #Raster to Polygon
            print "Vectorizing"
            if mtype in [1,3]:
                arcpy.RasterToPolygon_conversion(self.far, self.fgdbpath + "\\final_alloc_1", "NO_SIMPLIFY", "VALUE")
            
            elif mtype == 2:
                arcpy.RasterToPolygon_conversion(self.far, self.fgdbpath + "\\final_alloc_0", "NO_SIMPLIFY", "VALUE")
                arcpy.RasterToPolygon_conversion(datapath + "\\" + geoid + "\\" + saras, self.fgdbpath + "\\sa", "NO_SIMPLIFY", "VALUE")
                #Intersect
                arcpy.Intersect_analysis([self.fgdbpath + "\\final_alloc_0", self.fgdbpath + "\\sa"], self.fgdbpath + "\\final_alloc_1", "ALL")
                arcpy.AddField_management(self.fgdbpath + "\\final_alloc_1", "landid", "LONG")
                arcpy.CalculateField_management(self.fgdbpath + "\\final_alloc_1", "landid", "!grid_code! + 100*!grid_code_1!","PYTHON_9.3" )
                
            
            #Make feature layer and table view
            arcpy.MakeFeatureLayer_management(self.fgdbpath + "\\final_alloc_1", "final_alloc")
            arcpy.MakeTableView_management(self.fgdbpath + "\\updensities", "densities")
            if mtype in [1,3]:
                arcpy.AddJoin_management("final_alloc", "grid_code", "densities", "landid", "KEEP_ALL")
            else:
                arcpy.AddJoin_management("final_alloc", "landid", "densities", "landid", "KEEP_ALL")
            arcpy.CopyFeatures_management("final_alloc", self.fgdbpath + "\\final_alloc_dens")
            arcpy.FeatureToPoint_management(self.fgdbpath + "\\final_alloc_dens", self.fgdbpath + "\\final_alloc_dens_pt", "CENTROID")
            
            
            print "Process Complete"
            #print arcpy.GetMessages()
        except Exception, e:
            print str(e)
            print arcpy.GetMessages()
            pass
        
    def CopyFinal(self, outfile):
        try:
            arcpy.Copy_management(self.fgdbpath + "\\final_alloc_dens", outfile)
        except Exception:
            raise
        
if __name__ == "__main__":
    print "Starting"
    
    print "kern vwh"
    # Kern
    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Kern\SJV_Alternative-Nate_101708\runs\r081112162009\finalalloc" )
    fac.MainProc()
    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\krn_wwh.shp")
    fac = None

#    # Fresno
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\fresno\LocalPreff\runs\r081013000000\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\fre_Bpl.shp")
#    fac = None
    
#    print "kern"
#    # Kern
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Kern\SJV_Alternative-Nate_101708\runs\r090115143352\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\krn_bpl.shp")
#    fac = None
    
#    print "kings"
#    # Kings
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Kings\runs\r081231085338\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\kng_Bpl.shp")
#    fac = None
    
#    print "tulare"
#    # Tulare
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Tulare\runs\r090114184704\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\tul_Bpl.shp")
#    fac = None
    
#    print "madera"
#    # madera
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Madera\UpdateRuns092908\runs\r081231084215\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\mad_Bpl.shp")
#    fac = None
    
#    print "merced"
#    # Merced
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Merced\Uplan2_6\2.64_Update\runs\r090113131101\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\mer_Bpl.shp")
#    fac = None
    
#    print "stanislaus"  
#    # Stan
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\Stanislaus\runs\r090119214922\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\sta_Bpl.shp")
#    fac = None
    
#    print "sjq"
#    # Sjq
#    fac = FAConverter(r"M:\SJVBlueprint\SJV\Uplan2_6_Update\SanJoaquin\runs\r090221175308\finalalloc" )
#    fac.MainProc()
#    fac.CopyFinal(r"M:\rapidfire\RefillCalcs\Data\sjq_Bpl.shp")
#    fac = None
    
    print "done"