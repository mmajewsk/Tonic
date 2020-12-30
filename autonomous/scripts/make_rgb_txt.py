import os
import optparse

def create_rgb_file(folder, verbose=False):
    files = os.listdir(folder)
    pics = filter(lambda x: ".jpg" in x, files)
    pics = sorted(pics)
    d = {}
    pics = map(lambda x: (x, x.split("_")[1][:-4]), pics)
    with open(args[0] + "/rgb.txt", 'w') as f:
        for path, timestamp in pics:
            if d.get(timestamp, None) is None:
                d[timestamp] = True
                f.write("{} {} \n".format(timestamp[:17], path))

if __name__=="__main__":
    parser = optparse.OptionParser()
    (options, args) = parser.parse_args()
    create_rgb_file(args[0])

