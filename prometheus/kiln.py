import optparse
import sys

def main(prog_args=None):
    if prog_args is None:
        prog_args = sys.argv

    parser = optparse.OptionParser()
    parser.usage = """Prometheus"""
    #parser.add_option("-h", "--help", dest="help", help="help")

    opt, args = parser.parse_args(prog_args)

    if False: # some incorrect argument
        parser.print_help()

if __name__ == '__main__':
    main()
