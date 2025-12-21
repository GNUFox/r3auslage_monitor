import argparse
import subprocess
import threading

verbosity_level: int = 0
ev_stop_showing_img: threading.Event = threading.Event()

def show_image(path: str):
    # fbi = subprocess.Popen(["fbi", path])
    fbi = subprocess.Popen(["viewnior", path])
    ev_stop_showing_img.wait()
    fbi.terminate()


def main():
    """Main entry point"""
    global verbosity_level

    parser = argparse.ArgumentParser(description="Present rnadom images + webpages uing fbi")
    parser.add_argument('-v', '--verbose', type=int, dest='verbose', help="verbosity level")

    parser.add_argument("--test-single-file", type=str, dest="single_file")

    args = parser.parse_args()

    single_file: str = ""

    if args.verbose:
        verbosity_level = args.verbose
    
    if args.single_file:
        single_file = str(args.single_file)
    
    th_show_image = threading.Thread(target=show_image, args=[single_file])
    th_show_image.start()

    u = input("before stop")
    ev_stop_showing_img.set()
    u = input("after stop")


if __name__ == '__main__':
    main()
