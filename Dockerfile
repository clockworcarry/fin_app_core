FROM python:3.9

WORKDIR .

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY api/ /code/app/api/
COPY calc_engine/ /code/app/calc_engine/
COPY core/ /code/app/core/
COPY data_vendors/ /code/app/data_vendors/
COPY db/ /code/app/db/
COPY fin_app_crons/ /code/app/fin_app_crons/

ENV PYTHONPATH="${PYTHONPATH}:/code/app"

#CMD ["/bin/bash"]
#CMD ["python3"]
CMD ["python3", "/code/app/api/server.py", "--config_file_path", "/code/app/api/config.json"]
#CMD ["uvicorn", "api.server:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]