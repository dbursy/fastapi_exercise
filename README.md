# FastAPI Exercise

## Prerequisites: Virtual Environment

Create and activate the python virtual environment in the local project folder
 
```bash
python3 -m venv mlops_env
source mlops_env/bin/activate
```
 
If this step is successfull the comand line displays the prefix `(mlops_env)`. Continue by installing required Python packages
 
```bash
python -m pip install -r requirements.txt
```
 
Note: To create or update the requirements file, please run
 
```bash
pip freeze > requirements.txt
```

## Start and test the API service

```bash
uvicorn api.main:api --reload
```

Test the API using the following notebook `notebooks/quiz_api_text.ipynb` or access the documentation via `http://localhost:8000/docs`.

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)