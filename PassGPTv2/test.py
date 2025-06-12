def merge_patterns(prefix_pattern, pass_pattern):
    # Convert strings to lists if they're strings
    if isinstance(prefix_pattern, str):
        pattern1 = list(prefix_pattern)
    else:
        pattern1 = list(prefix_pattern)
    
    if isinstance(pass_pattern, str):
        pattern2 = list(pass_pattern)  # Chuyển chuỗi thành danh sách ký tự
        i = 1  # Bắt đầu từ chỉ mục lẻ (i = 1, 3, 5, ...)

        while i < len(pattern2):
            if not pattern2[i].isdigit() or (pattern2[i - 1] not in {'L', 'N', 'S'}):
                del pattern2[i - 1:i]  # Xóa cả pattern2[i-1] và pattern2[i]
            else:
                i += 2  # Chuyển sang chỉ mục lẻ tiếp theo
        if len(pattern2) % 2 != 0:
            pattern2.pop()
    new_pattern = []
    
    # Check if second-to-last element of pattern1 matches first element of pattern2
    if len(pattern1) >= 2:
        if pattern1[-2] == pattern2[0]:
            try:
                # Convert strings to integers and perform arithmetic addition
                num1 = int(pattern1[-1])  # Last element of pattern1
                num2 = int(pattern2[1])   # Second element of pattern2
                pattern1[-1] = str(num1 + num2)  # Add numbers and convert back to string
                new_pattern = pattern1.copy()
                # Add remaining elements of pattern2 (starting from index 2)
                for i in range(2, len(pattern2)):
                    new_pattern.append(pattern2[i])
            except ValueError:
                # If conversion to int fails, fall back to string concatenation
                pattern1[-1] = pattern1[-1] + pattern2[1]
                new_pattern = pattern1.copy()
                for i in range(2, len(pattern2)):
                    new_pattern.append(pattern2[i])
        else:
        # If no match, simply concatenate the lists
            new_pattern = pattern1 + pattern2

    # Join all elements into a single string
    pattern = "".join(str(x) for x in new_pattern)
    return pattern

# Test cases
print(merge_patterns("L4N3", "N3KFL7F"))  # "N3" matches, 3 + 7 = 10, output: "L4N10"
print(merge_patterns("L4N3", "L7NRN1%"))  # No match, output: "L4N3L7N1"