FROM python:3.8

ARG project_dir=/projects/

ADD requirements.txt $project_dir
WORKDIR $project_dir
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

COPY ./web $project_dir/web

ENTRYPOINT ["python", "-m", "web.main"]
