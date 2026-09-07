.PHONY: create_venv install run_mlflow run_ui run_api clean

# Create virtual environment
create_venv:
	uv venv .venv
	@echo "Virtual environment created!"
	@echo "To activate:"
	@echo "  - Linux/Mac: source .venv/bin/activate"
	@echo "  - Windows:   .venv\\Scripts\\activate"

# Install dependencies using uv sync
install:
	uv sync

# Run the MLflow and DagsHub test script
run_mlflow:
	uv run python test_mlflow.py

# Run the Streamlit UI
run_ui:
	uv run streamlit run app.py

# Run the FastAPI server
run_api:
	uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Clean cached files
clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
