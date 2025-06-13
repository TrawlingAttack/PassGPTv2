import os
import itertools
from collections import defaultdict
import random
import time
def read_guess_lists(list_file_pass):
    guess_lists = []
    for list_pass in list_file_pass:    
        guess_lists.append(list_pass)
    return guess_lists

def load_validation_set(file_path, sample_size=500000):
    with open(file_path, 'r', encoding='latin1', errors='ignore') as f:
        lines = [line.strip() for line in f if line.strip()]
    return set(random.sample(lines, min(sample_size, len(lines))))
    

def generate_multiview_subsets(guess_lists):
    l = len(guess_lists)
    subsets = defaultdict(list)
    seen = {}

    for rank in range(max(len(g) for g in guess_lists)):
        for i, g_list in enumerate(guess_lists):
            if rank < len(g_list):
                pwd = g_list[rank]
                bitmask = seen.get(pwd, 0)
                bitmask |= (1 << i)
                seen[pwd] = bitmask

    for pwd, bitmask in seen.items():
        key = format(bitmask, f'0{l}b')
        subsets[key].append(pwd)

    return subsets

def generate_power_intervals(k):
    intervals = []
    tolerance, temp, base = 1, 0, 10
    while temp < k:
        if temp < base:
            intervals.append((temp, temp + tolerance))
            temp += tolerance
        else:
            tolerance = base
            intervals.append((temp, temp + tolerance))
            temp += tolerance
            base *= 10
    return intervals

def evaluate_segments(subsets, validation_set, k):
    all_segments = []

    for label, pwd_list in subsets.items():
        intervals = generate_power_intervals(len(pwd_list))
        for start, end in intervals:
            segment = pwd_list[start:end]
            if not segment:
                continue
            hit = sum(1 for pwd in segment if pwd in validation_set)
            rate = hit / len(segment)
            all_segments.append((rate, segment))

    all_segments.sort(key=lambda x: -x[0])  # Sort by descending crack rate

    final_list = []
    for _, seg in all_segments:
        for pwd in seg:
            if len(final_list) >= k:
                break
            if pwd not in final_list:
                final_list.append(pwd)
        if len(final_list) >= k:
            break

    return final_list

def save_output(passwords, out_path='optimized_guess_list.txt'):
    with open(out_path, 'w', encoding='utf-8') as f:
        for pwd in passwords:
            f.write(pwd + '\n')

def guessfuse(input_files):
    validation_file = './Dataset/rockyou.txt'
    target_size = 10000
 

    time.sleep(1)
    print(f"==> [guessfuse] input_files: {type(input_files)} ({len(input_files)})")
    if not os.path.exists(validation_file):
        raise FileNotFoundError(f"[!] Không tìm thấy file: {validation_file}")
    time.sleep(1)
    try:
        guess_lists = read_guess_lists(input_files)
        print(f"   [+] Loaded guess_lists: {len(guess_lists)}")
        
        validation_set = load_validation_set(validation_file)
        print(f"   [+] Loaded validation set: {len(validation_set)}")

        subsets = generate_multiview_subsets(guess_lists)
        print(f"   [+] Generated subsets: {len(subsets)}")

        optimized_list = evaluate_segments(subsets, validation_set, target_size)
        print(f"   [+] Final optimized list: {len(optimized_list)} passwords.")
    except Exception as e:
        print(f"[!] Lỗi trong guessfuse: {str(e)}")
        raise

    return optimized_list
