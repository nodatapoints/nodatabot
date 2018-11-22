#!/bin/zsh

# ja das geht auch mit bash.

working_dir=$(mktemp -d)
old_dir=$PWD
cd $working_dir

cat - > main.tex
if ! latexmk main.tex &>/dev/null; 
then
  echo "FAILED."
  exit 3
fi
dvipng -D $1 main.dvi &>/dev/null
convert	*.png -bordercolor white -border x20% main.png
cp "$working_dir/main.png" "$old_dir/ext/main.png"
echo "$old_dir/ext/main.png"
rm -r "$working_dir"

