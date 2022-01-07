FROM python:3.9-slim-bullseye
ADD . ./ergo/
WORKDIR ./ergo
RUN pip install -r ./requirements.txt
CMD ["python","./bot.py"]