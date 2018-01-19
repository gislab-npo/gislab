FROM gisquick/django:latest


RUN pip3 install --no-cache-dir 'django-python3-ldap==0.10' && \
    pip3 install --no-cache-dir --upgrade 'ldap3==2.3'


COPY settings_custom.py /var/www/gisquick/djproject/settings_custom.py
COPY urls_custom.py /var/www/gisquick/djproject/urls_custom.py
