#!/usr/bin/env python3


"""

Contains all the file reading logic for the python pcfg trainer

"""


import codecs
import os

def get_confirmation(warningtext):
    """
    Prints a warning message and asks for user confirmation

    Inputs:
        warningtext: (String) The warning to display to the user

    Returns:
        True: User selected Yes
        
        False: User selected No

    """
    print()
    print(warningtext)
    while True:
        try:
            user_input = input("Please confirm (Y/N): ")
        except:
            user_input = ''
        if user_input.lower() == 'y' or user_input.lower() == 'yes':
            return True
        elif user_input.lower() == 'n' or user_input.lower() == 'no':
            return False

        print("The option: " + str(user_input) + " : is not a valid input")
        print("Valid options: [Y]es or [N]o")


def detect_file_encoding(training_file, file_encoding, max_passwords = 500000):
    """
    Used for autodetecting file encoding of the training password set

    Autodectection requires the python package chardet to be installed

    pip install chardet

    You can also get it from https://github.com/chardet/chardet

    I'm keeping the declarations for the chardet package local to this file
    so people can run this tool without installing it if they don't want to
    use this feature

    Inputs:
        training_file: (String) The path+name of the file to open

        file_encoding: (List) A list to return the possible/recommended file
        encodings of the training file

        max_passwords: (Int) The maximum number of passwords to parse to
        identify the encoding of the file. This is an optimization so this
        function doesn't have to parse the whole file.
        
    Returns:
        True: The function executed sucesfully
        
        False: An error occured, or the user did not have the chardet library
        and decided to not accept the default 'ascii' setting

    """

    # Try to import chardet
    #
    # If that package is not installed print out a warning and use is ok,
    # then use ascii as the default values
    #
    try:
        from chardet.universaldetector import UniversalDetector
        detector = UniversalDetector()
    except ImportError as error:
        print("FAILED: chardet not insalled")
        print("It is highly recommended that you install the 'chardet' Python package")
        print("or manually specify the file encoding of the training set via the command line")
        print("You can download chardet from https://pypi.python.org/pypi/chardet")
        if get_confirmation("Do you want to continue using the default encoding 'ascii'?"):
            file_encoding.append('ascii')
            return True

        # User wanted to exit instead
        print("Understood. Please install chardet or specify an encoding " +
            "format on the command line"
            )
        return False

    try:
        cur_count = 0
        with open(training_file, 'rb') as file:
            for line in file.readlines():
            
                # Check for a $HEX[] encoded password 
                end_bracket_pos = line.find(bytes("]", "ascii"))
                if line.startswith(bytes("$HEX[","ascii")) and end_bracket_pos:
                    try:
                        line = bytes.fromhex(line[5:end_bracket_pos].decode("ascii"))
                    except:
                        continue

                # Now try to detect encoding of line
                detector.feed(line)
                if detector.done:
                    break
                cur_count = cur_count + 1
                if cur_count >= max_passwords:
                    break
            detector.close()

    except IOError as error:
        print ("Error opening file " + training_file)
        print ("Error is " + str(error))
        return False

    try:
        file_encoding.append(detector.result['encoding'])
        print("File Encoding Detected: " + str(detector.result['encoding']))
        print("Confidence for file encoding: " + str(detector.result['confidence']))
        print("If you think another file encoding might have been used please ")
        print("manually specify the file encoding and run the training program again")
        print()

        # Manually overriding ASCII to UTF-8 to deal with $HEX[] encoded files
        if file_encoding[0] == "ascii":
            print("Overriding ASCII and converting it to UTF-8 to deal with $HEX[] encoded training files")
            print("If you really want to have an ASCII encoded file you can specify it on the command line")
            print("But there shouldn't be any downside with using UTF-8")
            file_encoding[0] = "utf-8"

    except KeyError as error:
        print("Error encountered with file encoding autodetection")
        print("Error : " + str(error))
        return False

    return True


def check_valid(input_password):
    """
    Checks to see if the input password is valid for this training program

    Invalid in this case means you don't want to train on them

    Additionaly grammar checks may be run later to futher exclude passwords#
    This just features that will likely be universal rejections

    Inputs:
        input_password: (String) The input password to parse

    Returns:
        TRUE: If the password is valid
        
        FALSE: If the password is invalid

    """

    # Don't accept blank passwords for training.
    if len(input_password) == 0:
        return False

    # Remove tabs from the training data
    # This is important since when the grammar is saved to disk tabs are used
    # as seperators. There certainly are other approaches but putting this
    # placeholder here for now since tabs are unlikely to be used in passwords
    if "\t" in input_password:
        return False

    # Below are other values that cause problems that we are going to remove.
    # These values include things like LineFeed LF

    #Invalid characters at the begining of the ASCII table
    for invalid_hex in range (0x0,0x20):
        if chr(invalid_hex) in input_password:
            return False

    # UTF-8 Line Seperator
    if u"\u2028" in input_password:
        return False

    # UTF-8 NEL Line seperator 'C285' eg unicode character '0085'
    # I coupld probably replace with a newline, but given how this tends to
    # show up in XML data it can highlight a weirder issue going on with inputs.
    # So dropping it vs. trying to fix it up for now.
    if u"\u0085" in input_password:
        return False

    return True


class TrainerFileInput:
    """
    Reads input passwords from file, one by one

    Making this a class so it can return one password at a time from the
    training file

    """

    def __init__(self, filename,socketio, encoding = 'utf-8', prefixcount = False):
        """
        Open the file for reading

        Passes file exceptions back up if they occur
        Eg: if the file doesn't exist
        
        Inputs:
            filename: (String) The filename of the training file to open
            
            encoding: (String) The file encoding to use when parsing the file
            
        Returns:
            TrainingFileInput: (Object)

        """

        # Using surrogateescape to handle errors so we can detect encoding
        # issues without raising an exception during the reading
        # of the original password
        #
        self.encoding = encoding
        self.filename = filename
        self.files_content = []  # Dùng để lưu nội dung của tất cả file
        self.socketio = socketio

        for file_path in filename:
            if file_path:
                for password in file_path:
                    self.files_content.append(password)


        # Keep track of the number of encoding errors
        self.num_encoding_errors = 0

        # Keep track of the number of valid passwords that have been parsed
        self.num_passwords = 0

        # Duplicate password detection
        #
        # Duplicates are good. If this doesn't see duplicate passwords warn the
        # user.
        self.duplicates_found = False

        # Mini dictionary of the first X passwords to look for duplicates
        self.duplicate_detection = {}

        # Number of passwords to read in to check for duplicates
        self.num_to_look_for_duplicates = 100000

        self.prefixcount = prefixcount

    def read_password(self):
        """
        Yields one password from the training set. If there are no more passwords, yields nothing.
    
        Returns:
            clean_password: (String) The next password
        """
        #self.socketio.emit('progress_status', {'status': 'start'})  # 👈 Bắt đầu loading
        try:
            i = 0
            for content in self.files_content:  # lặp từng nội dung file
                for password in content.splitlines():  # lặp từng dòng trong nội dung file
                    progress = (i + 1) / len(self.files_content)
                    self.socketio.emit('progress_update', {
                        'progress': progress * 100,
                        'current': i + 1,
                        'total': len(self.files_content)
})
                    # Unicode errors will throw an exception here, so catch it and skip the password
                    try:
                        password = str(password)
                    except UnicodeError:
                        self.num_encoding_errors += 1
                        continue

                    clean_password = password.rstrip('\r\n')

                    if self.prefixcount:
                        try:
                            n = int(clean_password.lstrip().split(' ')[0])
                            clean_password = ' '.join(clean_password.lstrip().split(' ')[1:])
                        except ValueError:
                            continue
                    else:
                        n = 1

                    if clean_password.startswith("$HEX[") and clean_password.endswith("]"):
                        try:
                            clean_password = bytes.fromhex(clean_password[5:-1]).decode(self.encoding)
                        except:
                            self.num_encoding_errors += n
                            continue

                    try:
                        clean_password.encode(self.encoding)
                    except UnicodeEncodeError as msg:
                        if msg.reason == 'surrogates not allowed':
                            self.num_encoding_errors += n
                        else:
                            self.num_encoding_errors += n
                        continue

                    if not check_valid(clean_password):
                        continue

                    self.num_passwords += n

                    if self.prefixcount and n > 1:
                        self.duplicates_found = True

                    if not self.duplicates_found:
                        if self.num_passwords < self.num_to_look_for_duplicates:
                            if clean_password in self.duplicate_detection:
                                self.duplicates_found = True
                                self.duplicate_detection.clear()
                            self.duplicate_detection[clean_password] = n

                    for _ in range(n):
                        yield clean_password
                    i += 1

        except IOError as error:
            print(error)
            print("Error reading files.")
            raise

