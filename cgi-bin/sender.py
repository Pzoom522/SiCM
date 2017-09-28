def send(userId):
	import boto3
	# Create SQS client
	sqs = boto3.client(
    	'sqs',
   	aws_access_key_id=YOUR_OWN_ACCESS_KEY_ID,
    	aws_secret_access_key=YOUR_OWN_SECRET_ACCESS_KEY,
	region_name=YOUR_OWN_REGION
)

	queue_url = 'https://cn-north-1.queue.amazonaws.com.cn/444376591338/sicm'
	sqs.set_queue_attributes(
    	QueueUrl=queue_url,
    	Attributes={'ReceiveMessageWaitTimeSeconds': '20'}
)

	# Send message to SQS queue
	response = sqs.send_message(
	    QueueUrl=queue_url,
	    DelaySeconds=5,
	    MessageAttributes={
	        'UserID':{
	        	'DataType':'String',
	        	'StringValue':str(userId)
	        }
	    },
	    MessageBody=(
	        'trail info X'
	    )
	)

	#print(response['MessageId'])     
