import glob
import os
import uuid
import shutil
import re
import string
from bs4 import BeautifulSoup
from email import message_from_file, message_from_bytes
from email.header import Header, decode_header, make_header
from email.utils import parseaddr

#############################
### Basic file operations ###
#############################

def delete_folder_recursively(directory):
    """ 
    Description:
        This is a wrapper function only availible in a bash shell
    Parameters:
        directory (str): Directory delere recursively
    """
    os.system('rm -r ' + directory)

def list_files(directory, extension="*", recursive=False):
    """ 
    Description:
        Lists all files with a chosen extension
    Parameters:
        directory (str): Directory to search in
        extension (str): File extensions e.g. "txt"
        recursive (bool): Whether to include files in subfolders
    Returns:
        list (list): List of file paths
    """
    if recursive:
        return [filename for filename in glob.iglob(directory + '/**/*' + extension, recursive=True) if os.path.isfile(filename)]
    else:
        return [filename for filename in glob.iglob(directory + '/*' + extension, recursive=False) if os.path.isfile(filename)]

def file_exists(path, filename):
    """ 
    Description:
        Checks whether file exists
    Parameters:
        path (str): Output folder
        filename (str): File name
    """
    return os.path.exists(os.path.join(path, filename))

def open_file(path):
    """ 
    Description:
        Opens a file
    Parameters:
        path (str): Path to file
    """
    f = open(path)
    return f

def save_file(path, filename, content, access_mode="wb"):
    """ 
    Description:
        Saves content to a file
    Parameters:
        path (str): Output folder
        filename (str): File name
        content (?): Content to write to file
    """
    file = open(os.path.join(path, filename), access_mode)
    file.write(content)
    file.close()

def make_directory(directory):
    """ 
    Description:
        Creates directory if it does not already exist
    Parameters:
        directory (str): Directory to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_name(key, file_name):
    """
    Description:
        Creates a unique filename by combining key, unique value and file_name. Whitespaces are removed.
    Parameters:
        key (str): ID string for the message
        file_name (str): File name
    Returns:
        new_file_name (str): A concatenation of the two input strings with underscores instead of whitespaces
    """
    new_file_name = key + "." + str(uuid.uuid4()) + "." + file_name
    new_file_name = new_file_name.replace(" ", "_")
    return new_file_name

####################################
### Cleaning/Decoding operations ###
####################################

def clean_file_name(path):
    """ 
    Description:
        Takes a full file path and cleans the filename from special characters
    Parameters:
        path (str): Full path to file
    Returns:
        clean_file_name (str): Filename with only alphanumeric characters
    """
    filename, fileextension = os.path.splitext(os.path.basename(path))
    pattern = re.compile('[\W_]+')
    clean_file_name = pattern.sub('', filename) + fileextension
    return clean_file_name

def decode_header_string(string):
    """ 
    Description:
        Decodes the header information such that they include unicode characters
    Parameters:
        string (str): Header string
    Returns:
        string (str): Decoded string
    """
    return str(make_header(decode_header(string)))

def decode_filename(file_name):
    """
    Description:
        Decodes filename
    Parameters:
        file_name (str): Encoded filename
    Returns:
        file_name (str): Decoded filename
    """
    if decode_header(file_name)[0][1] is not None:
        file_name = decode_header(file_name)[0][0].decode(decode_header(file_name)[0][1])
    return file_name

def remove_square_brackets(string):
    """
    Description:
        Removes square brackets "<>" from start and end of text
    Parameters:
        string (str): Text to be stripped
    Returns:
        string (str): Stripped string
    """
    string = string.strip()
    if string.startswith("<") and string.endswith(">"): return string[1:-1]
    return string

def remove_quotes(string):
    """
    Description:
        Removes single or double quotes from start and end of text
    Parameters:
        string (str): Text to be stripped
    Returns:
        string (str): Stripped string
    """
    string = string.strip()
    if string.startswith("'") and string.endswith("'"): return string[1:-1]
    if string.startswith('"') and string.endswith('"'): return string[1:-1]
    return string

def decode_text_and_html_payload(message):
    """
    Description:
        Takes a message payload of type "text/plain" and returns decoded text
    Parameters:
        message(email.message.Message): E-mail object extracted using email package
    Returns:
        chars (str): Decoded string
    """
    bytes = message.get_payload(decode=True)
    charset = message.get_content_charset()
    chars = bytes.decode(charset, 'replace')
    return chars

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

def get_header_data(message):
    """
    Description:
        To, From, Subject and Date is extracted from an email
    Parameters:
        message(email.message.Message): E-mail object extracted using email package
    Returns:
        From (str): E-mail sender
        To (str): E-mail reciever
        Subject (str): E-mail subject
        Date (str): E-mail date
    """
    Date = ""
    if (message["date"]): Date = decode_header_string(message["date"].strip())
    
    From = ""
    if (message["from"]): From = decode_header_string(message["from"].strip())
    
    To = ""
    if (message["to"]): To = decode_header_string(message["to"].strip())
    
    Subject = ""
    if (message["subject"]): Subject = decode_header_string(message["subject"].strip())
    
    return From, To, Subject, Date

def get_email_address(string):
    """ 
    Description:
        This function extracts the email-address from a to/from string
    Parameters:
        string (str): A To/From string such as 'Hans Peter Hansen <HPH@email.dk>'
    Returns:
        address (str): HPH@email.dk
    """
    address = parseaddr(string)[1]
    
    return address

def extract_text_from_html_message(html_message, remove_comment=True, remove_hex=True):
    """ 
    Description:
        This function extracts text from an email message with the content type 'text/html'
    Parameters:
        html_message (email.message.Message): A email message with the content type 'text/html'
        encoding (str): Encoding used for decoding the message
        remove_comment (bool): Whether to remove the html text between <!-- and -->
    Returns:
        text (str): Text with no HTML
    """
    myhtml = decode_text_and_html_payload(html_message)
    soup = BeautifulSoup(myhtml, features="lxml")
    text = soup.get_text(separator=' ')
    
    if remove_comment:
        text = re.sub('<!--[^>]+-->', '', text)
    if remove_hex:
        text = re.sub(r'\xa0', '', text)
    
    return text

def extract_content(message, key, output_path):
    """
    Description:
        Extracts content from an e-mail message including multipart and nested multipart messages.
    Parameters:
        message (email.message.Message): A email message object created using the email module
        key (str): ID string for the message
        output_path (str): Output path
    Returns:
        Text (str): All texts from all parts
        Html (str): All HTMLs from all parts
        Files (dic): Dictionary mapping extracted files to message ID
        Parts (int): Number of parts in the original message
    """
    # Objects for saving output
    Html = ""
    Html_text = ""
    Text = ""
    Files = {}
    Parts = 0
    
    # Handling "pkcs7-mime"-files
    if message.get_filename() == "smime.p7m":
        decoded = message.get_payload(decode=True).decode("iso-8859-1")
        message = message_from_bytes(re.sub(r'.*Content-Type:', 'Content-Type:', decoded).encode("iso-8859-1"))  
    
    # Extracting data
    elif not message.is_multipart():
        
        # Handling Attachments
        if message.get_filename(): 
            file_name = decode_filename(message.get_filename())
            attachment_file_name = create_name(key, file_name)
            Files[file_name] = (output_path + "/" + attachment_file_name, None)
            if file_exists(output_path, attachment_file_name): 
                return Text, Html, Html_text, Files, 1
            save_file(output_path, attachment_file_name, message.get_payload(decode=True))
            return Text, Html, Html_text, Files, 1
        
        # Handling other content types
        content_type = message.get_content_type()
        if content_type=="text/plain": 
            Text += decode_text_and_html_payload(message)
        elif content_type=="text/html":
            Html += decode_text_and_html_payload(message)
            Html_text += extract_text_from_html_message(message)
        else:
            # Handling content types other than text and html
            content_type_header = message.get("content-type")
            try: 
                id = remove_square_brackets(message.get("content-id"))
            except: 
                id = None
            
            # Finding filename in content header
            o = content_type_header.find("name=")
            if o==-1: 
                return Text, Html, Files, 1
            ox = content_type_header.find(";", o)
            if name2==-1: 
                name2 = None
            o += 5; file_name = cp[o:ox]
            file_name = remove_quotes(file_name)
            output_file_name = create_name(key, file_name)
            Files[file_name] = (output_path + "/" + output_file_name, id)
            if file_exists(output_file_name): 
                return Text, Html, Files, 1
            save_file(output_path, output_file_name, m.get_payload(decode=True))
        return Text, Html, Html_text, Files, 1
    
    # Extracting data recursively for multipart messages
    y = 0
    while 1:
        # If there is not payload we have reached the end
        try:
            payload = message.get_payload(y)
        except: 
            break
            
        # The payload (Message object) goes back into the function
        text, html, html_text, files, parts = extract_content(payload, key, output_path)
        Text += text
        Html += html
        Html_text += html_text
        Files.update(files)
        Parts += parts
        y += 1
    return Text, Html, Html_text, Files, Parts

#############################
### Main wrapper function ###
#############################

def unpack_eml(eml_file, key, output_path):
    """
    Description:
        Extracts data from e-mail and returns it as a dictionary
    Parameters:
        eml_file (_io.BufferedReader): An open eml-file
        key (str): ID string for the message
        output_path (str): Output path
    Returns:
        msg (dic): A dictionary with file text and attachments is returned
    """
    eml_file_io = open_file(eml_file)
    message = message_from_file(eml_file_io)
    From, To, Subject, Date = get_header_data(message)
    Text, Html, Html_text, Files, Parts = extract_content(message, key, output_path)
    Text = Text.strip()
    Html = Html.strip()
    unpacked_eml = {"input_file": eml_file, "subject": Subject, "from": From, "to": To, "date": Date, "text": Text, "html": Html, "html_text": Html_text, "parts": Parts}
    if Files: 
        unpacked_eml["files"] = Files
    return unpacked_eml