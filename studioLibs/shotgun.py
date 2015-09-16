from shotgun_api3 import Shotgun
from datetime import datetime


class studioShotgun(object):
    def __init__(self, path, name, key, project):
        self.SERVER_PATH = path
        self.SCRIPT_NAME = name     
        self.SCRIPT_KEY = key
        self.project_id = project
        self.sg = Shotgun(self.SERVER_PATH, self.SCRIPT_NAME, self.SCRIPT_KEY)

    #----------------------------------------------------------------------
    ## set Project id by ID
    def setProjectId(self, newId):
        self.project_id = newId

    #----------------------------------------------------------------------
    ## set Project id by ID
    def setProjectName(self, name):
        newId = 0
        projects = self.sg.find('Project', [], ['name'])
        for project in projects:
            if project['name'] == name:
                newId = project['id']

        self.project_id = newId

    #----------------------------------------------------------------------
    ## find asset by name
    def findAssetByName(self, name):
        fields = ['id', 'code', 'sg_asset_type', 'tasks']
        filters = [['project', 'is', {'type': 'Project', 'id': self.project_id}], ['code', 'is', name]]
        
        result = self.sg.find('Asset', filters, fields)
    
        return result
    
    #----------------------------------------------------------------------
    ## find shot by name
    def findShotByName(self, episode, shot):
        fields = ['id', 'code', 'sg_asset_type', 'tasks', 'sg_sequence']
        filters = [['project', 'is', {'type': 'Project', 'id': self.project_id}], ['code', 'is', shot]]
        
        result = self.sg.find('Shot', filters, fields)
    
        for x in result:
            name = x['sg_sequence']['name'].split('_')[0]
            if name == episode:
                return x
    
        return []

    #----------------------------------------------------------------------
    ## upload thumbnail to asset
    def uploadThumbnail(self, asset, thumbnail):
        upload = 0
        asset = self.findAssetByName(asset)
        if asset:
            upload = self.sg.upload_thumbnail("Asset", asset[0]['id'], thumbnail)
    
        return upload

    #----------------------------------------------------------------------
    ## create new asset
    def createAsset(self, asset, assetType, template, assetFile='', description=''):
        ## find asset
        asset = self.findAssetByName(asset)
        
        if not asset:
            ## create asset + task template
            filters = [['code', 'is', template]]
            template = self.sg.find_one('TaskTemplate', filters)
            
            data = {'project': {'type': 'Project', 'id': self.project_id}, 
                    'code': asset,
                    'description': description, 
                    'sg_asset_type': assetType, 
                    'sg_url_perforce': assetFile, 
                    'task_template': template}
    
            asset = self.sg.create('Asset', data)
    
        return asset

    #----------------------------------------------------------------------
    ## update file path in asset
    def updateAssetFilePath(self, asset, filename):
        asset = self.findAssetByName(asset)
    
        data = {'sg_url_perforce': filename}
        asset = self.sg.update("Asset", asset[0]['id'], data)
    
        return asset

    #----------------------------------------------------------------------
    ## create new version
    def createVersion(self, shotId, taskId, userId, filename, comment=''):
        curTime = datetime.now().strftime('%Y.%m.%d_%H.%M')
        fname = str(filename.split('/')[-1].split('.')[0]) + '_' + curTime
    
        data = {'project': {'type': 'Project', 'id': self.project_id},
                'code': fname,
                'description': comment,
                'sg_status_list': 'rev',
                'entity': {'type': 'Shot', 'id': shotId},
                'sg_task': {'type': 'Task', 'id': taskId},
                'user': {'type': 'HumanUser', 'id': userId}}
        
        result = self.sg.create('Version', data)
        
        upload = self.sg.upload('Version', result['id'], filename, 'sg_uploaded_movie')
    
        return [result, upload]

    #----------------------------------------------------------------------
    ## get user data from shotgum
    def getUserData(self, user):
        filters = [['login', 'is', user]]
        user = self.sg.find('HumanUser', filters)

        if user:
            return user[0]
        else:
            return []

    #----------------------------------------------------------------------
    ## get all user from project
    def getAllUsers(self):
        fields = ['id', 'login', 'name', 'projects', 'department']
        filters = [['projects', 'is', {'type': 'Project', 'id': self.project_id}]]
        users = self.sg.find('HumanUser', filters, fields)
    
        return users
