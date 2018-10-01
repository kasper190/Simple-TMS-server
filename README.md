# Simple TMS server
Simple TMS server is an application for processing and publishing the raw imagery data provided as GeoTIFF files and integrating it with Google Maps.

Technical Requirements:
- Python 3.5+
- Django framework 1.11
- python3-gdal 2.2.1
- Bootstrap 3.3.7

## Installation
To run Simple TMS server locally, first setup and activate virtual environment for it and then:

__1. Install requirements using pip:__
```shell
pip3 install -r requirements.txt
```

__2. Make migrations:__
```shell
python3 manage.py makemigrations
```

__3. Create the tables in the database by__ `migrate` __command:__
```shell
python3 manage.py migrate
```

__4.  Install GDAL2 library for Python 3:__
```shell
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt update
sudo apt install libgdal-dev python3-gdal
pip3 install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal" 
```

__5. Save some maps.__

To see how to save maps on your system, go to the MANUAL section below.

__6. Run the server:__
```shell
python3 manage.py runserver
```

__7. Go to the `"/settings/"` on your local domain and:__
- insert your Google Maps Javascript API key
- choose initial zoom
- choose initial marker position

__Now the Simple TMS server application is ready for use on `"/"` on your local domain – e.g.,__ `http://127.0.0.1:8000/`.

## Saving and removing GeoTIFF files MANUAL:
Put the GeoTIFF files in `TIF_FILES/` (`tms/TIF_FILES/`) directory and execute proper commands:

Generate tiles and create a record in the database of the `filename.tif` file:
```shell
python3 geotiff.py save filename.tif
```
Generate tiles and create a records in the database of the all files from TIF_FILES/ directory:
```shell
python3 geotiff.py saveall
```

__After saving the *.tif files, you can remove them from the TIF_FILES/ directory__

Remove tiles and record in the database of the `filename.tif` file:
```shell
python3 geotiff.py remove filename.tif
```
Remove tiles and records of all files from TIF_FILES/ directory:
```shell
python3 geotiff.py removeall
```
Display the manual:
```shell
python3 geotiff.py manual
```

<br />

__NOTE:__ The `google_markers` branch has the implementation of Google Maps markers. Branch `injected_markers` contains the implementation of markers injected into tiles.

<br />
<p align="center">
<img src="https://lh3.googleusercontent.com/mWHORxCr15v9LvcpjegZfptXUzBlf6v3R82IzsrRH_jdxdFeCpVlj4zc8LVwDJenLQWFki88MCo2KCfmB5mOt8L6TN0a2qeQkXiWprUB76b3kp4dh4QoGc0XDW0wlpkpMjDIypbGUIt79DvIv9GN4hRaEqSKF6ltEJ0oiE4YwB0pq3zSDTSDtV5tmxErRbGsi8cDZqDCFPnqusnk69oLXRjIkuR9ur6KL9TlE4boQ6m3S7Flha4LgliMPpY92I-4J1OiWt2FO6wRy0o1lPUFTzzSOHM2je5EZa3AuAT8_T9drbhRBt6cVlsovj5-s9de7MGMeNA8p17uI1NMzcO9Gs_CEJTE9NfI486EStrjj6vwFuHw2VVt6aXdChNNpWObacJBtVeWTtJpCaj2aXcN1tflUN8KUOkmRlbLX6t3ddQXWJtOqT1GgSYZi6Y6-f_MGOj9oPXq4APiCUPRVYH0cpOhtVf5dORut_KSF19T_ZuGMYf9QgaqAQjmXy4FRUnRGwNGW-OYJgB0QeClQqZdxtvbjIPIRuOxSp0VYrR4HVsl7t14BTVyjK5pRqK3fsZzYeNVL6y4JkUH8ASH47yvPzyLIU3Bl65ugUFapr838ulHyY1ax2dRrR5E-vRUm7UGIR9cYQgBq_IKzLoAmQNEI57zcEmWvHz4gAlUwNBRDY7RFJBiq3n_5KKj=w1695-h953-no" alt="TMS image 1">
</p>

<br />
<p align="center">
<img src="https://lh3.googleusercontent.com/d2NUd_bq9LMMoWCSFSub5mXTONrFStcbEGq2gRJD8APDonmvg067yTNeNN2_CUbCpOv8bBX6zKmI8SWMjKjQInKgjHPm_txCQtDpUGbULztS290fmUxRqF9EzJhTNazufY9dj8pX_nzAgeJ6GhlZJOKXEiJFeAf5U447Fal2uT8Z2gyMeIDiN0CFF3iRfVzEjDQ7ehGAjjtBjFJAKl6XWlDzfTo3H7Ab-tTBWbpAZe2Tv8rIzQOLVq2LVtcpLmmmUFj0B0C9-n2C8mwg3Zzbas6EiIxVBuxFPcUgUPzxCVIbRrh3FXUWC-hv-jFoJ4mxbbL5l6A1XwmjVUjm0sPWR8tBsJlIYR0gMcMQiDOOJ-iXyg0KjQvV1M9ss1zMDo6msGQeLoEy9vZjIQ7FikAj0bGJd9id8h_72JDYvnWYrEHV9PWUc4Crs8RAw5YL7eQ4x13bnkpgIL0sSKolKjK1TaSpr5BN73fVlbNRNJ9FJ3GqFfIPdETIocwvVvB1bzbEkeQzFbOraAz9KPK8f4AZBdZcwLxX2UA41BJ7izERXO5hxtMBZgsg_XnZqmdfkJwgSA9pNnWJsi49gGfaSI9z1zdR4yTdcDkIgAIy5qNah3ZQKrvKIOHT6GLSo35eGR9AFsdulTqiUTaEW-9PB5f0LkQA4_Jj4WXIGL7a3LkwwT3x6y2ZZ1s_S8xE=w1695-h953-no" alt="TMS image 2">
</p>

<br />
<p align="center">
<img src="https://lh3.googleusercontent.com/cDS6kyU98RyznpMsgN4chLyI2g88Z0TfPQJYhx7aziONInwezDtb90PxoxvH5bBxwD-4Y77mek6tIMl0i39ALOO6qZena3nrnZWvgvtKJex2wORlBLXXf93RatniVI_21_wlO1MWkYbheNne0ReXSmdApKIJGmB7F6-L25vAdLj7mCYB_19-Dn5i_eFL3HcfwoA7b44ZqrIZQBmzKsSVbi1JLgmgH_qKf65gGmh7yx9uxWqMS6X9T5H612zp9-gFv7iXeWNTeUQnPW_wWdyswzuXRbzh0xZedGE0QXt-A5IEOJHs5purFAiPLsOdXjjES32SPL74xWU-j4ZDe40-aCtcjwL11oMNmTwsdAjOMxnfuFJXY5sJF5d7Kc7F1H-8DU1kmIIVGsK0FXC_ZUH6MfFtUceNhriESRLkNTuIeR5VmrFnKKaYM7OqCq4hR9sbeq-wYIhRW8QIiMZHIikcUKWlCCpoyT9X9ei7Yg_wCdYpITv3LmQ4D_QEU0CF_8rJaQExN5Hpki80UWkNU09PZ9KY0MeQDDUha3RZ88JTotWijlrQC4dnrOoLAf1iX6yRexibjuS-xTZE10Ut6rBfOxA-BiVqG_Q7vB-whUmxUkQP5gCnMP0INAnoN1bostmGnBT3eUMV6JBcm7fZCgdLCwU6sux3FDwjIdAibv-KLKc1V-tkzWse1vSd=w1695-h953-no" alt="TMS image 3">
</p>

