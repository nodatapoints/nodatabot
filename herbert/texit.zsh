#!/bin/zsh

# ja das geht auch mit bash.

#exit status (higher numbers are worse):
# 0 - ok
# 2 - failed cleanup
# 3 - failed converting pdf to png
# 4 - failed compiling tex

working_dir=$(mktemp -d)
old_dir=$PWD
cd $working_dir

cat - > main.tex

if ! latexmk -xelatex -interaction=nonstopmode main.tex &>/dev/null;
then
  exit 4
fi

if ! {
    dvisvgm main.pdf --pdf --output=main.svg &>/dev/null
    inkscape -z main.svg -w ${1:-1920} -b#FFFFFF -e main.png &>/dev/null
    cp "$working_dir/main.png" "$old_dir/ext/main.png"
    echo "$old_dir/ext/main.png"
    }
then
    exit 3
fi

rm -r "$working_dir" || { echo "$working_dir"; exit 2 }

