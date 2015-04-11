import os
import mimetypes
import chardet

UTF8 = ('utf-8', 'ascii')
WANTED_CHARSET = UTF8
FILE_PATH = '.'
THRESHOLD = 0.6

# Chardet cannot recognize ISO-8859-1 charset.
RECOGNIZE_8859_2_AS_8859_1 = True

LOG_FILE_CONVERTED = '/dcclog/converted'
LOG_FILE_UNCONVERTED = '/dcclog/unconverted'
LOG_FILE_CAN_NOT_DETECT = '/dcclog/can_not_detect'
LOG_FILE_FILENAME_IS_NOT_TEXT_FILE = '/dcclog/not_text_file'
LOG_FILES = (
    LOG_FILE_CONVERTED,
    LOG_FILE_UNCONVERTED,
    LOG_FILE_CAN_NOT_DETECT,
    LOG_FILE_FILENAME_IS_NOT_TEXT_FILE,
)
IGNORED = ('.git', '.idea', 'dcclog', 'dcc.py', '.gitignore')
MIME_EXTRA_TEXT_TYPES = (
    'application/javascript',
    'application/x-sh',
    'application/xml',
)


def init_log():
    try:
        os.mkdir(FILE_PATH+'/dcclog')
    except FileExistsError:
        pass

    for file in LOG_FILES:
        try:
            os.remove(FILE_PATH + file)
        except FileNotFoundError:
            pass


def log(logfile, file_path_name, mime_type, encoding, confidence):
    with open(FILE_PATH + logfile, 'at') as file:
        l = '{}, {}, {}, {}\n'.format(file_path_name, mime_type, encoding, confidence)
        file.write(l)


def ignored(dirpath, filename):
    while not os.path.samefile(dirpath, FILE_PATH):
        dirpath, filename = os.path.split(dirpath)
    # print(dirpath, filename, sep='< ^o^ >')
    if filename in IGNORED:
        return True


def _main():
    init_log()
    for dirpath, dirnames, filenames in os.walk(FILE_PATH):
        for filename in filenames:
            if ignored(dirpath, filename):
                continue
            encoding = None
            confidence = None
            mime_type = mimetypes.guess_type(filename, strict=False)[0]
            file_path_name = os.path.join(dirpath, filename)
            if mime_type is None or mime_type.startswith('text') or mime_type in MIME_EXTRA_TEXT_TYPES:
                with open(file_path_name, 'rb') as file:
                    content = file.read()
                    detect = chardet.detect(content)
                    encoding = detect['encoding']
                    confidence = detect['confidence']
                    if RECOGNIZE_8859_2_AS_8859_1 and encoding == 'ISO-8859-2':
                        encoding = 'ISO-8859-1'
                if confidence < THRESHOLD:
                    log(LOG_FILE_CAN_NOT_DETECT, file_path_name, mime_type, encoding, confidence)
                elif encoding in WANTED_CHARSET:
                    log(LOG_FILE_UNCONVERTED, file_path_name, mime_type, encoding, confidence)
                else:
                    with open(file_path_name, 'wb') as file:
                        file.write(content.decode(encoding).encode(WANTED_CHARSET[0]))
                    log(LOG_FILE_CONVERTED, file_path_name, mime_type, encoding, confidence)
            else:
                log(LOG_FILE_FILENAME_IS_NOT_TEXT_FILE, file_path_name, mime_type, encoding, confidence)


if __name__ == '__main__':
    _main()