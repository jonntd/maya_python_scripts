import os, shutil, stat
import maya.cmds as cmds
from P4 import P4,P4Exception


class studioPerforce(object):
    def __init__(self, prefix='', local=''):
        self.p4 = P4()
        self.p4.exception_level = 2
        self.perforcePrefix = prefix
        self.perforceLocal = local

    #----------------------------------------------------------------------
    def findAsset(self, extension='*.mb', folder='...', count=10):
        self.p4.connect()
                
        query = self.perforcePrefix + folder + '/' + extension
    
        try:
            res = self.p4.run('files', '-e', '-m ' + str(count), query)
        except P4Exception:
            res = []
        
        self.p4.disconnect()
        
        return res

    #----------------------------------------------------------------------
    def getAssetTree(self, folder='...', extension=''):
        self.p4.connect()
            
        query = self.perforcePrefix + folder + extension
        res = self.p4.run('files', '-e', query)
    
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def convertFileListToTree(self, data):
        out = {}
        for current in data:
            data = current['depotFile'].split('/')[4:]
            level = out
            for cur in data:
                if cur not in level:
                    level[cur] = {}
                level = level[cur]
        
        return out

    #----------------------------------------------------------------------
    def getLatestRevision(self, path, force=False):
        if not os.path.isfile(path):
            force = True
        
        self.p4.connect()
        
        res = []
        errors = []
        warnings = []
        try:
            if force:
                res = self.p4.run('sync', '-f', path)
            else:
                res = self.p4.run('sync', path)
        except P4Exception:
            for e in self.p4.errors:
                errors.append(e)
            for e in self.p4.warnings:
                warnings.append(e)
        
        self.p4.disconnect()
    
        return {'result': res, 'errors': errors, 'warnings': warnings}

    #----------------------------------------------------------------------
    def syncReferences(self, filename, files=False, lenFnc=None, countFnc=None, types=[], statusFnc=None):
        newFile = '/'.join(filename.split('/')[:-1]) + '/...'
        if files:
            data = self.getLatestRevision(newFile)
            if statusFnc:
                statusFnc('sync: ' + newFile)
        else:
            data = self.getLatestRevision(filename)
            for curType in types:
                self.getLatestRevision(newFile + '.' + curType)
                if statusFnc:
                    statusFnc('sync: ' + newFile)

        refs = cmds.file(filename, q=True, reference=True)
        refs = [str(x) for x in refs]

        data = [{'file': filename, 'ref': refs, 'error': data['errors'], 'warning': data['warnings']}]

        if lenFnc:
            lenFnc(len(refs))

        for num, ref in enumerate(refs):
            data.append(self.syncReferences(ref, files, types=types, statusFnc=statusFnc)[0])

            if countFnc:
                countFnc(num)

        return data

    #----------------------------------------------------------------------
    def getCheckedOutData(self, filename):
        self.p4.connect()
        
        res = []
        try:
            res = self.p4.run('opened', '-a', filename)
        except P4Exception:
            for e in self.p4.errors:
                print(e)
            for e in self.p4.warnings:
                print(e)
        
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def checkout(self, filename):
        self.p4.connect()
            
        res = []
        try:
            res = self.p4.run('edit', filename)
        except P4Exception:
            for e in self.p4.errors:
                print(e)
            for e in self.p4.warnings:
                print(e)
            
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def submit(self, filename, description):
        self.p4.connect()
                
        res = []
        try:
            res = self.p4.run('submit', '-f revertunchanged', '-d '+description, filename)
        except P4Exception:
            for e in self.p4.errors:
                print(e)
            for e in self.p4.warnings:
                print(e)
                
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def revert(self, filename):
        self.p4.connect()
                
        res = []
        try:
            res = self.p4.run('revert', filename)
        except P4Exception:
            for e in self.p4.errors:
                print(e)
            for e in self.p4.warnings:
                print(e)
                
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def add(self, filename):
        self.p4.connect()
                
        res = []
        try:
            res = self.p4.run('add', filename)
        except P4Exception:
            for e in self.p4.errors:
                print(e)
            for e in self.p4.warnings:
                print(e)
                
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def syncPreview(self, folder='...', extension='.png'):
        self.p4.connect()

        res = []
        query = self.perforcePrefix + folder + extension
        try:
            res = self.p4.run('sync', query)
        except P4Exception:
            pass
    
        self.p4.disconnect()

        return res

    #----------------------------------------------------------------------
    def getCurrentUser(self):
        return self.p4.user

    #----------------------------------------------------------------------
    def copyFileToRightFolder(self, previewFile, curSceneName, preview='/', description='update'):
        # set right folder for file
        previewExt = previewFile.split('.')[-1]
        curFileName = curSceneName.split('/')[-1].split('.')[0] + '.' + previewExt
        previewPath = '/'.join(curSceneName.split('/')[:-1]) + preview
        destName = previewPath + curFileName
        
        # check file in destination folder delete and copy new
        newFile = True
    
        if previewFile != destName:
            self.getLatestRevision(destName, True)
    
            if os.path.isfile(destName):
                data = self.checkout(destName)
                os.chmod(destName, stat.S_IWRITE)
                os.remove(destName)
                if data:
                    newFile = False
        
            if not os.path.isdir(previewPath):
                os.makedirs(previewPath)
        
            shutil.copy2(previewFile, destName)
    
        if newFile:
            self.add(destName)
    
        self.submit(destName, description)
    
        return destName

    #----------------------------------------------------------------------
    def getMyCheckoutedFiles(self, folder='...', extension='.mb'):
        user = self.getCurrentUser()
        queryString = self.perforcePrefix + folder + extension
    
        self.p4.connect()
            
        res = self.p4.run('opened', '-u', user, queryString)
        
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def getAllUsers(self):
        self.p4.connect()
            
        res = self.p4.run('users')
    
        self.p4.disconnect()
    
        return res

    #----------------------------------------------------------------------
    def getWorspace(self, user):
        self.p4.connect()
            
        res = self.p4.run('workspaces', '-u', user)
    
        self.p4.disconnect()
    
        return res
