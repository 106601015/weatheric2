import os
import imageio

# make gif for all image in each subfolder
def all_subfolder(duration=0.2):
    for dirPath, dirNames, fileNames in os.walk(os.getcwd()):
        if dirPath == os.getcwd():continue
        print(dirPath, dirNames, fileNames)

        images = []
        for filename in fileNames:
            # you can set string conditions to control source gif set
            # ex: if dirPath.split('/')[-1]) == 'temp'  and  filename.split('_')[-1] == '?????.png': ...
            images.append(imageio.imread(os.path.join(dirPath, filename)))
        imageio.mimsave(os.path.join(dirPath, '{}.gif'.format(dirPath.split('/')[-1])), images, duration = duration) # <-- 0.2s delay


def gif_subfolder(duration=0.2):
    for dirPath, dirNames, fileNames in os.walk(os.path.join(os.getcwd(), 'do_gif')):
        images = []
        for filename in fileNames:
            images.append(imageio.imread(os.path.join(dirPath, filename)))
        imageio.mimsave(os.path.join(os.getcwd(), 'gif.gif'), images, duration = duration) # <-- 0.2s delay

def gif_help_to_do(duration=0.2):
    for dirPath, dirNames, fileNames in os.walk(os.path.join(os.getcwd(), 'help_to_do')):
        print('dirPath:', dirPath)

        if dirPath == os.path.join(os.getcwd(), 'help_to_do'):continue
        # dirPath=dirPath2
        for dirPath2, dirNames2, fileNames2 in os.walk(dirPath):
            images = []
            for filename in fileNames2:
                images.append(imageio.imread(os.path.join(dirPath, filename)))
            imageio.mimsave(os.path.join(os.getcwd(), '{}.gif'.format(dirPath2.split('\\')[-1])), images, duration = duration) # <-- 0.2s delay

if __name__ == '__main__':
    #gif_subfolder(duration=1.5)
    #all_subfolder()
    gif_help_to_do(duration=0.2)