FROM python:3

RUN echo "now building..."

ARG project_dir=/usr/src/app

WORKDIR $project_dir
ADD requirements.txt $project_dir
ADD server.py $project_dir
ADD settings.py $project_dir

RUN pip install -r requirements.txt
CMD ["python", "server.py"]