import os
import time
import sys
import shutil
import argparse

# for repeated use, build an image and do not run the git commands
os.system('apt update && apt-get install -y python python-dev python-pip build-essential swig git libpulse-dev libasound2-dev portaudio19-dev')
# because there is an issue in librosa dependency on numba, removing the un needed dependency line
os.system("export liborsa=$(pip3 show librosa | grep Location | cut -f 2 -d ' ') && sed -i '/from numba.decorators import jit as optional_jit/d' ""$liborsa/librosa/util/decorators.py""")

sys.path.append('.')
from keras_audio.library.cifar10 import Cifar10AudioClassifier

labels = [100,90,80,70,60,50,40,30,20,10]

# note the following parameter is passed:  '--data_dir': ds.as_mount()
parser = argparse.ArgumentParser()
parser.add_argument("--data_dir")
args = parser.parse_args()

def load_path_labels(sourcePath):
    # here we are expecting file in the format XXXXXXX-N.wav, where N is the label
    pairs = []
    for f in os.listdir(sourcePath):
        try:
            if str(f.split('.')[1]).lower() == 'wav':          # only process wav files
                label = int(f.split('.')[0].split('-')[1])
                path = sourcePath + '/' + f
                pairs.append((path, labels.index(label)))
        except:
            print('error with: ' + str(f))
    return pairs

def main():
    audio_path_label_pairs = load_path_labels(str(args.data_dir))
    print('loaded: ' + str(len(audio_path_label_pairs)) + ' files')
 
    classifier = Cifar10AudioClassifier()
    batch_size = 8
    epochs = 50000
    classifier.fit(audio_path_label_pairs=audio_path_label_pairs, model_dir_path='model', batch_size=batch_size, epochs=epochs)

    #zipping compiled model and copy back to mounted blob storage
    shutil.make_archive(base_name='model', format='zip', base_dir='model')
    os.system('cp -r model.zip ' + args.data_dir + '/' + str(int(time.time() * 1000)) + 'model.zip')

    # copying the model contents to the output directory
    os.system('cp -r ./model outputs')

if __name__ == '__main__':
    main()
