.PHONY: publish
publish:
	pandoc pages/README.org --from=org --to=html5 \
    		--standalone --toc --self-contained \
		--resource-path=".:pages:results" \
		-o publish/index.html

# --css=style.css \
