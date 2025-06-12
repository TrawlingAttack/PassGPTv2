import time
import argparse
import torch
from transformers import GPT2LMHeadModel
from datasets import load_dataset
from transformers import RobertaTokenizerFast
import numpy as np
import random
import string

def pattern_to_string(pattern):
    # Bảng ánh xạ ký hiệu sang ký tự đại diện
    symbol_map = {
        'L': 'l',  # lowercase
        'U': 'u',  # uppercase
        'N': 'n',  # number
        'S': 's',  # special character
    }

    result = ""
    parts = pattern.split()

    for part in parts:
        symbol = part[0]
        count = int(part[1:])
        if symbol in symbol_map:
            result += symbol_map[symbol] * count
        else:
            raise ValueError(f"Unknown symbol: {symbol}")

    return result
 
def Generate_Password(seed_offset,prefix,tokenizer,model,maxchars,batch_size,num_beams,top_p,top_k,temperature):
    torch.manual_seed(seed_offset)
    all_tokens = [[i] for i in range(len(tokenizer))]
    with torch.no_grad():
        input_ids = None
        if(prefix == ""):
            input_ids = torch.tensor([[tokenizer.bos_token_id]])
        elif(prefix["prefix"] != "" and prefix["struction"] == ""):
            input_ids = tokenizer.encode(prefix["prefix"], return_tensors="pt", add_special_tokens=False)
        else:
            if prefix["prefix"] == "":
                prefix_prefix = "<s>"
                struction = pattern_to_string(prefix["struction"])
                last_num_struction = len(struction)-0
                len_prefix = 1
            else:
                len_prefix = len(prefix["prefix"])
                prefix_prefix = prefix["prefix"]
                struction = pattern_to_string(prefix["struction"])
                last_num_struction = len(struction)-len_prefix
            
            last_struction = struction[-last_num_struction:] 
            input_ids = tokenizer.encode(prefix_prefix, return_tensors="pt", add_special_tokens=False)
            generation = input_ids
            for char in last_struction:
                if char == "u":
                    bad_tokens = [i for i in all_tokens if i not in tokenizer(list(string.ascii_uppercase), add_special_tokens=False).input_ids]
                elif char == "l":
                    bad_tokens = [i for i in all_tokens if i not in tokenizer(list(string.ascii_lowercase), add_special_tokens=False).input_ids]
                elif char == "n":
                    bad_tokens = [i for i in all_tokens if i not in tokenizer(list(string.digits), add_special_tokens=False).input_ids]
                elif char == "s":
                    bad_tokens = [i for i in all_tokens if i not in tokenizer(list(string.punctuation), add_special_tokens=False).input_ids]
                generation = model.generate(generation, do_sample=True, max_length=len_prefix+1, pad_token_id=tokenizer.pad_token_id, num_return_sequences=1,  bad_words_ids=bad_tokens)
                len_prefix += 1
            
            decoded = tokenizer.batch_decode(generation.tolist())
            decoded_clean = [y.replace("<s>", "").split("</s>")[0] for y in decoded] # Get content before end of password token
            del generation
            del decoded
            return decoded_clean
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token

            # Generate tokens sampling from the distribution of codebook indices
        g = model.generate(input_ids, do_sample=True, max_length=maxchars+2,bad_words_ids=[[tokenizer.bos_token_id]], 
                               pad_token_id=tokenizer.pad_token_id, num_return_sequences=batch_size, num_beams=num_beams, 
                               top_p=top_p/100, top_k=top_k, temperature=temperature)
            #bad_words_ids=[[tokenizer.bos_token_id]]

        decoded = tokenizer.batch_decode(g.tolist())
        decoded_clean = [y.replace("<s>", "").split("</s>")[0] for y in decoded] # Get content before end of password token
        del g
        del decoded
    return decoded_clean
def RunPassGPT(country,lenght_pass, number_pass,socketio,list_prefix):
    global list_new_password  # Thêm dòng này để dùng biến toàn cục
    list_new_password = []
    if country in ["vn", "china", "indo", "uk"]:
        token = 96
    elif country in ["malaysia", "us", "taiwan", "den"]:
        token = 99
    elif country in ["canada"]:
        token = 96
    else:
        token = 99
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="Path to PassGPT checkpoint or Huggingface name", type=str, required=False)
    parser.add_argument("--tokenizer_path", help="Path to pre-trained tokenizer or Huggingface name. If none, it will be set to model_path", type=str, default=f"PassGPT/configs/byte_bpe_tokenizer_{token}_{country}")
    parser.add_argument("--train_data_path", help="path to training data", type=str, required=False)
    parser.add_argument("--eval_data_path", help="path to evaluation data", type=str, required=False)
    parser.add_argument("--out_path", help="Path to store the generations", type=str, required=False)
    parser.add_argument("--filename", help="Filename where generations will be stored", type=str, default="passwords.txt")
    parser.add_argument("--maxchars", help="Maximum length of the passwords", type=int, default=lenght_pass)
    parser.add_argument("--seed_offset", help="Random seed offset for generation. Allows to parallelize generation across different executions.", type=int, default=0)
    parser.add_argument("--num_generate", help="Number of passwords to generate", type=int, default=int(number_pass))
    parser.add_argument("--batch_size", help="Batch size for generation", type=int, default=1)
    parser.add_argument("--device", help="Device to run execution", type=str, default='cpu')
    parser.add_argument("--num_beams", help="Number of beams for sampling", type=int, default=1)
    parser.add_argument("--top_p", help="Probability for nucleus sampling", type=int, default=100)
    parser.add_argument("--top_k", help="Sample only from k tokens with highes probability", type=int, default=None)
    parser.add_argument("--temperature", help="Sampling temperature", type=float, default= 1)

    args = parser.parse_args()
    
    # Init random seeds
    random.seed(args.seed_offset)
    np.random.seed(args.seed_offset)
    torch.manual_seed(args.seed_offset)
    
    # Assert sizes are divisible
    #assert args.num_generate%args.batch_size==0, "Number of passwords to generate should be divisible by batch size"
    
    # assert not os.path.isfile(os.path.join(args.out_path, args.filename)), "The provided output path already exists, please provide a unique path."
    # Path(args.out_path).mkdir(parents=True, exist_ok=True)
    args.model_path = f"PassGPT/model/model_passgpt_{country}/model_passgpt_{country}"
    # Load tokenizer
    if args.tokenizer_path is None:
        args.tokenizer_path = args.model_path
    
    tokenizer = RobertaTokenizerFast.from_pretrained(args.tokenizer_path, 
                                                  max_len=18,
                                                  padding="max_length", 
                                                  truncation=True,
                                                  do_lower_case=False,
                                                  strip_accents=False,
                                                  mask_token="<mask>",
                                                  unk_token="<unk>",
                                                  pad_token="<pad>",
                                                  truncation_side="right")
    
    # Load models
    model = GPT2LMHeadModel.from_pretrained(args.model_path).eval().to(args.device)
    # Passwords generation
    total_steps = int(args.num_generate)  # Tổng số bước
    y = 0
    i = 0
    while i < total_steps:
        # Set seed for reproducibility
        progress = (i+1) / total_steps
        socketio.emit('progress_update', {'progress': progress * 100})  # Gửi dữ liệu đến client
        if len(list_prefix) > 0:
            prefix = random.choice(list_prefix)
        else:
            prefix = ""
        decoded_clean = Generate_Password(args.seed_offset + y,prefix,tokenizer,model,args.maxchars,args.batch_size,args.num_beams,args.top_p,args.top_k,args.temperature)
        y += 1
        list_new_password.append(decoded_clean[0])
        i += 1

        del decoded_clean

    for idx,line in enumerate(list_new_password):
        if idx < 1000:
            print(f"{idx}: {line}")
            time.sleep(0.002)
        else:
            break
    return list_new_password

def list_passwords():
    global list_new_password
    return list_new_password
