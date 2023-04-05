import glob
import ntpath
import os
import sys

from PIL import Image

# requires pillow 9.0.1+


def main(source, dest):
    ext = ["*.bmp", "*.png"]
    for e in ext:
        files = os.path.join(source, "**", e)
        print(files)
        for file in glob.glob(files, recursive=True):
            head, tail = ntpath.split(file)
            sub_dir = head.split(os.sep)[-1]
            if "xyz" in head:
                sub_dir = os.path.join(head.split(os.sep)[-2], sub_dir)
            image = Image.open(file)
            image = image.resize((256, 256), Image.Dither.NONE)
            dest_dir = os.path.join(dest, sub_dir)
            os.makedirs(dest_dir, exist_ok=True)
            file_name = os.path.join(dest_dir, tail)
            image.save(file_name)


if __name__ == "__main__":
    # main(sys.argv[1], sys.argv[2])
    # src = r"c:\Users\sebastian\Documents\Unreal Projects\VRNetzer_Backend\static\MAPS"
    # dest = r"c:\Users\sebastian\Documents\Unreal Projects\VRNetzer_Backend\static\NewMaps"
    src = "/Users/till/Documents/Playground/VRNetzer_Backend/static/maps/cartoons_ss_coloring"
    dest = "/Users/till/Documents/Playground/VRNetzer_Backend/static/maps/cartoons_ss_coloring_256"
    main(src, dest)
