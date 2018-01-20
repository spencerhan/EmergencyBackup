#-------------------------------------------------------------------------------
# Name:        CDEM Backup Script _simp_ beta _ version 1
# Purpose:     To back up the master oracle database using ArcSDE environment
#              for emergency purposes.
#
#              This is a simplified version of preview version. It will only
#              fetching data from GIS_ALL
#
# Author:      Spencer Han
#
# Created:     16/12/2015
# Copyright:   (c) Spencer Han 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

# Import arcpy module
import time, os, datetime, sys, logging, logging.handlers, shutil
import arcpy

def formatTime(x):
    minutes, seconds_rem = divmod(x, 60)
    if minutes >= 60:
        hours, minutes_rem = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
    else:
        minutes, seconds_rem = divmod(x, 60)
        return "00:%02d:%02d" % (minutes, seconds_rem)

def getDatabaseItemCount(workspace):
    log = logging.getLogger("backup_log")
    """returns the item count in provided database"""
    arcpy.env.workspace = workspace
    feature_classes = []
    log.info("Compiling a list of items in {0} and getting count.".format(workspace))
    i = 1
    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,datatype="Any",type="Any"):
        for filename in filenames:
            print("Fetching" + " " + str(i) + " " + "feature(s) file addresses")
            feature_classes.append(os.path.join(dirpath, filename))
            i += 1
    log.info("There are a total of {0} items in the database".format(len(feature_classes)))
    return feature_classes, len(feature_classes)

def replicateDatabase(dbConnection, targetGDB):
    log = logging.getLogger("backup_log")
    startTime = time.time()

    if arcpy.Exists(dbConnection):
        featureSDE,cntSDE = getDatabaseItemCount(dbConnection)
        log.info("Geodatabase being copied: %s -- Feature Count: %s" %(dbConnection, cntSDE))
        if arcpy.Exists(targetGDB):
            featureGDB,cntGDB = getDatabaseItemCount(targetGDB)
            log.info("Old Target Geodatabase: %s -- Feature Count: %s" %(targetGDB, cntGDB))
            try:
                shutil.rmtree(targetGDB)
                log.info("Deleted Old %s" %(os.path.split(targetGDB)[-1]))
            except Exception as e:
                #log.info(e)
                log.exception(e)
        GDB_Path, GDB_Name = os.path.split(targetGDB)
        log.info("Now Creating New %s" %(GDB_Name))
        arcpy.CreateFileGDB_management(GDB_Path, GDB_Name)
        arcpy.env.workspace = dbConnection
        log.info("Start fetching the feature class list \n")
        print("Start fetching the feature class list \n")
        for fc in arcpy.ListFeatureClasses():
            if "GIS_ALL" not in fc:
                print("Skipped a feature that is not from the GIS_ALL")
                log.info("Skipped a feature that is not from the GIS_ALL")
                del fc
                continue
            else:
                try:
                    print("Attempting to Copy %s to %s" %(fc, targetGDB))
                    log.info("Attempting to Copy %s to %s" %(fc, targetGDB))
                    #arcpy.FeatureClassToGeodatabase_conversion(featureClasses, targetGDB)
                    arcpy.FeatureClassToGeodatabase_conversion(fc, targetGDB)
                    print("Finished copying %s to %s \n" %(fc, targetGDB))
                    log.info("Finished copying %s to %s \n" %(fc, targetGDB))
                    del fc
                except Exception as e:
                    print(e.message)
                    print("Unable to copy %s to %s" %(fc, targetGDB))
                    log.info("Unable to copy %s to %s" %(fc, targetGDB))
                    log.exception(e)
                    del fc
                    continue
        featGDB,cntGDB = getDatabaseItemCount(targetGDB)
        print("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))
        log.info("Completed replication of %s -- Feature Count: %s" %(dbConnection, cntGDB))

    else:
        print("{0} does not exist or is not supported! \
        Please check the database path and try again.".format(dbConnection))
        log.info("{0} does not exist or is not supported! \
        Please check the database path and try again.".format(dbConnection))

if __name__ == '__main__':
    main()
    ############################### log file header #################################
    startTime = time.time()
    now = datetime.datetime.now()
    print now.strftime("%d-%m-%Y_%H-%M.log")
    print sys.version
    ############################### user variables #################################
    '''change these variables to the location of the database being copied, the target
    database location and where you want the log to be stored'''

    databaseConnection = r"" 
    arcpy.env.workspace = r""
    out_folder_path = r""
    base = os.path.splitext("BACKUP_PYTHON.gdb")
    out_name = base[0] +"_"+ now.strftime("%d-%m-%Y_%H-%M")+".gdb"
    arcpy.CreateFileGDB_management(out_folder_path, out_name)

    targetGDB = out_folder_path + "\\" + out_name

    ############################### logging items ###################################
    # Make a global logging object.
    logPath = out_folder_path
    logName = os.path.join(logPath,(now.strftime("%d-%m-%Y_%H-%M.log")))

    log = logging.getLogger("backup_log")
    log.setLevel(logging.INFO)

    h1 = logging.FileHandler(logName)
    h2 = logging.StreamHandler()

    f = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(lineno)d] - %(message)s",'%d/%m/%Y %I:%M:%S %p')

    h1.setFormatter(f)
    h2.setFormatter(f)

    h1.setLevel(logging.INFO)
    h2.setLevel(logging.INFO)

    log.addHandler(h1)
    log.addHandler(h2)

    log.info('Script: {0}'.format(os.path.basename(sys.argv[0])))

    try:
        ########################## function calls ######################################

        replicateDatabase(databaseConnection, targetGDB)

        ################################################################################
    except Exception as e:
        print(e.message)
        log.exception(e)
        #log.info(e.message, e.args)

    totalTime = formatTime((time.time() - startTime))
    log.info('--------------------------------------------------')
    log.info("Backup Completed After: {0}".format(totalTime))
    log.info('--------------------------------------------------')
    log.removeHandler(h1)
    log.removeHandler(h2)
    del log,h1,h2
    print "Log file closed"
