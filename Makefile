.PHONY: publish
publish:
	pandoc pages/README.org --from=org --to=html5 \
    		--embed-resources --standalone --toc \
		--resource-path=".:pages:results" \
		--css=publish/style.css \
		-o publish/index.html

