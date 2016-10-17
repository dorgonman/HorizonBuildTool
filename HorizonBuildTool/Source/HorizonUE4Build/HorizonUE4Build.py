# -*- coding: utf-8 -*- 
import sys
from optparse import OptionParser;
from xml.dom import minidom;


import re
import os
import csv
import hashlib
import shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from HorizonBuildFileUtil import HorizonBuildFileUtil
import subprocess


class HorizonUE4Build(object):
    """description of class"""
    def __init__(self):
         #current tool version is 1
        self.m_iCodeVersion = 1
        self.m_sConfig = "default";
        self.m_sOutReportFilePath = "Output/HorizonUE4BuildReport.log"
        self.m_sClean = False

    def __generateOptionParser__(self):
        parser = OptionParser();
        parser.add_option("--config", dest="config",
                      default="./Config/HorizonUE4Build/UE4Build_sample.xml",
                      help="config file", metavar="FILE")
        parser.add_option("--clean", action="store_true", dest="clean")


        parser.add_option("--engine", dest="unreal_engine_root",
                      default="UnrealEngineRoot",
                      help="root path of unreal engine", metavar="FILE")


        parser.add_option("--project", dest="project_file_full_path",
                      default="project_file_full_path",
                      help="project_file_full_path", metavar="project_file_full_path")


        parser.add_option("--build_platform", dest="build_platform",
                      default="win64",
                      help="ex: Win64, Win32, Android...", metavar="build_platform")

        parser.add_option("--build_config", dest="build_config",
                      default="win64",
                      help="ex: Win64, Win32, Android...", metavar="build_config")
        parser.add_option("--archive", dest="build_archive_path",
                      default="./Archive/Build/",
                      help="build_archive_path", metavar="build_archive_path")


        parser.add_option("--buildclient", action="store_true", dest="buildclient")
        parser.add_option("--buildserver", action="store_true", dest="buildserver")

        parser.add_option("--cookclient", action="store_true", dest="cookclient")
        parser.add_option("--cookserver", action="store_true", dest="cookserver")
        return parser;
    def init(self):
        print("curretn folder:" + os.getcwd() + "\n")
        parser = self.__generateOptionParser__()
        (self.options, self.args) = parser.parse_args()
        print("options:" + str(self.options))
        print("args" + str(self.args))
        if(self.options.config != None):
           self.m_sConfig = self.options.config;

        if(self.options.clean != None):
           self.m_sClean = self.options.clean;

        if(self.options.unreal_engine_root != None):
           self.m_sUnrealEngineRoot = self.options.unreal_engine_root;

        if(self.options.project_file_full_path != None):
           self.m_sProjectFileFullPath = self.options.project_file_full_path;


        if(self.options.build_platform != None):
           self.m_sBuildPlatform = self.options.build_platform;


        if(self.options.build_config != None):
           self.m_sBuildConfig = self.options.build_config;

        if(self.options.build_archive_path != None):
           self.m_sBuildArchivePath = self.options.build_archive_path;


        print("m_sUnrealEngineRoot:" + str(self.m_sUnrealEngineRoot))
        print("m_sProjectFileFullPath:" + str(self.m_sProjectFileFullPath))
        print("m_sBuildPlatform:" + str(self.m_sBuildPlatform)) 
        print("m_sBuildArchivePath:" + str(self.m_sBuildArchivePath))
        #xmldoc = minidom.parse(self.m_sConfig)   
        #self.m_sHorizonEngineRoot = os.path.abspath(xmldoc.getElementsByTagName('UnrealEngineRoot')[0].firstChild.nodeValue);

    def execute(self): 

        HorizonBuildFileUtil.HorizonBuildFileUtil.EnsureDir(self.m_sOutReportFilePath)
        reportFile = open(self.m_sOutReportFilePath, 'w', encoding = 'utf-8')
        reportFile.truncate()
        reportFile.close()
     
        if(self.options.buildclient != None):
             self.buildClient()
   
   
        if(self.options.buildserver != None):
             self.buildServer()


        if(self.options.cookclient != None):
            self.cookClient()

        if(self.options.cookserver != None):
             self.cookServer()
  


    def buildClient(self):
        bSuccess = False
        self.__buildClientEditor()
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Build/BatchFiles/RunUAT.{EXT}" BuildCookRun \
               -project="{PROJECT_FILE_FULL_PATH}" \
               -noP4 -platform={BUILD_PLATFORM} \
               -clientconfig={BUILD_CONFIG} -serverconfig={BUILD_CONFIG} \
               -cook -allmaps -build -stage \
               -pak -archive -archivedirectory="{BUILD_ARCHIVE_PATH}"'
        

        sCmd = self.__getBuildCommand(sCmd)

        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  
           

    def cookClient(self):
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Build/BatchFiles/RunUAT.{EXT}" BuildCookRun \
               -project="{PROJECT_FILE_FULL_PATH}" \
               -noP4 -platform={BUILD_PLATFORM} \
               -clientconfig={BUILD_CONFIG} -serverconfig={BUILD_CONFIG} \
               -cook -allmaps -NoCompile -stage \
               -pak -archive -archivedirectory="{BUILD_ARCHIVE_PATH}"'
        

        sCmd = self.__getBuildCommand(sCmd)

        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  


    def buildServer(self):
        bSuccess = False
        #self.__buildServerEditor()
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Build/BatchFiles/RunUAT.{EXT}" BuildCookRun -verbose\
               -project="{PROJECT_FILE_FULL_PATH}" \
               -noP4 -platform={BUILD_PLATFORM} \
               -clientconfig={BUILD_CONFIG} -serverconfig={BUILD_CONFIG} \
               -cook -server -serverplatform={BUILD_PLATFORM} -noclient -build -stage \
               -pak -archive -archivedirectory="{BUILD_ARCHIVE_PATH}"'
        

        sCmd = self.__getBuildCommand(sCmd)

        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  

    def cookServer(self):
        bSuccess = False
        self.__buildClientEditor()
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Build/BatchFiles/RunUAT.{EXT}" BuildCookRun \
               -project="{PROJECT_FILE_FULL_PATH}" \
               -noP4 -platform={BUILD_PLATFORM} \
               -clientconfig={BUILD_CONFIG} -serverconfig={BUILD_CONFIG} \
               -cook -server -serverplatform={BUILD_PLATFORM} -noclient -NoCompile -stage \
               -pak -archive -archivedirectory="{BUILD_ARCHIVE_PATH}"'
        

        sCmd = self.__getBuildCommand(sCmd)

        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  
    #========================private function==============================

    def __buildClientEditor(self):
        # for fix error: https://answers.unrealengine.com/questions/409205/automated-build-system-errors-ue4editor-xdll-missi.html
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Binaries/DotNET/UnrealBuildTool.exe" \
                {BUILD_TARGET} {BUILD_CONFIG} {BUILD_PLATFORM} -project="{PROJECT_FILE_FULL_PATH}" \
                -editorrecompile -progress -noubtmakefiles -NoHotReloadFromIDE -2015'


        sBuildTarget = os.path.splitext(os.path.basename(self.m_sProjectFileFullPath))[0]
        sCmd = sCmd.format(
            UNREAL_ENGINE_ROOT=self.m_sUnrealEngineRoot, 
            BUILD_TARGET=sBuildTarget, 
            PROJECT_FILE_FULL_PATH=self.m_sProjectFileFullPath,
            BUILD_PLATFORM=self.m_sBuildPlatform,
            BUILD_CONFIG=self.m_sBuildConfig) 
        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  
    def __buildServerEditor(self):
        # for fix error: https://answers.unrealengine.com/questions/409205/automated-build-system-errors-ue4editor-xdll-missi.html
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Binaries/DotNET/UnrealBuildTool.exe" \
                {BUILD_TARGET} {BUILD_CONFIG} {BUILD_PLATFORM} -project="{PROJECT_FILE_FULL_PATH}" \
                -editorrecompile -progress -noubtmakefiles -NoHotReloadFromIDE -2015'


        sBuildTarget = os.path.splitext(os.path.basename(self.m_sProjectFileFullPath))[0] + "Server"
        sCmd = sCmd.format(
            UNREAL_ENGINE_ROOT=self.m_sUnrealEngineRoot, 
            BUILD_TARGET=sBuildTarget, 
            PROJECT_FILE_FULL_PATH=self.m_sProjectFileFullPath,
            BUILD_PLATFORM=self.m_sBuildPlatform,
            BUILD_CONFIG=self.m_sBuildConfig) 
        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  
  
    def __getExt(self):
        sExt = "sh"
        if("win" in self.m_sBuildPlatform.lower()):
            sExt = "bat"
        else:
            sExt = "sh"
        return sExt
    def __getBuildCommand(self, sCmd):
        sExt = self.__getExt()
        sResult = sCmd.format(
                           UNREAL_ENGINE_ROOT=self.m_sUnrealEngineRoot, 
                           EXT=sExt, 
                           PROJECT_FILE_FULL_PATH=self.m_sProjectFileFullPath,
                           BUILD_PLATFORM=self.m_sBuildPlatform,
                           BUILD_CONFIG=self.m_sBuildConfig,
                           BUILD_ARCHIVE_PATH=self.m_sBuildArchivePath
                            ) 
        return sResult