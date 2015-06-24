#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Keeps the files in a source and destination directory in sync.
#
# In the case of movie files in the source directory,
# they will be encoded using hbencode and dropped in the destination directory.
# 
# In the case of other file types in the source directory,
# the equivalent files in the destination directory will be symlinked
# to the source directory.
# 
# Files in the destination directory that are not present
# in the source directory will be ignored.
# 
# Certain files in the source directory will be ignored,
# such as invisible files and .part files.
# 

import getopt
import os
import os.path
import subprocess
import sys
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ------------------------------------------------------------------------------
# Main

PREFERENCES_FILEPATH = os.path.join(os.path.expanduser('~'), '.direncode_prefs')

def main(args):
    # Parse arguments
    opts, args = getopt.getopt(args, 'w', ['watch'])
    
    if len(args) != 2:
        exit("""syntax: direncode.py [<options>] SOURCE_DIR DESTINATION_DIR
    
    Options:
        -w, --watch             Continuously watch the source directory
                                and continue synchronizing both directories.
    """)
    src_dirpath, dst_dirpath = args
    
    watch = False
    for (k, v) in opts:
        if k in ['-w', '--watch']:
            watch = True
    
    # Load preferences
    preferences = load_preferences(PREFERENCES_FILEPATH)
    
    # Locate hbencode.py
    global HBENCODE
    HBENCODE = preferences.get('hbencode', None)
    while True:
        if HBENCODE is None:
            HBENCODE = raw_input('Path to hbencode.py: ')
        
        if not os.path.exists(HBENCODE):
            print 'hbencode.py not found at: %s' % HBENCODE
            HBENCODE = None
            continue
        else:
            break
    
    # Save preferences, in case they were updated
    preferences['hbencode'] = HBENCODE
    save_preferences(PREFERENCES_FILEPATH, preferences)
    
    if not watch:
        sync_directories(src_dirpath, dst_dirpath)
    else:
        # Queue up an initial directory sync operation
        global watched_dir_changed
        watched_dir_changed = True
        
        class DirectoryChangeEventHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                global watched_dir_changed
                watched_dir_changed = True
        
        # Start watching source directory for changes
        observer = Observer()
        observer.schedule(
            DirectoryChangeEventHandler(), src_dirpath,
            recursive=True)
        observer.start()
        
        # Wait until interrupted by keyboard
        try:
            while True:
                if watched_dir_changed:
                    # (Keep all directory sync operations on the same thread)
                    while sync_directories(src_dirpath, dst_dirpath):
                        pass
                    watched_dir_changed = False
                    print('WATCHING: ' + src_dirpath)
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def sync_directories(src_dirpath, dst_dirpath):
    changed = False
    
    src_filenames = [fn for fn in os.listdir(src_dirpath) if not is_ignored_filename(fn)]
    dst_filenames = [fn for fn in os.listdir(dst_dirpath) if not is_ignored_filename(fn)]
    
    # Sync files in this directory
    dst_fileids = [make_fileid(fn) for fn in dst_filenames]
    for src_filename in src_filenames:
        src_filepath = os.path.join(src_dirpath, src_filename)
        if os.path.isdir(src_filepath):
            continue
        
        src_fileid = make_fileid(src_filename)
        if src_fileid not in dst_fileids:
            if is_movie_file(src_filename):
                # Encode it
                print('ENCODE: ' + src_filepath)
                dst_filepath = os.path.join(dst_dirpath, make_encoded_filename(src_filename))
                encode(src_filepath, dst_filepath)
                changed = True
            else:
                # Symlink it
                print('SYMLINK: ' + src_filepath)
                dst_filepath = os.path.join(dst_dirpath, src_filename)
                os.symlink(src_filepath, dst_filepath)
                changed = True

    # Sync folders in this directory
    for src_filename in src_filenames:
        src_filepath = os.path.join(src_dirpath, src_filename)
        if not os.path.isdir(src_filepath):
            continue
        dst_filepath = os.path.join(dst_dirpath, src_filename)
        
        if not os.path.exists(dst_filepath):
            print('MKDIR: ' + src_filepath)
            os.mkdir(dst_filepath)
            changed = True
        changed = sync_directories(src_filepath, dst_filepath) or changed
    
    return changed


def encode(src_filepath, dst_filepath):
    global HBENCODE
    
    # Encode to the output directory and save the encode log
    log_filepath = dst_filepath + '.part.log.txt'
    try:
        with open(log_filepath, 'wb') as log_file:
            try:
                subprocess.check_call(
                    [HBENCODE, '--auto', '-o', dst_filepath + '.part', '-x', '-f mp4', src_filepath],
                    stdout=log_file,
                    stderr=subprocess.STDOUT)
                if not os.path.exists(dst_filepath + '.part'):
                    raise AssertionError('hbencode exited successfully but did not generate output file: ' + dst_filepath)
            except Exception as e:
                # Log any exceptions that occur
                traceback.print_exc(file=log_file)
                raise
    except:
        # Error while encoding? Leave the part file and the log file.
        # The residual files will suppress repeated encode operations.
        pass
    else:
        # Success? Move the part file into place and remove the log
        os.rename(dst_filepath + '.part', dst_filepath)
        os.remove(log_filepath)

# ------------------------------------------------------------------------------
# Filename Manipulations

def is_ignored_filename(filename):
    if filename.startswith('.'):
        return True
    if filename == 'Icon\r':
        return True
    if filename == 'Thumbs.db':
        return True
    if filename.endswith('.part'):
        return True
    return False


def make_fileid(filename):
    non_ext = filename.rsplit('.', 1)[0]
    return non_ext


def is_movie_file(filename):
    ext = filename.rsplit('.', 1)[-1]
    return ext in ['mp4', 'm4v', 'mkv', 'avi', 'ogm']


def make_encoded_filename(src_filename):
    non_ext = src_filename.rsplit('.', 1)[0]
    return non_ext + '.m4v'

# ------------------------------------------------------------------------------
# Preferences

def load_preferences(preferences_filepath):
    preferences = {}
    
    if not os.path.exists(preferences_filepath):
        return preferences
    
    with open(preferences_filepath, 'rb') as preferences_file:
        for line in preferences_file:
            (k, v) = line.strip('\r\n').split('=', 1)
            preferences[k] = v
    
    return preferences


def save_preferences(preferences_filepath, preferences):
    with open(preferences_filepath, 'wb') as preferences_file:
        for (k, v) in preferences.iteritems():
            preferences_file.write(k)
            preferences_file.write('=')
            preferences_file.write(v)
            preferences_file.write('\n')

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])
