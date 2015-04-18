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
# Requires: Python 2.7 or later
# 

import os
import os.path
import subprocess

src_dirpath = '/Volumes/Fireman/TORRENTS'
dst_dirpath = '/Volumes/Fireman/TORRENTS - ENCODED'


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
    return filename.split('.', 1)[0]

def is_movie_file(filename):
    ext = filename.rsplit('.', 1)[-1]
    return ext in ['mp4', 'm4v', 'mkv', 'avi', 'ogm']

def make_encoded_filename(src_filename):
    non_ext = src_filename.rsplit('.', 1)[0]
    return non_ext + '.m4v'


def sync_directories(src_dirpath, dst_dirpath):
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
            else:
                # Symlink it
                print('SYMLINK: ' + src_filepath)
                dst_filepath = os.path.join(dst_dirpath, src_filename)
                os.symlink(src_filepath, dst_filepath)

    # Sync folders in this directory
    for src_filename in src_filenames:
        src_filepath = os.path.join(src_dirpath, src_filename)
        if not os.path.isdir(src_filepath):
            continue
        dst_filepath = os.path.join(dst_dirpath, src_filename)
        
        if not os.path.exists(dst_filepath):
            print('MKDIR: ' + src_filepath)
            os.mkdir(dst_filepath)
        print('ENTER: ' + src_filepath)
        sync_directories(src_filepath, dst_filepath)

def encode(src_filepath, dst_filepath):
    # Encode to the output directory and save the encode log
    log_filepath = dst_filepath + '.part.log.txt'
    try:
        with open(log_filepath, 'wb') as log_file:
            subprocess.check_call(
                ['hbencode', '--auto', '-o', dst_filepath + '.part', src_filepath],
                stdout=log_file,
                stderr=subprocess.STDOUT)
    except:
        # Error while encoding? Leave the part file and the log file
        pass
    else:
        # Success? Move the part file into place and remove the log
        os.rename(dst_filepath + '.part', dst_filepath)
        os.remove(log_filepath)

sync_directories(src_dirpath, dst_dirpath)
