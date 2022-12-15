all: paper

paper: paper.tex cites.bib
	xelatex paper
	biber paper
	xelatex paper
	xelatex paper

clean:
	rm -f *.aux *.bcf *.log *.out *.xml *.bbl *.blg *.fff

wipe: clean
	rm -f *.pdf
