#!.env/bin/python
# -*- coding: UTF-8 -*- #
import sys

# Check that we are running inside a virtualenv.
if not hasattr(sys, 'real_prefix'):
    print("Must run inside virtualenv.")
    sys.exit(1)

from units3.main import app

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",
                        help="start in debug mode",
                        action="store_true")

    parser.add_argument("-v", "--visible",
                        help="make server externally visible",
                        action="store_true")

    args = parser.parse_args()

    host = '0.0.0.0' if args.visible else '127.0.0.1'

    app.run(host=host, debug=args.debug)
