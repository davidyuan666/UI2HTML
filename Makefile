# GitHub repository management commands
.PHONY: commit push pull status clean

# Default git commit message
MESSAGE ?= "Update repository"


.PHONY: install
install:
	pdm install


# Git commands
status:
	git status

pull:
	git pull origin main

commit:
	git add .
	git commit -m $(MESSAGE)
	git push origin main

# Clean unnecessary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name ".ipynb_checkpoints" -delete

# Help command
help:
	@echo "Available commands:"
	@echo "  make status    - Show git status"
	@echo "  make pull      - Pull from main branch"
	@echo "  make commit    - Add and commit changes (use MESSAGE='your message' to customize)"
	@echo "  make push      - Push to main branch"
	@echo "  make deploy    - Commit and push in one command"
	@echo "  make clean     - Remove temporary files"