import argparse
import subprocess
import threading
import os
import time

verbosity_level: int = 0
ev_stop_showing_img: threading.Event = threading.Event()

def show_image(path: str):
    # fbi = subprocess.Popen(["fbi", path])
    fbi = subprocess.Popen(["viewnior", path])
    ev_stop_showing_img.wait()
    fbi.terminate()


def run_slideshow(webpages_dir: str, photos_dir: str):
    l_webpages: list[str] = []
    l_photos: list[str] = []

    if webpages_dir:
        l_webpages = [os.path.join(webpages_dir, contents) for contents in os.listdir(webpages_dir) if os.path.isfile(os.path.join(webpages_dir, contents))]
    if photos_dir:
        l_photos = [os.path.join(photos_dir, contents) for contents in os.listdir(photos_dir) if os.path.isfile(os.path.join(photos_dir, contents))]

    if(len(l_webpages) == 0):
        print("webpages dir is empty")
    if(len(l_photos) == 0):
        print("photos dir is empty")
    if(len(l_photos) == 0 and len(l_webpages) == 0):
        print("no files to show")
        return
    
    for file in l_webpages:
        print(f"showing {file}")
        th_show_image = threading.Thread(target=show_image, args=[file])
        th_show_image.start()
        time.sleep(2)
        ev_stop_showing_img.set()
        ev_stop_showing_img.clear()

def main():
    """Main entry point"""
    global verbosity_level

    parser = argparse.ArgumentParser(description="Present rnadom images + webpages uing fbi")
    parser.add_argument('-v', '--verbose', type=int, dest='verbose', help="verbosity level")
    parser.add_argument('-p', '--photos', action='append', dest='photos', nargs='+', help="photos directory")
    parser.add_argument('-w', '--webpages', action='append', dest='webpages', nargs='+', help="webpages directory")


    parser.add_argument("--test-single-file", type=str, dest="single_file")

    args = parser.parse_args()

    single_file: str = ""
    photos_dir: str = ""
    webpages_dir: str = ""

    if args.verbose:
        verbosity_level = args.verbose

    if args.photos:
        photos_dir = str(args.photos)
    if args.webpages:
        webpages_dir = str(args.webpages[0][0])
    
    if args.single_file:
        single_file = str(args.single_file)

    run_slideshow(webpages_dir, photos_dir)


if __name__ == '__main__':
    main()
