# txt2pdf

Convert one or more text files to a PDF document using LaTeX typesetting.

This tool was developed for typesetting novels and short story collections written in pure text files.
The goal is to keep the text files as clean as possible with a minimum of structured formatting, i.e. a harsh subset of Markdown.

Most people writing fiction and literature use Word, Pages, Scrivener or some other WYSIWYG editor.
However, there are many reasons to use a plain text editor, e.g. better text editing, less distraction of text formatting and productivity features such as full screen and zen modes (as found in [Visual Studio Code](https://code.visualstudio.com/) and [Sublime Text](https://www.sublimetext.com/)).

One drawback, though, is the difficulties in producing a good looking, formatted and typeset document (to be sent to publishers). This is the problem that txt2pdf tries to solve.

## Prerequisites

* Python 3
  * jinja2
  * langdetect
* [MikTex](https://miktex.org/) \[Windows] or `texlive` packet \[Debian or Ubuntu Linux]

## Installation

1. Clone or download this project.

2. Create an isolated Python environment using **virtualenv** or just use the system installation and make sure the required packages are installed using the **requirement.txt** file.

   On Windows:

       py -3 -m pip install -r requirement.txt

   On Linux:

       python3 -m pip install -r requirement.txt

3. Run the following command to read more about the command line arguments:

   On Windows:

       py -3 txt2pdf.py --help

   On Linux:

       python3 txt2pdf.py --help

On Windows: When running the script for the first time (with real and valid inputs) MikTex will install multiple LaTeX packages. You should accept this.

## Example

Let's say you have written The Great Novel. It consists of ten chapters in ten separate text files. All the files are located in the same directory among other useful resources for the writing project.

An example directory tree could look like this:

```text
TheGreatNovel
│   chapter01.txt
│   chapter02.txt
│   chapter03.txt
│   chapter04.txt
│   chapter05.txt
│   chapter06.txt
│   chapter07.txt
│   chapter08.txt
│   chapter09.txt
│   chapter10.txt
│
└───fragments
│   │   ...
│
└───old
│   │   ...
│
└───research
│   │   ...
│   │
│   └───maps
│       │   ...
│
└───build
    │   generate_book.bat
    │   the_great_novel.pdf
    │
    └───env
    |   │   ...
    │
    └───txt2pdf
        │   ...
```

A recommendation is to create a directory (called _build_ in the example above) with a batch or bash script that creates the PDF document. If you have a big writing project with lots of chapters or short stories (i.e. text files) the list of command arguments can be quite long. You don't want to type it every time...

Besides, using a script makes it easy and fast to generate the PDF document and you want to be agile also when you write The Great Novel. Right?

The **generate_book.bat** could look something like this:

```batch
@echo off
env\Scripts\python txt2pdf\txt2pdf.py ^
--title The Great Novel ^
--author John Doe ^
--output the_great_novel ^
chapter01.txt ^
chapter02.txt ^
chapter03.txt ^
chapter04.txt ^
chapter05.txt ^
chapter06.txt ^
chapter07.txt ^
chapter08.txt ^
chapter09.txt ^
chapter10.txt ^
```

## Text file format

The input text files to txt2pdf are plain text files. You shouldn't need to worry about formatting. There are just a few "features" to remember.

The first line of the text file represent the chapter name (or the name of the short story). E.g. **chapter01.txt** in the example above could look like this:

```text
Chapter one

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
mollit anim id est laborum.
```

Minus characters in the text are converted to dashes when appropriate.

### Markdown subset

A very small subset of Markdown syntax is supported (i.e. only what I, the author of txt2pdf, so far have needed...).

Emphasis, aka italics, are marked using underscores:

```text
You don't know anything, dear. _I killed the captain!_, said the butler.
```

Quotes can be written like this to get a nice format in the output:

```text
The next day a read the following in the newspaper:

> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
> et dolore magna aliqua.

I couldn't believe my eyes.
```

Verses can be written with with four spaces. Line breaks will then be kept. E.g.:

```text
Suddenly she started to recite a poem:

    Lorem ipsum dolor sit amet
    consectetur adipiscing elit,
    sed do eiusmod tempor incididunt
    ut labore et dolore magna aliqua

I couldn't believe my ears.
```

## Output typesetting

Since LaTeX is used in the background for the actual typesetting, people familiar with LaTeX will recognize the typesetting of the output.
I have used the document classes that I think look good. If someone wants to change the look of the PDF output [template.tex](./template.tex) is a good start.
