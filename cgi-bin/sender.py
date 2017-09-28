def send(userId):
	import boto3
	# Create SQS client
	sqs = boto3.client(
    	'sqs',
   	aws_access_key_id="AKIAPNCADUXD3HUR2QMQ",
    	aws_secret_access_key="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",
	region_name="cn-north-1"
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