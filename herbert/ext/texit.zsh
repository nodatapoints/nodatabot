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

clean_exit () {
  rm -r "$working_dir" || { echo "$working_dir"; exit 2 }
  exit $1
}

cat - > main.tex

if ! pdflatex -interaction=nonstopmode main.tex &>/dev/null;
then
  clean_exit 4
fi

if ! {
        pdftoppm -scale-to-x ${1:-1920} -scale-to-y -1 -singlefile -q -png main.pdf main
        cp "$working_dir/main.png" "$old_dir/ext/main.png"
        echo "$old_dir/ext/main.png"
    }
then
    clean_exit 3
fi

clean_exit 0


