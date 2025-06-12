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

def gen_sample(country,test_model_path, tokenizer, GEN_BATCH_SIZE, device, seed, list_prefix):
    model = GPT2LMHeadModel.from_pretrained(test_model_path)
    if country in ["vn", "china", "indo", "uk"]:
        token = 96
    elif country in ["malaysia", "us", "taiwan", "den"]:
        token = 99
    elif country in ["canada"]:
        token = 96
    else:
        token = 99
    tokenizer2 = RobertaTokenizerFast.from_pretrained(
        f"PassGPT/configs/byte_bpe_tokenizer_{token}_{country}", 
        max_len=18,
        padding="max_length", 
        truncation=True,
        do_lower_case=False,
        strip_accents=False,
        mask_token="<mask>",
        unk_token="<unk>",
        pad_token="<pad>",
        truncation_side="right"
    )

    model_passgpt = GPT2LMHeadModel.from_pretrained(f"PassGPT/model/model_passgpt_{country}/model_passgpt_{country}").eval().to('cpu')

    inputs = ""
    if len(list_prefix) > 0:
        selected = random.choice(list_prefix)
        prefix = selected["prefix"]
        struction = selected["struction"]
        if struction == "" and prefix != "":
            outputs = Generate_Password(seed, selected, tokenizer2, model_passgpt, 10, 1, 1, 100, None, 1)
            new_pattern = get_pattern(outputs[0])
            for i in range(0, len(new_pattern), 2):
                inputs += " ".join(new_pattern[i:i+2]) + " "
            inputs += "<SEP> "
            for i in prefix:
                inputs += i + " "
        elif struction != "" and prefix == "":
            inputs += struction + " <SEP> "
        else:
            inputs += struction + " <SEP> "
            for i in prefix:
                inputs += i + " "
    else:
        inputs = ""

    device = device if device == 'cpu' else f'cuda:{device}'
    model.to(device)

    tokenizer_forgen_result = tokenizer.encode_forgen(inputs)

    passwords = set()

    outputs = model.generate(
        input_ids=tokenizer_forgen_result.view(1, -1).to(device),
        pad_token_id=tokenizer.pad_token_id,
        max_length=MAX_LEN,
        do_sample=True,
        num_return_sequences=GEN_BATCH_SIZE,
    )
    outputs = tokenizer.batch_decode(outputs)
    for output in outputs:
        passwords.add(output)

    return list(passwords)



def gen_parallel(country,vocab_file, batch_size, test_model_path, N, num_threads, socketio, list_prefix):
    print(f'Load tokenizer.')
    tokenizer = CharTokenizer(
        vocab_file=vocab_file, 
        bos_token="<BOS>",
        eos_token="<EOS>",
        sep_token="<SEP>",
        unk_token="<UNK>",
        pad_token="<PAD>"
    )
    tokenizer.padding_side = "left"

    total_start = time.time()
    threads = {}
    total_passwords = []

    total_round = N // batch_size
    print('*' * 30)
    print(f'Generation begin.')
    print(f'Total generation needs {total_round} batches.')

    i = 0
    while i < total_round or len(threads) > 0:
        if len(threads) == 0:
            for _ in range(num_threads):
                if i < total_round:
                    # Chạy trên CPU: chỉ truyền device='cpu' hoặc bỏ hẳn nếu mặc định là CPU
                    t = ThreadBase(
                        target=gen_sample,
                        args=(country,test_model_path, tokenizer, batch_size, 'cpu', i, list_prefix)
                    )
                    t.start()
                    threads[t] = i
                    i += 1

        # check whether some threads have finished
        temp_threads = threads.copy()
        for t in temp_threads:
            t.join()
            if not t.is_alive():
                new_passwords = t.get_result()
                total_passwords += new_passwords
                threads.pop(t)

                progress = (len(set(total_passwords)) + 1) / total_round
                socketio.emit('progress_update', {'progress': int(progress * 100)})

    total_passwords = set(total_passwords)

    total_end = time.time()
    total_time = total_end - total_start

    print('Generation done.')
    print('*' * 30)
    print('Use time: {}'.format(total_time))
    return total_passwords

        

def RunPassGPT2(country,max_lenght,max_num,socketio,list_prefix):
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="directory of pagpassgpt" , default=f'./PassGPTv2/model/model_passgptv2_{country}/model_passgptv2_{country}/last-step', type=str)
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

    
    list_result = gen_parallel(country,vocab_file, batch_size, model_path, n, num_gpus,socketio,list_prefix)
    list_pass = []
    socketio.emit('progress_update', {'progress': int(100)})
    for idx,i in enumerate(list_result):
        if(idx < 1000):
            print(i)
            list_pass.append(i.split(' ', 1)[1])
            time.sleep(0.003)
        else:
            break
    return list_pass
