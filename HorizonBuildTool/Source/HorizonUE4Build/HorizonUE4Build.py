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
        return parser;
    def init(self):
        print("curretn folder:" + os.getcwd() + "\n")
        parser = self.__generateOptionParser__()
        (options, args) = parser.parse_args()
        print("options:" + str(options))
        print("args" + str(args))
        if(options.config != None):
           self.m_sConfig = options.config;

        if(options.clean != None):
           self.m_sClean = options.clean;

        if(options.unreal_engine_root != None):
           self.m_sUnrealEngineRoot = options.unreal_engine_root;

        if(options.project_file_full_path != None):
           self.m_sProjectFileFullPath = options.project_file_full_path;


        if(options.build_platform != None):
           self.m_sBuildPlatform = options.build_platform;


        if(options.build_config != None):
           self.m_sBuildConfig = options.build_config;

        if(options.build_archive_path != None):
           self.m_sBuildArchivePath = options.build_archive_path;


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
        #self.cookClient()
        self.buildClient()


    def buildClient(self):
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        sCmd = '"{UNREAL_ENGINE_ROOT}/Engine/Build/BatchFiles/RunUAT.{EXT}" BuildCookRun \
               -project="{PROJECT_FILE_FULL_PATH}" \
               -noP4 -platform={BUILD_PLATFORM} \
               -clientconfig={BUILD_CONFIG} -serverconfig={BUILD_CONFIG} \
               -cook -allmaps -build -stage \
               -pak -archive -archivedirectory="{BUILD_ARCHIVE_PATH}"'
        

        if("win" in self.m_sBuildPlatform.lower()):
            sExt = "bat"
        else:
            sExt = "sh"

        sCmd = sCmd.format(
                           UNREAL_ENGINE_ROOT=self.m_sUnrealEngineRoot, 
                           EXT=sExt, 
                           PROJECT_FILE_FULL_PATH=self.m_sProjectFileFullPath,
                           BUILD_PLATFORM=self.m_sBuildPlatform,
                           BUILD_CONFIG=self.m_sBuildConfig,
                           BUILD_ARCHIVE_PATH=self.m_sBuildArchivePath
                            ) 

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
        

        if("win" in self.m_sBuildPlatform.lower()):
            sExt = "bat"
        else:
            sExt = "sh"

        sCmd = sCmd.format(
                           UNREAL_ENGINE_ROOT=self.m_sUnrealEngineRoot, 
                           EXT=sExt, 
                           PROJECT_FILE_FULL_PATH=self.m_sProjectFileFullPath,
                           BUILD_PLATFORM=self.m_sBuildPlatform,
                           BUILD_CONFIG=self.m_sBuildConfig,
                           BUILD_ARCHIVE_PATH=self.m_sBuildArchivePath
                            ) 

        HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
        result = subprocess.run(sCmd, shell=True)  

        if(result.returncode == 0):
            bSuccess = True
        reportFile.close()
        return bSuccess  
