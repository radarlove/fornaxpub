""" astropy_s3_presigned_https_uri_fsspec_range_test.py
	
	Test whether astropy fits/fsspec can pull only a section of an S3 when
	using a pre-signed HTTPS URL to point to the S3.

	This works but requires some different invocation than with an S3 url.
	Worked on Linux, but not on my Mac Sonoma 14.5 due to SSL issues.

	The S3 example (below) in the astropy docs:
		https://docs.astropy.org/en/latest/io/fits/usage/cloud.html
	will return a section or cutout using a presigned HTTPS URL, but
	** only after first downloading the entire file **.

	The invocation must change from:

    	with fits.open(s3_uri, fsspec_kwargs=\{"anon" : True}) as hdul:

	to:
	
     	with fits.open(s3_presigned_uri, use_fsspec=True) as hdul:

	Original
	--------

        #Download a small 10-by-20 pixel cutout from a FITS file stored in Amazon S3

        with fits.open(s3_uri, fsspec_kwargs={"anon": True}) as hdul:
            cutout = hdul[1].section[10:20, 30:50]



	The test used the following S3 fits URI and generated the pre-signed URL as follows:

        s3_uri = 's3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits'
        s3_presigned = os.popen('aws s3 presign %s' % s3_uri).read().strip()

	Successful output will look like the following with no Download progress displayed
    and the presigned download being very quick, perhaps even faster than the S3.

    The failure case will at best show a much longer download that can be watched
	for perhaps 10 to 30 seconds.

	Sample (cut presigned URI lines at 70 chars long to fit here:
	-------------------------------------------------------------

		(astro) ubuntu@ip-10-0-53-53:~$ python astropy_s3_presigned_https_uri_fsspec_range_test.py 
		1721569108.4048135
		Fits cutout 10x20 with s3_uri: s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits
		--
		Fetched cutout of length: 800 bytes
	  * Fetched in: 0.6296992301940918      
		Fits cutout with s3_presigned_uri: 

			https://stpubdata.s3.aws.com/hst/public/j8pu/j8pu0y010/j8pu0y01...
            gyd6tbZUiEvT78%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEIb%2F%2...
			k%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEmka5v1ySRIdlduLZzRMLaA...
	        ....
            r0Vu1GaReKn%2FoSqWWBosMYIfVyTCI2GS0BoZQfW5dY%3D&Expires=1721572708

		--
		Fetched cutout of length: 800 bytes
	  *	Fetched in: 0.21128630638122559
"""

import os
import time

from astropy.io import fits
from urllib.parse import unquote


s3_uri = 's3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits'
s3_presigned = os.popen('aws s3 presign %s' % s3_uri).read().strip()

start = time.time()
print(start)
print('Fits cutout 10x20 with s3_uri: %s' % s3_uri)
print('--')
with fits.open(s3_uri, fsspec_kwargs={"anon": True}) as hdul:  
    cutout = hdul[1].section[10:20, 30:50]
    cbytes = cutout.tobytes()
    l = len(cbytes)
    print('Fetched cutout of length: %s bytes' % l)

fin = time.time()

print('Fetch in: %s' % (fin-start))
print('Fits cutout with s3_presigned_uri: %s' % s3_presigned)
print('--')
with fits.open(s3_presigned, use_fsspec=True) as hdul:  
    pcutout = hdul[1].section[10:20, 30:50]
    pcbytes = pcutout.tobytes()
    l = len(pcbytes)
    print('Fetched cutout of length: %s bytes' % l)

end = time.time()
print('Fetch in: %s' % (end-fin))
