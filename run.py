#!.env/bin/python
# -*- coding: UTF-8 -*- #
import sys

if not hasattr(sys, 'real_prefix'):
    print("Must run inside virtualenv.")
    sys.exit(1)

from units3.main import app

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="start in debug mode",
                        action="store_true")
    args = parser.parse_args()

    app.run(debug=args.debug)
