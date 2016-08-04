import skimage.io
import os
import glob


def save_image(imagefile, x1, y1, x2, y2, savedir=None):
    img = skimage.io.imread(imagefile)  # H x W x Channel
    crop_img = img[y1:y2, x1:x2]
    filename = os.path.splitext(os.path.basename(imagefile))[0]
    ext = os.path.splitext(os.path.basename(imagefile))[1]
    output_filename = "{0}.{1},{2}-{3},{4}{5}".format(filename, x1, y1, x2, y2, ext)
    if savedir:
        output_filename = savedir + "/" + output_filename
    skimage.io.imsave(output_filename, crop_img)
    return output_filename


def clear_images(imagefile, savedir=None):
    filename = os.path.splitext(os.path.basename(imagefile))[0]
    if savedir:
        filepattern = savedir + "/" + filename + ".*.jpg"
    else:
        filepattern = filename + ".*.jpg"
    print filepattern
    [os.remove(f) for f in glob.glob(filepattern)]
