# test_client.py
import poster
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import urllib2
import uuid

# Register the streaming http handlers with urllib2
register_openers()

# Start the multipart/form-data encoding of the file "DSC0001.jpg"
# "image1" is the name of the parameter, which is normally set
# via the "name" parameter of the HTML <input> tag.

# headers contains the necessary Content-Type and Content-Length
# datagen is a generator object that yields the encoded parameters
file = MultipartParam.from_file("file1", "test.tlog")
file.filetype = 'application/vnd.mavlink.tlog'
params = {
    #'tlog1.tlog': file, # the name doesn't matter if the content type is correct
    #'tlog1.tlog': open("mav.tlog", "rb"),
    'autoCreate': 'true',
    'login': 'test-bob10',
    'password': 'secretsecret8',
    'email': 'kevinh+pytest@geeksville.com',
    'fullName': 'Bob Bumblesticks',
    'api_key': 'YOURDEVCODE.YOURAPPKEY'
    }
datagen, headers = poster.encode.multipart_encode(MultipartParam.from_params(params) + [file])

# Create the Request object

vehicle = str(uuid.uuid1(clock_seq = 0))
request = urllib2.Request("https://api.3drobotics.com/api/v1/mission/upload/" + vehicle, datagen, headers)
# Actually do the request, and get the response
print urllib2.urlopen(request).read()