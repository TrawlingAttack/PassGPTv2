from PCFG.prince_ling import RunPCFG
from Markov_Omen.enumNG import RunOmenMarkov
from GNPassGAN.sample import RunGNPassGAN
from PassGPT.PassGPT import RunPassGPT
from PassGPTv2.normal_gen import RunPassGPT2
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


class Generate_Model():
    def __init__(self,country,max_lenght,max_num,socket,option_model,list_prefix=[]):
        self.country = country
        self.max_lenght = int(max_lenght)
        self.max_num = int(max_num)
        self.option_model = option_model
        self.list_prefix = []
        if list_prefix:
            for i in list_prefix:
                self.list_prefix.append(i)
        self.socket = socket


    def main(self):
        list_password = []
        if(self.option_model == 0):
            list_password = RunPCFG(self.max_lenght,self.max_num,self.socket,self.list_prefix)
        elif(self.option_model == 1):
            list_password = RunOmenMarkov(self.max_lenght,self.max_num,self.socket,self.list_prefix)
        elif(self.option_model == 2):
            list_password = RunGNPassGAN(self.max_lenght,self.max_num,self.socket,self.list_prefix)
        elif(self.option_model == 3):
            list_password = RunPassGPT(self.country,self.max_lenght,self.max_num,self.socket,self.list_prefix)
        elif(self.option_model == 4):
            list_password = RunPassGPT2(self.country,self.max_lenght,self.max_num,self.socket,self.list_prefix)
        return list_password

