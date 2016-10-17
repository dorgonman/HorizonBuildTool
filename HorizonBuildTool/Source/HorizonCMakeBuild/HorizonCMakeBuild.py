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

import HorizonBuildFileUtil
from HorizonBuildFileUtil import HorizonBuildFileUtil
import subprocess


class HorizonCMakeBuild(object):
    """description of class"""
    def __init__(self):
         #current tool version is 1
        self.m_iCodeVersion = 1
        self.m_sConfig = "default";
        self.m_sOutReportFilePath = "Output/HorizonCMakeBuildReport.log"
        self.m_bClean = False

    def __generateOptionParser__(self):
        parser = OptionParser();
        parser.add_option("--config", dest="config",
                      default="./Config/sqlite3_vs2015_win64.xml",
                      help="config file", metavar="FILE")
        parser.add_option("--clean", action="store_true", dest="clean")
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
           self.m_bClean = options.clean;

        xmldoc = minidom.parse(self.m_sConfig)
        self.m_sHorizonEngineRoot = os.path.abspath(xmldoc.getElementsByTagName('HorizonEngineRoot')[0].firstChild.nodeValue);
        self.m_sProjectRoot = os.path.abspath(xmldoc.getElementsByTagName('ProjectRoot')[0].firstChild.nodeValue);
        self.m_sProjectBuildRoot = os.path.abspath(xmldoc.getElementsByTagName('ProjectBuildRoot')[0].firstChild.nodeValue);     
        self.m_sProjectBuildArch = xmldoc.getElementsByTagName('ProjectBuildArch')[0].firstChild.nodeValue;
        self.m_sProjectBuildPlatform = xmldoc.getElementsByTagName('ProjectBuildPlatform')[0].firstChild.nodeValue;
        self.m_sProjectBuildConfig = xmldoc.getElementsByTagName('ProjectBuildConfig')[0].firstChild.nodeValue;
        self.m_sProjectGeneratedExtraFlag = xmldoc.getElementsByTagName('ProjectGeneratedExtraFlag')[0].firstChild.nodeValue;
        self.m_sProjectBuildExtraFlag = xmldoc.getElementsByTagName('ProjectBuildExtraFlag')[0].firstChild.nodeValue;
        self.m_bGenerateOnly = HorizonBuildFileUtil.HorizonBuildFileUtil.ToBool(xmldoc.getElementsByTagName('GenerateOnly')[0].firstChild.nodeValue);
        print("Config.HorizonEngineRoot:" + str(self.m_sHorizonEngineRoot))
        print("Config.ProjectRoot:" + str(self.m_sProjectRoot))
        print("Config.ProjectBuildRoot:" + str(self.m_sProjectBuildRoot)) 
        print("Config.ProjectBuildArch:" + str(self.m_sProjectBuildArch))
        print("Config.ProjectBuildPlatform:" + str(self.m_sProjectBuildPlatform))
        print("Config.ProjectBuildConfig:" + str(self.m_sProjectBuildConfig))
        print("Config.ProjectBuildExtraFlag:" + str(self.m_sProjectBuildExtraFlag))
        print("Config.GenerateOnly:" + str(self.m_bGenerateOnly))


        self.m_sCMakeGenerator = xmldoc.getElementsByTagName('CMakeGenerator')[0].firstChild.nodeValue;     
        print("Config.CMakeGenerator:" + str(self.m_sCMakeGenerator))

        self.m_sProjectIDERoot = os.path.abspath(self.m_sProjectRoot + "/intermediate/project/" + 
                                                 self.m_sProjectBuildPlatform + "/" + 
                                                 self.m_sProjectBuildArch + "/" + 
                                                 self.m_sProjectBuildConfig + "/")


        self.m_sProjectIDERoot = self.m_sProjectIDERoot.replace(";", "_")

        self.m_sCMakeArchiveOutputFolder = os.path.abspath(self.m_sProjectRoot + "/libs/" + 
                                                               self.m_sProjectBuildPlatform + "/" + 
                                                               self.m_sProjectBuildArch + "/")

        self.m_sCMakeArchiveOutputFolder = self.m_sCMakeArchiveOutputFolder.replace(";", "_")
        print("ProjectIDERoot:" + str(self.m_sProjectIDERoot))
        print("CMakeArchiveOutputFolder:" + str(self.m_sCMakeArchiveOutputFolder))

    def buildGenericProject(self):
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        with HorizonBuildFileUtil.HorizonBuildFileUtil.pushd(self.m_sProjectIDERoot):
            sCmd = 'cmake --build {PROJECT_IDE_ROOT} --config {PROJECT_BUILD_CONFIG} {PROJECT_BUILD_EXTRA_FLAG}'
            sCmd = sCmd.format(
                                PROJECT_IDE_ROOT=self.m_sProjectIDERoot, 
                                PROJECT_BUILD_CONFIG=self.m_sProjectBuildConfig, 
                                PROJECT_BUILD_EXTRA_FLAG=self.m_sProjectBuildExtraFlag) 

            HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
            result = subprocess.run(sCmd, shell=True)  

            if(result.returncode == 0):
                bSuccess = True
        reportFile.close()
        return bSuccess  
    
    def generateWindowsProject(self):
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        with HorizonBuildFileUtil.HorizonBuildFileUtil.pushd(self.m_sProjectIDERoot):
            sCmd = 'cmake {PROJECT_BUILD_ROOT} -G "{CMAKE_GENERATOR}" \
            {PROJECT_GENERATED_EXTRA_FLAG} \
            -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={CMAKE_ARCHIVE_OUTPUT_DIRECTORY} \
            -DHORIZON_ENGINE_ROOT={HORIZON_ENGINE_ROOT}'

            sCmd = sCmd.format(
                                PROJECT_BUILD_ROOT=self.m_sProjectBuildRoot, 
                                CMAKE_GENERATOR=self.m_sCMakeGenerator, 
                                PROJECT_GENERATED_EXTRA_FLAG=self.m_sProjectGeneratedExtraFlag, 
                                CMAKE_ARCHIVE_OUTPUT_DIRECTORY=self.m_sCMakeArchiveOutputFolder,
                                HORIZON_ENGINE_ROOT=self.m_sHorizonEngineRoot) 

            HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
            result = subprocess.run(sCmd, shell=True)  

            if(result.returncode == 0):
                bSuccess = True
        reportFile.close()
        return bSuccess


    def buildWindowsProject(self):
       return self.buildGenericProject()
    
    def generateAndroidProject(self):
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')

        #https://blogs.msdn.microsoft.com/vcblog/2015/12/15/support-for-android-cmake-projects-in-visual-studio/
        #https://cmake.org/cmake/help/v3.6/manual/cmake-toolchains.7.html
        #/d/NVPACK/android-ndk-r12b/toolchains/arm-linux-androideabi-4.9/prebuilt/windows-x86_64/bin/arm-linux-androideabi-readelf.exe -a -W /d/workspace/horizonengine/thirdparty/libSqlite3/libs/android/armeabi/Debug/libsqlite3Static.a



        with HorizonBuildFileUtil.HorizonBuildFileUtil.pushd(self.m_sProjectIDERoot):

            xmldoc = minidom.parse(self.m_sConfig)
            self.m_androidMinAPI = xmldoc.getElementsByTagName('AndroidMinAPI')[0].firstChild.nodeValue;
            self.m_androidTargetAPI = xmldoc.getElementsByTagName('AndroidTargetAPI')[0].firstChild.nodeValue;

            subprocess.run("cmake --version", shell=True)  
            sCmd = 'cmake {PROJECT_BUILD_ROOT} -G "{CMAKE_GENERATOR}" \
                    -DCMAKE_TOOLCHAIN_FILE={CMAKE_TOOLCHAIN_FILE} \
                    {PROJECT_GENERATED_EXTRA_FLAG} \
                    -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={CMAKE_ARCHIVE_OUTPUT_DIRECTORY} \
                    -DHORIZON_ENGINE_ROOT={HORIZON_ENGINE_ROOT} \
                    -DCMAKE_SYSTEM_NAME=Android  \
                    -DCMAKE_ANDROID_ARCH={PROJECT_BUILD_ARCH} \
                    -DCMAKE_ANDROID_API={ANDROID_API} \
                    -DCMAKE_ANDROID_API_MIN={ANDROID_API_MIN}'

            sToolChainPath=os.path.abspath(self.m_sHorizonEngineRoot + "/cmake/android/toolchain.cmake")
            sCmd = sCmd.format(
                                PROJECT_BUILD_ROOT=self.m_sProjectBuildRoot, 
                                CMAKE_GENERATOR=self.m_sCMakeGenerator, 
                                CMAKE_TOOLCHAIN_FILE=sToolChainPath,
                                PROJECT_GENERATED_EXTRA_FLAG=self.m_sProjectGeneratedExtraFlag, 
                                CMAKE_ARCHIVE_OUTPUT_DIRECTORY=self.m_sCMakeArchiveOutputFolder,
                                HORIZON_ENGINE_ROOT=self.m_sHorizonEngineRoot,
                                PROJECT_BUILD_PLATFORM=self.m_sProjectBuildPlatform,
                                PROJECT_BUILD_ARCH=self.m_sProjectBuildArch,
                                ANDROID_API=self.m_androidMinAPI,
                                ANDROID_API_MIN=self.m_androidTargetAPI) 

            HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
            result = subprocess.run(sCmd, shell=True)  

            if(result.returncode == 0):
                bSuccess = True
        reportFile.close()
        return bSuccess
    def buildAndroidProject(self):
        return self.buildGenericProject()

    def generateMacOSXProject(self):
        #CMAKE_OSX_ARCHITECTURES="i386;x86_64"
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        with HorizonBuildFileUtil.HorizonBuildFileUtil.pushd(self.m_sProjectIDERoot):
            sCmd = 'cmake {PROJECT_BUILD_ROOT} -G "{CMAKE_GENERATOR}" \
            {PROJECT_GENERATED_EXTRA_FLAG} \
            -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={CMAKE_ARCHIVE_OUTPUT_DIRECTORY} \
            -DHORIZON_ENGINE_ROOT={HORIZON_ENGINE_ROOT} \
            -DCMAKE_OSX_ARCHITECTURES="{CMAKE_OSX_ARCHITECTURES}"'

            sCmd = sCmd.format(
                                PROJECT_BUILD_ROOT=self.m_sProjectBuildRoot, 
                                CMAKE_GENERATOR=self.m_sCMakeGenerator, 
                                PROJECT_GENERATED_EXTRA_FLAG=self.m_sProjectGeneratedExtraFlag, 
                                CMAKE_ARCHIVE_OUTPUT_DIRECTORY=self.m_sCMakeArchiveOutputFolder,
                                HORIZON_ENGINE_ROOT=self.m_sHorizonEngineRoot,
                                CMAKE_OSX_ARCHITECTURES=self.m_sProjectBuildArch) 

            HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
            result = subprocess.run(sCmd, shell=True)  

            if(result.returncode == 0):
                bSuccess = True
        reportFile.close()
        return bSuccess


    def buildMacOSXProject(self):
        return self.buildGenericProject()


    def generateIOSProject(self):
        #XCODE_ATTRIBUTE_ENABLE_BITCODE
        #cmake .. -DCMAKE_TOOLCHAIN_FILE=../../../toolchain/iOS.cmake -DIOS_PLATFORM=SIMULATOR
        #https://github.com/NativeScript/ios-runtime/blob/master/CMakeLists.txt
        bSuccess = False
        reportFile = open(self.m_sOutReportFilePath, 'a', encoding = 'utf-8')
        with HorizonBuildFileUtil.HorizonBuildFileUtil.pushd(self.m_sProjectIDERoot):

            xmldoc = minidom.parse(self.m_sConfig)
            self.m_sIOSSDKRoot = xmldoc.getElementsByTagName('IOSSDKRoot')[0].firstChild.nodeValue;
            self.m_sIOSSupportedPlatforms = xmldoc.getElementsByTagName('IOSSupportedPlatforms')[0].firstChild.nodeValue;
            self.m_sIOSEffectivePlatforms = xmldoc.getElementsByTagName('IOSEffectivePlatforms')[0].firstChild.nodeValue;
            self.m_sIOSEnableBitCode      = xmldoc.getElementsByTagName('IOSEnableBitCode')[0].firstChild.nodeValue;


            sCmd = 'cmake {PROJECT_BUILD_ROOT} \
            -DCMAKE_XCODE_ATTRIBUTE_SDKROOT="{XCODE_ATTRIBUTE_SDKROOT}" \
            -DCMAKE_XCODE_ATTRIBUTE_SUPPORTED_PLATFORMS="{XCODE_ATTRIBUTE_SUPPORTED_PLATFORMS}" \
            -DCMAKE_XCODE_EFFECTIVE_PLATFORMS="{XCODE_EFFECTIVE_PLATFORMS}" \
            -DCMAKE_XCODE_ATTRIBUTE_ENABLE_BITCODE={XCODE_ATTRIBUTE_ENABLE_BITCODE}    \
            -DCMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH=NO \
            -G "{CMAKE_GENERATOR}" \
            {PROJECT_GENERATED_EXTRA_FLAG} \
            -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={CMAKE_ARCHIVE_OUTPUT_DIRECTORY} \
            -DHORIZON_ENGINE_ROOT={HORIZON_ENGINE_ROOT}'

            #-DCMAKE_XCODE_ATTRIBUTE_ARCHS="arm64 armv7 x86_64" \
            #-DCMAKE_XCODE_ATTRIBUTE_VALID_ARCHS="arm64 armv7 x86_64" \
            #sIOSCMakeToolChainPath= os.path.abspath(self.m_sHorizonEngineRoot + "/cmake/ios-cmake/toolchain/iOS.cmake")
            sCmd = sCmd.format(
                                PROJECT_BUILD_ROOT=self.m_sProjectBuildRoot, 
                                CMAKE_GENERATOR=self.m_sCMakeGenerator, 
                                PROJECT_GENERATED_EXTRA_FLAG=self.m_sProjectGeneratedExtraFlag, 
                                CMAKE_ARCHIVE_OUTPUT_DIRECTORY=self.m_sCMakeArchiveOutputFolder,
                                HORIZON_ENGINE_ROOT=self.m_sHorizonEngineRoot,
                                XCODE_ATTRIBUTE_SDKROOT=self.m_sIOSSDKRoot,
                                XCODE_ATTRIBUTE_SUPPORTED_PLATFORMS=self.m_sIOSSupportedPlatforms,
                                XCODE_EFFECTIVE_PLATFORMS=self.m_sIOSEffectivePlatforms,
                                XCODE_ATTRIBUTE_ENABLE_BITCODE=self.m_sIOSEnableBitCode) 

            HorizonBuildFileUtil.HorizonBuildFileUtil.LogInfo(reportFile, sCmd)
            result = subprocess.run(sCmd, shell=True)  

            if(result.returncode == 0):
                bSuccess = True
        reportFile.close()
        return bSuccess


    def buildIOSProject(self):
        return self.buildGenericProject()

    def generateProject(self):
        if("win" in self.m_sProjectBuildPlatform.lower()):
            self.generateWindowsProject()               
        if("macosx" in self.m_sProjectBuildPlatform.lower()):
            self.generateMacOSXProject()    
        if("ios" in self.m_sProjectBuildPlatform.lower()):
            self.generateIOSProject()    
        if("android" in self.m_sProjectBuildPlatform.lower()):
            self.generateAndroidProject()     
    def buildProject(self):
        if("win" in self.m_sProjectBuildPlatform.lower()):
            self.buildWindowsProject()
        if("macosx" in self.m_sProjectBuildPlatform.lower()):
            self.buildMacOSXProject()    
        if("ios" in self.m_sProjectBuildPlatform.lower()):
            self.buildIOSProject()    
        if("android" in self.m_sProjectBuildPlatform.lower()):
            self.buildAndroidProject()      
              
    def execute(self): 
        HorizonBuildFileUtil.HorizonBuildFileUtil.EnsureDir(self.m_sOutReportFilePath)
        reportFile = open(self.m_sOutReportFilePath, 'w', encoding = 'utf-8')
        reportFile.truncate()
        reportFile.close()
        if(self.m_bClean == True):
            print("start clean project")
            try:
                print("remove folder:" + self.m_sProjectIDERoot)
                shutil.rmtree(self.m_sProjectIDERoot)
                sArchiveOutputFolder = os.path.abspath(self.m_sCMakeArchiveOutputFolder + "/" + self.m_sProjectBuildConfig + "/")

                print("remove folder:" + sArchiveOutputFolder)
                shutil.rmtree(sArchiveOutputFolder)
                print("clean project finished")
            except:
                pass 
        else:
            print("start build project")
            HorizonBuildFileUtil.HorizonBuildFileUtil.CreateDir(self.m_sProjectIDERoot)
            HorizonBuildFileUtil.HorizonBuildFileUtil.CreateDir(self.m_sCMakeArchiveOutputFolder)
            bSuccess = self.generateProject()

            if(bSuccess == False):
                raise Exception("Generate Project failed!!")

            if(self.m_bGenerateOnly == False):
                bSuccess = self.buildProject()
                if(bSuccess == False):
                    raise Exception("Build Project failed!!")

            #sCurrentProject = os.path.abspath(self.m_sProjectRoot + "/CurrentProject/")
            #os.symlink(self.m_sProjectIDERoot, sCurrentProject, True)
            #shutil.copytree(self.m_sProjectIDERoot, sCurrentProject)







       
      

      




