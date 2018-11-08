#!/bin/zsh

# ja das geht auch mit bash.

working_dir=$(mktemp -d)
old_dir=$PWD
cd $working_dir

cat - > main.tex
if ! latexmk main.tex &>/dev/null; then
  echo "FAILED."
  exit 3
fi
if [[ $1 != '-invert' ]]; then
	dvipng -D 900 main.dvi &>/dev/null
	BORDERCOLOR=white
else
	dvipng -D 900 main.dvi -bg 'rgb 0 0 0' -fg 'rgb 1 1 1' &>/dev/null
fi
convert	main*.png -bordercolor ${BORDERCOLOR:-black} -border x20% -resize x500 main.png
echo $working_dir/main.png
