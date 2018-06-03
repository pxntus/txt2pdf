#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""txt2pdf - Convert one or more text files to a PDF document using LaTeX typesetting.

This tool was developed for typesetting novels and short story collections written in pure text files.
The goal is to keep the text files as clean as possible with a minimum of structured formatting, i.e. a harsh subset of Markdown.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
import glob
import re

import jinja2
import langdetect


# Exception classes.

class InvalidInputTxtFileException(Exception):
    def __init__(self, filename=None):
        self.filename = filename

    def __str__(self):
        if self.filename is not None:
            return self.filename

class ErrorWhenExecutingLatexException(Exception):
    def __init__(self, completed_process=None):
        self.completed_process = completed_process

    def __str__(self):
        if self.completed_process is not None:
            return self.completed_process.stderr


TEX_ITALIC_PRE_STR = r"\emph{"
TEX_ITALIC_POST_STR = r"}"

def convert_simplified_markdown_to_latex(content):

    # Pre-process text to make it properly LaTeX formatted
    content = content.replace('"', "''")            # proper citation marks
    content = content.replace(' - ', ' -- ')        # proper LaTeX dash
    content = content.replace('&', r'\&')           # proper '&' character
    content = content.replace('#', r'\#')           # proper '#' character
    content = re.sub(r'\[\[.*?\]\]', '', content)   # Remove text between [[ ... ]] delimiters
    content = re.sub(r"\n- ", r"\n-- ", content)    # replace dash at the beginning of line

    # Convert text between underscores to emphasized formatting.
    emphasized_text_state = False
    pos = content.find('_')
    while (pos >= 0):
        if emphasized_text_state:
            content = content[0:pos] + TEX_ITALIC_POST_STR + content[pos+1:]
            pos += len(TEX_ITALIC_POST_STR) - 1  # minus one for underscore
            emphasized_text_state = False
        else:
            content = content[0:pos] + TEX_ITALIC_PRE_STR + content[pos+1:]
            pos += len(TEX_ITALIC_PRE_STR) - 1  # minus one for underscore
            emphasized_text_state = True
        pos = content.find('_')
    if emphasized_text_state:
        print("Warning: Unfinished emphasized text marker!", file=sys.stderr)

    paragraphs = content.splitlines()
    title = paragraphs[0]
    paragraphs = paragraphs[1:]
    new_paragraphs = []

    # Pre-process various quotes
    verse = False
    quote = False
    for paragraph in paragraphs:
        if paragraph[0:4] == "    ":
            if not verse:
                # Start of verse
                new_paragraphs.append('\\begin{verse}')
                new_paragraphs.append(paragraph.lstrip() + '\\\\')
                verse = True
                continue
            else:
                # After first line of verse
                new_paragraphs.append(paragraph.lstrip() + '\\\\')
                continue
        elif verse:
            # End of verse
            new_paragraphs.append('\\end{verse}')
            verse = False
        if paragraph[0:2] == "> ":
            if not quote:
                # Start of quote
                new_paragraphs.append('\\begin{quote}')
                new_paragraphs.append(paragraph[2:])
                quote = True
                continue
            else:
                # After first line of quote
                new_paragraphs.append('\\\\' + paragraph[2:])
                continue
        elif quote:
            # End of quote
            new_paragraphs.append('\\end{quote}')
            quote = False
        if paragraph == "*":
            new_paragraphs.append('\\vspace{6mm}')
        else:
            new_paragraphs.append(paragraph)
    content = "\n".join(new_paragraphs)

    return (title, content)


def preprocess_input(args):
    metadata = {}
    metadata['title'] = ' '.join(args.title)
    metadata['author'] = ' '.join(args.author)
    metadata['multiple_chapters'] = len(args.sources) > 1
    metadata['wide_line_spacing'] = args.wide_line_spacing
    metadata['chapters'] = []

    lang_detect_input = None

    # Process inputs
    if args.basepath is not None:
        basepath = args.basepath
    else:
        basepath = '../'

    for path in args.sources:
        path = os.path.join(basepath, path)
        try:
            with open(path, 'rU') as f:
                content = f.read()
        except IOError:
            raise InvalidInputTxtFileException(path)

        if lang_detect_input is None:
            # Use content from first input to detect language.
            lang_detect_input = content

        (chapter_title, chapter_content) = convert_simplified_markdown_to_latex(content)
        chapter_metadata = {'title': chapter_title, 'content': chapter_content}
        metadata['chapters'].append(chapter_metadata)

    # Detect language
    detected_language = langdetect.detect(lang_detect_input)
    language_dict = {
        'sv': 'swedish',
        'en': 'english'
    }
    if detected_language in language_dict:
        metadata['language'] = language_dict[detected_language]
    else:
        print("Add support for more languages!", file=sys.stderr)
        metadata['language'] = None

    return metadata


def find_latex_binary():
    # Only supports Windows for now. This should be the only code that needs to be fixed to support Linux.
    for filename in glob.iglob("c:/Program Files/**/pdflatex.exe", recursive=True):
        return filename
    for filename in glob.iglob("c:/Program Files (x86)/**/pdflatex.exe", recursive=True):
        return filename
    home = os.path.expanduser("~")
    for filename in glob.iglob(home + "/**/pdflatex.exe", recursive=True):
        return filename
    return None


def generate_latex_source(metadata, tex_path):
    template_dir = os.path.dirname(os.path.realpath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    tex_template = env.get_template('template.tex') 
    with open(tex_path, 'w') as tex_file:
        tex_file.write(tex_template.render(metadata))


def generate_pdf_output(latex_bin, tex_path, temp_dir):
    result = subprocess.run([latex_bin, tex_path, "-quiet", "-halt-on-error", "-output-directory", temp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise ErrorWhenExecutingLatexException(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a PDF out of one or more text files.')
    parser.add_argument('sources', metavar='path', type=str, nargs='+', help='text file(s)')
    parser.add_argument('--title', nargs='+', help='Document title.')
    parser.add_argument('--author', nargs='+', help='Document author.')
    parser.add_argument('--basepath', help='Base path of text file(s).')
    parser.add_argument('--output', default='nameless', help='Output filename.')
    parser.add_argument('--wide-line-spacing', action='store_true', help='Extra wide line spacing.')
    args = parser.parse_args()

    try:
        print("Looking for LaTeX binaries on your system...")
        latex_bin = find_latex_binary()
        if latex_bin is None:
            print("Could not find LaTeX on your system!")
            sys.exit(1)

        print("Processing input...")
        metadata = preprocess_input(args)

        temp_dir = tempfile.mkdtemp()
        tex_path = os.path.join(temp_dir, args.output + ".tex")
        output_filename = args.output + ".pdf"
        pdf_path = os.path.join(temp_dir, output_filename)

        print("Generating intermediate files...")
        generate_latex_source(metadata, tex_path)
        print("Generating PDF '{}'...".format(output_filename))
        generate_pdf_output(latex_bin, tex_path, temp_dir)
        shutil.copy(pdf_path, "./")

        print("Cleaning up intermediate files...")
        shutil.rmtree(temp_dir)

    except InvalidInputTxtFileException as e:
        print("Couldn't find input file '{}'!".format(e.filename), file=sys.stderr)
        sys.exit(1)

    except ErrorWhenExecutingLatexException as e:
        print("Something bad happened during LaTeX execution!\n")
        if e.completed_process.stderr is not None:
            print(e.completed_process.stderr)
        print("Copying generated tex file and log file for debugging...\n")
        shutil.copy(os.path.join(temp_dir, args.output + ".log"), "./")
        shutil.copy(os.path.join(temp_dir, args.output + ".tex"), "./")
        shutil.rmtree(temp_dir)
        sys.exit(1)

    #except:
    #    print("Unexpected error: {}".format(sys.exc_info()[0]))
    #    print(str(sys.exc_info()[2]))
