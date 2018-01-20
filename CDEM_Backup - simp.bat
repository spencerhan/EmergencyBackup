cls
echo on
rem setting up python path. 
setlocal
if exist C:\Python27\ArcGISx6410.4 set path=%path%; C:\Python27\ArcGISx6410.4
if exist C:\Python27\ArcGISx6410.4 set PYTHONPATH=%PYTHONPATH%; C:\Python27\ArcGISx6410.4
rem Reporting Python version
python -V exit()
rem Run the main python script, command line output wil be save a txt file
echo %Date% %time% > ''\%date:~-10,2%-%date:~-7,2%-%date:~-4,4%_BACKUP.txt
python $DirecotryPath\CDEM_BACKUP\Backup_Script_simp_version.py >> $DirecotryPath\%date:~-10,2%-%date:~-7,2%-%date:~-4,4%_BACKUP.txt
endlocal
exit