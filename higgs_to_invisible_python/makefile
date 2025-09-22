# User-configurable paths
PYTHON    = python
RUNCOUNT  = scripts/run_counting.py
SUMMARY   = scripts/summarize_results.py

# Files
YIELDS    = yields.json
SUMMARYJS = results_summary.json

# Default target: full workflow
all: $(SUMMARYJS)

# Step 1: produce yields.json
$(YIELDS): $(RUNCOUNT)
	$(PYTHON) -m scripts.run_counting

# Step 2: produce results_summary.json from yields.json
$(SUMMARYJS): $(YIELDS) $(SUMMARY)
	$(PYTHON) -m scripts.summarize_results

# Clean up
clean:
	rm -f $(YIELDS) $(SUMMARYJS)

.PHONY: all clean
