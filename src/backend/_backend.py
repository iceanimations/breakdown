from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")
asd(r"d:/user_files/hussain.parsaiyan/Documents/trunk/work/tactic")
import app.util as util
from imaya import FileInfo as fi
reload(util)


import pymel.core as pc
import os.path as op
import json

def get_snapshot_list(assets):
    snaps = []
    map(snaps.extend, map(util.get_snapshot_from_sobject,
                         assets))
    return snaps

def map_filename_to_snapshot(snaps):

    f_to_snap = {}
    
    for snap in snaps:
        print snap
        f_to_snap[op.normpath(
            util.filename_from_snap(snap,
                                    mode = 'client_repo')).lower()
                  ] = snap
    return f_to_snap

def reference_paths():
    '''
    @return: {refNode: path} of all level one scene references
    '''
    refs = {}
    for ref in pc.listReferences():
        refs[ref] = str(ref.path)
    return refs

def check_scene(proj):

    refs = reference_paths()

    # {ref_node: False(if ref stale)|path of upto date}
    status = {}
    
    assets = retrieve_assets()
    
    snaps = get_snapshot_list(assets)
    snap_files = map_filename_to_snapshot(snaps)

    for ref in refs:
        cur_snap = snap_files.get(op.normpath(refs[ref]).lower())
        if not cur_snap:
            continue
        process = cur_snap['process'].lower()
        context = cur_snap['context'].lower()
        search_type = cur_snap['search_type'].lower()
        version = cur_snap['version']
        search_code = cur_snap['search_code']
        status[ref] = False
        for snap in snaps:
            
            if (process == snap['process'].lower() and
                context == snap['context'].lower() and
                search_type == snap['search_type'].lower() and
                search_code == snap['search_code']):
                if snap['version'] > version:
                    status[ref] = util.filename_from_snap(snap, mode = 'client_repo')
                    version = snap['version']
                    
    return status

def retrieve_assets():
    '''
    @return: list of TACTIC asset search keys
    '''

    # assets list to be returned
    assets = []
    
    # tactic fileInfo dict
    raw_tactic = fi.get('TACTIC')
    if raw_tactic:
        tactic = json.loads(raw_tactic)
    else:
        return assets
    
    server = util.get_server()
        
    for asset in tactic.get('assets'):
        
        assets.append(server.build_search_key(
            asset.get('search_type'),
            asset.get('search_code'),
            project_code = asset.get('project_code')))
    return assets



def change_ref(node, newPath):
    return node.load(newFile = newPath)





