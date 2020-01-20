import textract
import re
import string
import os
from lxml import etree

############################
### Retrieval operations ###
############################

def get_file_name(path):
    """ 
    Description:
        Takes a full path and returns filename and file extension
    Parameters:
        path (str): Full path to file
    Returns:
        filename (str): Filename without extension
        fileextension (str): File extension
    """
    basename = os.path.basename(path)
    filename, fileextension = os.path.splitext(basename)
    return filename, fileextension

#################################
### Text extraction functions ###
#################################

def xml_to_text(path, encoding="ISO-8859-1"):
    """ 
    Description:
        Extracts text from xml-files removing tags
    Parameters:
        path (str): Full path to file
        encoding (str): Encoding of file
    Returns:
        text (str): Extracted text
    """
    tree = etree.parse(path)
    text = etree.tostring(tree, encoding=encoding, method='text')
    text = text.decode(encoding)
    return text

def txt_to_text(path, encoding="ISO-8859-1"):
    """ 
    Description:
        Extracts text from txt-files
    Parameters:
        path (str): Full path to file
        encoding (str): Encoding of file
    Returns:
        text (str): Extracted text
    """
    with open(path, "rb") as file_io:
        text = file_io.read().decode(encoding)
    return text

def file_to_jpgs(path):
    """ 
    Description:
        Converts a file to one or more jpg-files. This is a wrapper of ImageMagick.
    Parameters:
        path (str): Full path to file
    Returns:
        output_filepaths (str): Path to output_file(s)
    """
    # Creating unique output directory
    file_directory = os.path.dirname(path)
    output_directory = file_directory + "/" + str(uuid.uuid4())
    make_directory(output_directory)

    # Cleans filename and moves to temp folder
    clean_name = clean_file_name(path)
    temp_path = output_directory + "/" + clean_name
    shutil.copy(path, temp_path)

    # Creates new output filenames
    file_directory = os.path.dirname(temp_path)
    filename, fileextension = os.path.splitext(os.path.basename(temp_path))
    output_filenames = file_directory + "/" + filename + "-page%03d.jpg"
    
    # Converting to one or more jpg-files
    code = "magick -density 300 " + temp_path + " -quality 300 " + output_filenames
    os.system(code)
    
    # Outputting output filenames
    output_filepaths = list_files(output_directory, "jpg")
    
    return output_filepaths, output_directory

def file_to_text(path, encoding="utf-8"):
    """ 
    Description:
        A file and extracts the text with stated encoding.
        The code works for the following extensions:
            .csv, .doc, .docx, .eml, .epub, .gif, 
            .htm, .html, .jpeg, .jpg, .json, .log, 
            .mp3, .msg, .odt, .ogg, .pdf, .png, .pptx, 
            .ps, .psv, .rtf, .tff, .tif, .tiff, .tsv, 
            .txt, .wav, .xls, .xlsx
    Parameters:
        path (str): Full path to file
        encoding (str): Encoding of file
    Returns:
        text (str): Extracted text
    """
    text = textract.process(path, language="dan", encoding=encoding)
    text = text.decode(encoding)
    return text

def attachment_to_text(path):
    """ 
    Description:
        Extracts text from most file types
    Parameters:
        path (str): Full path to file
    Returns:
        text (str): Extracted text
    """
    filename, fileextension = get_file_name(path)
    extracted_text = ""
    try:
        if fileextension.lower()==".txt":
            return txt_to_text(path)
        elif fileextension.lower()==".xml":
            return xml_to_text(path)
        else:
            return file_to_text(path)
    except:
        print("INFO: File is non-standard and ImageMagick will be used")
        pass
    try:
        if fileextension.lower() in [".pdf", ".png", ".bmp", ".jpeg", ".gif", ".tif", ".tiff"]:
            jpg_paths, jpg_directory = file_to_jpgs(path)
            list_of_texts = [file_to_text(jpg_path) for jpg_path in jpg_paths]
            text = ' '.join(list_of_texts)
            shutil.rmtree(jpg_directory, ignore_errors=True)
            return text
        else:
            print("INFO: No text could be extracted from: " + path)
            return ""
    except:
        print("WARN: Something went wrong and no text was extracted from: " + path)
        return ""

###################################################################
### Wrapper functions to extract all texts from all attachments ###
###################################################################

def unpack_attachments(unpack_dic):
    """ 
    Description:
        The function takes a dictionary in the format output by unpack_eml(),
        and if the dictionary has attachments it extracts the texts, else it
        just returns the dictionary as is.
    Parameters:
        unpack_dic (dic): Dictionary output by unpack_eml()
    Returns:
        output_dic (dic): Dictionary with texts in attachments
    """
    if "files" in unpack_dic:
        file_paths = [value[0] for key, value in unpack_dic['files'].items()]
        file_texts = [attachment_to_text(path) for path in file_paths]
        files_texts = dict(zip(file_paths, file_texts))
        unpack_dic['files_texts'] = files_texts
        return unpack_dic
    else:
        return unpack_dic

def collect_texts(unpack_dic, keys, as_list=False):
    """ 
    Description:
        The function takes a dictionary in the format output by unpack_attachments(),
        and concatenates the texts from the keys specified.
    Parameters:
        unpack_dic (dic): Dictionary output by unpack_attachments()
        keys (list): List of keys to collect texts from 
        as_list (bool): Whether you want the data returned as a list of strings or just one big string
    Returns:
        texts (str): All text as either one large string or as a list of strings
    """
    texts = []
    for key in keys:
        if key in unpack_dic:
            if key in ["subject", "from", "to", "date", "text", "html_text", "html"]:
                texts.append(unpack_dic[key])
            elif key=="parts":
                texts.append(str(unpack_dic[key]))
            elif key=="files":
                filenames = ' '.join([filename for filename in unpack_dic['files'].keys()])
                texts.append(filenames)
            elif key=="files_texts":
                file_texts = ' '.join([value for key, value in unpack_dic['files_texts'].items()])
                texts.append(file_texts)
    if as_list:
        return texts
    else:
        return ' '.join(texts)

###############################
### Text cleaning functions ###
###############################

def string_split_by_k(string, split_char, k):
    """ 
    Description:
        Takes a string and splits into k bites based on a separator
    Parameters:
        string (str): String to be split
        split_char (str): Character to split by
        k (int): Splits string into k parts
    Returns:
        split_string (list): String split into k parts
    """
    split_positions = [x.start() for x in re.finditer(split_char, string)]
    split_string = list()
    for i in range(k):
        if i == 0:
            split_string.append(string[0:split_positions[i]])
        elif i == k-1:
            split_string.append(string[split_positions[i-1]+1:])
        else:
            split_string.append(string[split_positions[i-1]+1:split_positions[i]])
    return split_string

def remove_characters(text, characters=['\\','`','*','_','{','}','[',']','(',')', '<','>','#','+','!','$','\'', '?', '@']):
    """ 
    Description:
        Removes a list of characters from a string
    Parameters:
        text (str): Input text
        characters (list): List of special characters to remove from text
    Returns:
        text (str): Text with special characters removed
    """
    for char in characters:
        if char in text:
            text = text.replace(char," ")
    return text

def remove_extra_whitespaces(text):
    """ 
    Description:
        Takes a text and removes a excess white spaces such as newlines, line endings and trailing whitespaces.
    Parameters:
        text (str): Text
    Returns:
        text (str): Text with white spaces removes
    """
    text = re.sub('\s+',' ',text)
    return text

def replace_dates(text, replacement=' DATE '):
    """ 
    Description:
        Takes some text and replaces dates in various formats with a word of choice
    Parameters:
        text (str): Text
        replacement (str): Replacement string, remember to put spaces before/after yourself
    Returns:
        text (str): Text with dates replaced
    """
    text = re.sub('\s(\d{1,2}.\s\w*\s\d{2,4})', replacement, text)
    text = re.sub('\s(\d{1,2}\s\w*\s\d{2,4})', replacement, text)
    text = re.sub('\s(\d{1,2}\/\d{1,2}\s)', replacement, text)
    text = re.sub('\s(\d{1,4}\.\d{1,2}\.\d{1,4})', replacement, text)
    text = re.sub('\s(\d{1,4}\-\d{1,2}\-\d{1,4})', replacement, text)
    text = re.sub('\s(\d{1,4}\/\d{1,2}\/\d{1,4})', replacement, text)
    
    return text

def replace_times(text, replacement=' TIME '):
    """ 
    Description:
        Takes some text and replaces times in various formats
    Parameters:
        text (str): Text
        replacement (str): Replacement string, remember to put spaces before/after yourself
    Returns:
        text (str): Text with times replaced
    """
    text = re.sub('\s(\d*\:\d*\:\d*)', replacement, text)
    text = re.sub('\s(\d*\:\d*)', replacement, text)
    text = re.sub('\s(\d*\:\d*\:\d*\.\d*)', replacement, text)
    
    return text

def replace_amounts(text, replacement=' AMOUNT '):
    """ 
    Description:
        Takes some text and replaces amounts in various formats
    Parameters:
        text (str): Text
        replacement (str): Replacement string, remember to put spaces before/after yourself
    Returns:
        text (str): Text with amounts replaced
    """
    # Replacing positive amounts
    text = re.sub(r'\s(?<![.,])\d+[,.]\d*[,.]\d*', replacement, text)
    text = re.sub('\s([0-9]+[,.]+[0-9]+[,.]+[0-9])', replacement, text)
    text = re.sub('\s([0-9]+[,.]+[0-9]+)', replacement, text)
    
    # Replacing negative amounts
    text = re.sub(r'\s-(?<![.,])\d+[,.]\d*[,.]\d*', replacement, text)
    text = re.sub('\s-([0-9]+[,.]+[0-9]+[,.]+[0-9])', replacement, text)
    text = re.sub('\s-([0-9]+[,.]+[0-9]+)', replacement, text)
    
    return text

def replace_numbers(text, replacement=' NUMBER '):
    """ 
    Description:
        Takes some text and replaces numbers
    Parameters:
        text (str): Text
        replacement (str): Replacement string, remember to put spaces before/after yourself
    Returns:
        text (str): Text with numbers replaced
    """
    text = re.sub(r'\b\d+(?:\.\d+)?(\s+|$|,|.)', replacement, text)
    
    return text

def replace_cpr(text, replacement=' CPR '):
    """ 
    Description:
        Takes some text and replaces cpr
    Parameters:
        text (str): Text
        replacement (str): Replacement string, remember to put spaces before/after yourself
    Returns:
        text (str): Text with cpr replaced
    """
    text = re.sub('\s(\d{6}\-\d{4})\s', replacement, text)
    text = re.sub('\s(\d{10})\s', replacement, text)
    
    return text

def collect_and_clean_text(unpack_dic, keys, remove_extra_whitespaces_bool=True, remove_characters_bool=True, replace_dates_bool=True, replace_times_bool=True, replace_amounts_bool=True, replace_cpr_bool=True, replace_numbers_bool=True):
    """ 
    Description:
        This is a wrapper function that first collects the stated texts, and then cleans it in several ways
    Parameters:
        unpack_dic (dic): Dictionary output by unpack_attachments()
        keys (list): List of keys to collect texts from 
        remove_characters (bool): Removes special characters
        remove_extra_whitespaces (bool): Removes extra white spaces
        replace_dates (bool): Replaces dates with "DATE"
        replace_times (bool): Replaces times with "TIME"
        replace_amounts (bool): Replaces amounts with "AMOUNT"
        replace_numbers (bool): Replaces numbers with "NUMBER"
    Returns:
        filename (str): Name of input file
        text (str): Collected and clean text
    """
    filename = unpack_dic['input_file']
    text = collect_texts(unpack_dic, keys)
    
    if remove_extra_whitespaces_bool:
        text = remove_extra_whitespaces(text)
    if replace_dates_bool:
        text = replace_dates(text)
    if replace_times_bool:
        text = replace_times(text)
    if replace_amounts_bool:
        text = replace_amounts(text)
    if replace_cpr_bool:
        text = replace_cpr(text)
    if remove_characters_bool:
        text = remove_characters(text)
    if replace_numbers_bool:
        text = replace_numbers(text)
    if remove_extra_whitespaces_bool:
        text = remove_extra_whitespaces(text)
    
    return filename, text