from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")
asd(r"d:/user_files/hussain.parsaiyan/Documents/trunk/work/tactic")
import app.util as util
from imaya import FileInfo as fi
import imaya as mi
reload(util)

from iutil import profile
from iutil import networkmaps as nmaps
from iutil import symlinks as syml

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
        try:
            filename = op.normpath(
                    util.filename_from_snap(snap, mode = 'client_repo')
                    ).lower()
            f_to_snap[filename] = snap
        except IndexError:
            continue
    return f_to_snap

def check_scene_old(proj):

    refs = mi.get_reference_paths()

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
                    try:
                        filename = util.filename_from_snap(snap, mode = 'client_repo')
                        status[ref] = filename
                        version = snap['version']
                    except IndexError:
                        continue
                    
    return status
 
def check_scene(proj):

    status = {}

    netmaps = nmaps.getNetworkMaps()
    server = util.get_server()
    basedir = server.get_base_dirs()['win32_client_repo_dir']
    symlmaps = syml.getSymlinks(basedir)
    refs = mi.get_reference_paths()

    for ref, path in refs.items():
        # either we have p: or //dbserver
        path = op.normpath(path)
        npath = nmaps.translateUNCtoMapped(path, maps=netmaps)
        sympath = syml.translatePath(npath, maps=symlmaps, reverse=True)
        try:
            relpath = op.relpath(sympath, basedir)
        except ValueError:
            continue
        if not relpath.startswith('..'):

            dirname, basename = op.split(relpath)

            fileobj = server.query('sthpw/file',
                    filters = [('project_code', proj),
                        ('relative_dir', dirname.replace('\\', '/')),
                        ('file_name', basename)], single = True)

            if not fileobj:
                continue

            snapshot = server.query('sthpw/snapshot', filters=[('code',
                fileobj['snapshot_code'])], single=True)

            latest_snapshot = server.get_snapshot(snapshot['__search_key__'],
                    context=snapshot['context'], version=-1)

            if latest_snapshot['code'] != snapshot['code']:
                try:
                    filename = util.get_filename_from_snap(latest_snapshot, mode='client_repo')
                    status[ref] = filename
                    continue
                except IndexError:
                    pass

            status[ref] = False

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



