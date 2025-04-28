import torch
import GNPassGAN.tflib as lib
import os, sys
sys.path.append(os.getcwd())
import time
import pickle
import random
import numpy as np
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import GNPassGAN.tflib.plot
from sklearn.preprocessing import OneHotEncoder
import GNPassGAN.utils
import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input-dir', '-i',
                        default='GNPassGAN/output',
                        dest='input_dir',
                        help='Trained model directory. The --output-dir value used for training.')


    parser.add_argument('--output', '-o',
                        default='GNPassGAN/samples.txt',
                        help='File path to save generated samples to (default: samples.txt)')

    parser.add_argument('--num-samples', '-n',
                        type=int,
                        default=50,
                        dest='num_samples',
                        help='The number of password samples to generate (default: 100000000)')

    parser.add_argument('--batch-size', '-b',
                        type=int,
                        default=64,
                        dest='batch_size',
                        help='Batch size (default: 64).')
    
    parser.add_argument('--seq-length', '-l',
                        type=int,
                        default=12,
                        dest='seq_length',
                        help='The maximum password length. Use the same value that you did for training.')
    
    parser.add_argument('--layer-dim', '-d',
                        type=int,
                        default=128,
                        dest='layer_dim',
                        help='The hidden layer dimensionality for the generator. Use the same value that you did for training (default: 128)')
    
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        parser.error('"{}" folder doesn\'t exist'.format(args.input_dir))


    if not os.path.exists(os.path.join(args.input_dir, 'charmap.pickle')):
        parser.error('charmap.pickle doesn\'t exist in {}, are you sure that directory is a trained model directory'.format(args.input_dir))

    if not os.path.exists(os.path.join(args.input_dir, 'charmap_inv.pickle')):
        parser.error('charmap_inv.pickle doesn\'t exist in {}, are you sure that directory is a trained model directory'.format(args.input_dir))

    return args
# ==================Definition Start======================
class ResBlock(nn.Module):

    def __init__(self):
        super(ResBlock, self).__init__()

        self.res_block = nn.Sequential(
            nn.ReLU(True),
            nn.Conv1d(args.layer_dim, args.layer_dim, 5, padding=2),#nn.Linear(DIM, DIM),
            nn.ReLU(True),
            nn.Conv1d(args.layer_dim, args.layer_dim, 5, padding=2),#nn.Linear(DIM, DIM),
        )

    def forward(self, input):
        output = self.res_block(input)
        return input + (0.3*output)


class Generator(nn.Module):

    def __init__(self):
        super(Generator, self).__init__()

        self.fc1 = nn.Linear(128, args.layer_dim*args.seq_length)
        self.block = nn.Sequential(
            ResBlock(),
            ResBlock(),
            ResBlock(),
            ResBlock(),
            ResBlock(),
        )
        self.conv1 = nn.Conv1d(args.layer_dim, len(charmap), 1)

    def forward(self, noise):
        output = self.fc1(noise)
        output = output.view(-1, args.layer_dim, args.seq_length) # (BATCH_SIZE, DIM, SEQ_LEN)
        output = self.block(output)
        output = self.conv1(output)
        output = output.transpose(1, 2)
        shape = output.size()
        output = output.contiguous()
        output = output.view(args.batch_size*args.seq_length, -1)
        output = torch.tanh(output)
        return output.view(shape) # (BATCH_SIZE, SEQ_LEN, len(charmap))
        
def generate_samples(netG):
    noise = torch.randn(args.batch_size, 128)
    if use_cuda:
        noise = noise.cuda(gpu)
    with torch.no_grad():
            noisev = noise.cuda()
    samples = netG(noisev)
    samples = samples.view(-1, args.seq_length, len(charmap))
    # print samples.size()

    samples = samples.cpu().data.numpy()

    samples = np.argmax(samples, axis=2)
    decoded_samples = []
    for i in range(len(samples)):
        decoded = []
        for j in range(len(samples[i])):
            decoded.append(inv_charmap[samples[i][j]])
        decoded_samples.append(tuple(decoded))
    return decoded_samples

# ==================Definition End======================
args = parse_args()
# Dictionary
with open(os.path.join(args.input_dir, 'charmap.pickle'), 'rb') as f:
    charmap = pickle.load(f, encoding='latin1')

# Reverse-Dictionary
with open(os.path.join(args.input_dir, 'charmap_inv.pickle'), 'rb') as f:
    inv_charmap = pickle.load(f, encoding='latin1')
with open(os.path.join(args.input_dir, 'charmap.pickle'), 'rb') as f:
    charmap = pickle.load(f, encoding='latin1')

torch.manual_seed(1)
use_cuda = torch.cuda.is_available()
if use_cuda:
    gpu = 0

netG = Generator()
if use_cuda:
    netG = netG.cuda(gpu)
# load weights
netG.load_state_dict(torch.load('GNPassGAN/output/checkpoints/netG_epoch_200000.pth'))


def RunGNPassGAN(max_lenght,max_num,socketio,list_prefix):
    if max_num < 100:
        max_num = 100
    if(max_lenght >= 10):
        max_lenght = 10
    samples = []
    batch = []
    list_pass = []
    for i in range(int(max_num / args.batch_size)):
        progress = (i+1) / int(max_num / args.batch_size)
        socketio.emit('progress_update', {'progress': progress * 100})  # Gửi dữ liệu đến client
        samples.extend(generate_samples(netG))

        for s in samples:
            s = "".join(s).replace('`','')
            if len(list_prefix) > 0:
                password = random.choice(list_prefix) + s
            else:
                password = s
            list_pass.append(password)
 
        samples = []
        # Gửi những mật khẩu còn lại sau vòng lặp
    time.sleep(2)
    for idx,i in enumerate(list_pass):
        if(idx < 1000):
            print(i)
            time.sleep(0.003)
        else:
            break
    return list_pass
    #RunGNPassGAN(max_lenght,max_num,socketio,list_prefix)
# max_lenght = 10
# max_num = 100
# list_prefix = ["abc","minh"]
# RunGNPassGAN(max_lenght,max_num,list_prefix)