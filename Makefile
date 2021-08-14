SOURCE = $(wildcard *.tex images/*)
DOC = report

$(DOC).pdf: $(SOURCE)
	latexmk -pdf -shell-escape -interaction=nonstopmode $(DOC).tex

.PHONY: wipe clean distclean watch

wipe:
	rm -f $(DOC).synctex.gz
	rm -rf _minted-$(DOC)

clean: wipe
	latexmk -c

distclean: wipe
	latexmk -C

watch:
	latexmk -pdf -pvc -shell-escape -interaction=nonstopmode $(DOC).tex
