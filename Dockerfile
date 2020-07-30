FROM python:3

RUN echo "now building..."

ARG project_dir=/usr/src/app
ARG web_dir=/usr/src/app/web

WORKDIR ${web_dir}
ADD web ${web_dir}/

RUN pip install -r ../requirements.txt
RUN cd ${project_dir}
CMD ["gunicorn" "web.server:app"]