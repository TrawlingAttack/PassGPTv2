import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from transformers import (
    GPT2LMHeadModel
)
from transformers import RobertaTokenizerFast
import time
import threading
import torch
from PassGPTv2.tokenizer import CharTokenizer
import argparse
import random
from PassGPTv2.concat_pattern_password import get_pattern
from collections import defaultdict



from PassGPT.PassGPT import Generate_Password



MAX_LEN = 32    # It should be equal to input size of model.

class ThreadBase(threading.Thread):
    """ overload threading, so that it can return values """
    def __init__(self, target=None, args=()):
        super().__init__()
        self.func = target
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)
 
    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print(e)
            return None

def gen_sample(test_model_path, tokenizer, GEN_BATCH_SIZE, GPU_ID,seed,list_prefix):
    model = GPT2LMHeadModel.from_pretrained(test_model_path)

    tokenizer2 = RobertaTokenizerFast.from_pretrained("PassGPT/configs/byte_bpe_tokenizer_99", 
                                                  max_len=18,
                                                  padding="max_length", 
                                                  truncation=True,
                                                  do_lower_case=False,
                                                  strip_accents=False,
                                                  mask_token="<mask>",
                                                  unk_token="<unk>",
                                                  pad_token="<pad>",
                                                  truncation_side="right")
    model_passgpt = GPT2LMHeadModel.from_pretrained("PassGPT/model_passgpt/model_passgpt").eval().to('cpu')
    inputs = ""
    if len(list_prefix) > 0:
        selected = random.choice(list_prefix)
        prefix = selected["prefix"]
        struction = selected["struction"]
        if struction == "" and prefix != "":
            outputs = Generate_Password(seed,prefix,tokenizer2,model_passgpt,10,1,1,100,None,1)
            new_pattern = get_pattern(outputs[0])
            for i in range(0, len(new_pattern), 2):
                inputs += " ".join(new_pattern[i:i+2]) + " "
            inputs += "<SEP> "
            for i in prefix:
                inputs += i +" "
        elif struction != "" and prefix == "":
            inputs += struction + " <SEP> "
        else:
            inputs += struction + " "
            inputs += "<SEP> "
            for i in prefix:
                inputs += i +" "
    else:
        inputs = ""
    device = "cuda:"+str(GPU_ID)
    model.to(device)

    tokenizer_forgen_result = tokenizer.encode_forgen(inputs)

    passwords = set()
    
    outputs = model.generate(
        input_ids= tokenizer_forgen_result.view([1,-1]).to(device),
        pad_token_id=tokenizer.pad_token_id,
        max_length=MAX_LEN, 
        do_sample=True, 
        num_return_sequences=GEN_BATCH_SIZE,
        )
    outputs = tokenizer.batch_decode(outputs)
    for output in outputs:
        passwords.add(output)

    return [*passwords,]


def gen_parallel(vocab_file, batch_size, test_model_path, N, num_gpus, gpu_index,socketio,list_prefix):
    print(f'Load tokenizer.')
    tokenizer = CharTokenizer(vocab_file=vocab_file, 
                              bos_token="<BOS>",
                              eos_token="<EOS>",
                              sep_token="<SEP>",
                              unk_token="<UNK>",
                              pad_token="<PAD>"
                              )
    tokenizer.padding_side = "left"

    # mulit gpu parallel
    if not torch.cuda.is_available():
        print('ERROR! GPU not found!')
    else:
        total_start = time.time()
        threads = {}
        total_passwords = []

        total_round = N//batch_size
        print('*'*30)
        print(f'Generation begin.')
        print('Total generation needs {} batchs.'.format(total_round))

        i = 0
        while(i < total_round or len(threads) > 0 ):
            if len(threads) == 0:
                for gpu_id in range(num_gpus):
                    if i < total_round:
                        t=ThreadBase(target=gen_sample, args=(test_model_path, tokenizer, batch_size, gpu_id+gpu_index,i,list_prefix))
                        t.start()
                        threads[t] = i
                        i += 1
            
            # check whether some threads have finished.
            temp_threads = threads.copy()
            for t in temp_threads:
                t.join()
                if not t.is_alive():
                    new_passwords = t.get_result()
                    total_passwords += new_passwords
                    #print('[{}/{}] generated {}.'.format(temp_threads[t]+1, total_round, new_num))
                    threads.pop(t)

                    progress = (len(set(total_passwords)) + 1) / total_round
                    socketio.emit('progress_update', {'progress': int(progress * 100)})
        total_passwords = set(total_passwords)

        total_end = time.time()
        total_time = total_end-total_start
        
        print('Generation done.')
        print('*'*30)
        print('Use time:{}'.format(total_time))
    return total_passwords
        

def RunPassGPT2(max_lenght,max_num,socketio,list_prefix):
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="directory of pagpassgpt" , default='./PassGPTv2/model_passgptv2/model_passgptv2/last-step', type=str)
    parser.add_argument("--vocabfile_path", help="path of vocab file", type=str, default='./PassGPTv2/tokenizer/vocab.json')
    parser.add_argument("--output_path", help="path of output file path" , default='./', type=str)
    parser.add_argument("--generate_num", help="total guessing number", default=10, type=int)
    parser.add_argument("--batch_size", help="generate batch size", default=1, type=int)
    parser.add_argument("--gpu_num", help="gpu num", default=1, type=int)
    parser.add_argument("--gpu_index", help="Starting GPU index", default=0, type=int)
    args = parser.parse_args()

    model_path = args.model_path
    vocab_file = args.vocabfile_path

    n = max_num
    batch_size = args.batch_size
    num_gpus = args.gpu_num
    gpu_index = args.gpu_index

    
    list_result = gen_parallel(vocab_file, batch_size, model_path, n, num_gpus, gpu_index,socketio,list_prefix)
    list_pass = []
    for idx,i in enumerate(list_result):
        if(idx < 1000):
            print(i)
            list_pass.append(i.split(' ', 1)[1])
            time.sleep(0.003)
        else:
            break
    return list_pass
