import dagshub
import mlflow

# Initialize DagsHub tracking
dagshub.init(repo_owner='abdallahatefhatem', repo_name='LangChain-Multi-Agent-Research-System', mlflow=True)

# Start an MLflow run and log a parameter and a metric
with mlflow.start_run():
    mlflow.log_param('parameter name', 'value')
    mlflow.log_metric('metric name', 1)
    
print("Successfully logged to DagsHub via MLflow!")
