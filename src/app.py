#!/usr/bin/env python

import os

import cbplims

if __name__ == "__main__":
    extra_dirs = ['cbplims', ]
    extra_files = set(extra_dirs[:])
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename) and filename[-3:] == '.py':
                    extra_files.add(filename)
                    extra_files.add(dirname)

    debug = True if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'dev' else False
    cbplims.run(host='0.0.0.0', port=5000, use_reloader=debug, debug=debug, extra_files=extra_files)
