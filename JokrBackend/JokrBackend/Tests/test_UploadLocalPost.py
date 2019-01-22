#===============================================================================
# Testing the UploadLocalPost functionality.
#
# Nick Wrobel
# Created: 5/5/15
# Modified: 5/5/15
#===============================================================================

from django.core.urlresolvers import reverse
from django.test import TestCase
from JokrBackend.Models.LocalPostModel import LocalPost
import json
import base64


class UploadLocalPostViewTest(TestCase):
    def test(self):
        #Create all the fake json data      
        latitude = 123.3242423
        longitude = 90.534532
        
        # Read a fake image file. We are assuming client is sending us the image
        # in Json as a base64 string.
        # with open("/var/webserver-data/test/local/source/1920x1080.jpg.gz", "rb") as imageFile:
        #    imageStr = base64.b64encode(imageFile.read()).decode()
            
        with open("/var/webserver-data/test/local/source/1920x1080.jpg.gz", "rb") as imageFile:
            imageStr = base64.b64encode(imageFile.read()).decode()
        
        
        
        # Various json possiblities to test
        data = { 'latitude': latitude,
                 'longitude': longitude,
                 'image': imageStr
                }
        
        bsData1 = { 'hello': latitude,
                 'goodbye': longitude,
                 'image': imageStr
                }
    
        bsData2 = { 'latitude': 'ayy',
                   'longitude': 'lmao',
                   'image': imageStr
                   }
               

        # Test a GET request with no Json
#         response = self.client.get('/UploadLocalPost/')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), str(-1))
#          
#         # Test a POST request with no Json
#         response = self.client.post('/UploadLocalPost/')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), str(-1))
#          
#         # Test a POST request with bs random content (not json)
#         response = self.client.post('/UploadLocalPost/', content_type='application/json', data='sdfgdsfgsdf34')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), str(-1))
#         
#         # Test a POST request with bs Json1
#         # Case Json data is valid, but key names are messed up
#         response = self.client.post('/UploadLocalPost/', content_type='application/json', data=json.dumps(bsData1))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), str(-1))
#         
#         # Test a POST request with bs Json2
#         # Case Json data is a bad data type but has the right key names
#         response = self.client.post('/UploadLocalPost/', content_type='application/json', data=json.dumps(bsData2))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.content.decode(), str(-1))
        
        # Test a POST request with Json (correct)
        response = self.client.post('/UploadLocalPost/', content_type='application/json', data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), str(0))
        
        # Now that we've got the data saved in the db, pull it back out and 
        # test the integrity.
        # Querying the database through django's API: look in the LocalPosts model
        # (table) of the db and return the first object (row) in there
        savedPost = LocalPost.objects.first()
        
        # Print the data to be sure
        print(savedPost.__getattribute__('timeCreated'))
        print(savedPost.__getattribute__('ipAddress'))
        print(savedPost.__getattribute__('latitude'))
        print(savedPost.__getattribute__('longitude'))
        print(savedPost.__getattribute__('image'))
    
        
