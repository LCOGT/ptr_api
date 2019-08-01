# This file is for pieces of code that aren't in use or are broken, but 
# still worth saving for reference.

S3_BUCKET = 'pythonbits'
REGION = 'us-east-1'

# Stream a file upload directly to s3. 
# Almost works; but creates an invalid 4.0 KB file.
@application.route('/<site>/upload/', methods=['POST'])
def upload(site):
    s3 = boto3.resource('s3', REGION)
    chunk_size = 4096
    filename = f"{time.time()}_flaskupload.fits"
    s3.Object(S3_BUCKET, filename).put(Body=request.stream.read(chunk_size))

#-----------------------------------------------------------------------------#

        
@application.route('/local/', methods=['GET', 'POST'])
def start_s3():
    try:
        t1 = threading.Thread(target=start_s3)
        t1.start()
    except Exception as e: 
        print(e)
        return jsonify({"error": e})
    return "local s3 server started at port 5001"

@application.route('/local/test')
def test_local_s3():
    createbuckets()
    buckets = listbuckets()
    return jsonify({"buckets":buckets})



def start_s3():
    try:
        subprocess.call(["moto_server", "s3", "-p5001"])
    except Exception as e:
        print(e)

@mock_s3
def listbuckets():
    s3 = boto3.resource('s3', region_name='us-east-1', endpoint_url='http://localhost:5001')
    buckets = [bucket.name for bucket in s3.buckets.all()]
    #print(buckets)
    return buckets

@mock_s3
def createbuckets(names=['a-totally-unique-moto-bucket-name', 'moto']):
    s3 = boto3.resource('s3', region_name='us-east-1', endpoint_url='http://localhost:5001')
    for name in names:
        s3.create_bucket(Bucket=name)
