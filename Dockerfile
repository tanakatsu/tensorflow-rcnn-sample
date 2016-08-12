# Inherit from Heroku's python stack
FROM heroku/python

WORKDIR /app/user
RUN apt-get update
RUN apt-get install -y liblapack-dev libatlas-base-dev gfortran g++
ADD requirements.txt /app/user/
RUN /app/.heroku/python/bin/pip install -r requirements.txt
RUN pip install numpy
RUN pip install scipy
RUN pip install scikit-image
RUN pip install selectivesearch
ADD . /app/user/

CMD ["gunicorn", "main:app"]

