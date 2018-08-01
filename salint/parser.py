# -*- coding: utf-8 -*-
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Lint Salt States.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='*',
                        help="paths to search for sls files in")
    return parser.parse_args()
