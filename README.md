# Video Scene Detection Application

A microservice based application that detects shots and subshots from an input video.

## Tech Stack Used
- AWS Components: Amazon MQ (Rabbit MQ), S3, SQS, SNS, Rekognition
- Frameworks: Flask, SocketIO, PySceneDetect

## Architecture
The system composed of primarily two microservices: Publisher and Consumer.
- Publisher: It is responsible for handling the input video sent via HTTP Request. The video is processed and uploaded to a S3 bucket and a socket channel is used to provide the client feedback of the upload progress. Once the video is uploaded, a message containing the resource ID is then published to a RabbitMQ Broker hosted using Amazon MQ service.

- Consumer: It subscribes to the RabbitMQ and consumes the message with the resource ID. Then the video is fed to the AWS Rekognition service that processes it and returns a JSON containing the timestamps of each shot.


<i>Note: The project is still in progress</i>