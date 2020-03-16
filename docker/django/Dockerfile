FROM python:3.7

# RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
# RUN apt-get update && apt-get install -y npm netcat nodejs
RUN apt-get update
RUN apt-get install netcat -y

RUN pip install --upgrade pip  # make things faster, hopefully

COPY CompetitionPlatform/requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV PATH="/app/utils:${PATH}"

WORKDIR /app/CompetitionPlatform
