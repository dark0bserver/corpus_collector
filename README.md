# Corpus Collector
`Text for everyone`
## Purpose
This project grew out of a need to quickly gather sample pages from common websites and examine their lexical content. This is designed to work in AWS free tier but depending on corpus size, your mileage might vary.

This repository is several packagings of the same tool though the primary usecase is AWS SAM for raw scalability.

## Installation

**Configure AWS credentials:**
This can be done with `aws configure`.
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

**Clone this repository:**
```sh
$ git clone git@github.com:dark0bserver/corpus_collector.git
```

#### Commandline Tool
Corpus Collector has been prepared as an installable python module. From the cloned directory run the below command:
```sh
$ pip install .
```
Corpus Collector is now available as a command and can be invoked as below.
```sh
$ corpus_collector cnn.com --limit 5
```

#### AWS SAM Deployment
_This assumes that the AWS SAM command-line tool `aws-sam-cli` is already present in the local environment and that appropriate permissions have been granted to the deploying role._
https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-template-publishing-applications.html

##### Create code deployment bucket
Prior to deployment, create an S3 bucket to hold the deployed code. Then replace `$DEPLOYMENT_CODE_BUCKET` in the below example with the name of that bucket.

##### Build and deploy
The following steps build, package, and deploy the serverless application to a stack named `corpus-collector`. Feel free to update to taste.
```sh
$ cd corpus_collector
$ sam build
$ sam package --s3-bucket $DEPLOYMENT_CODE_BUCKET --output-template-file deploy-template.yml
$ sam deploy --template-file deploy-template.yml --stack-name corpus-collector --capabilities CAPABILITY_IAM
```

##### Usage
To invoke the collection harness for a given domain, call the AWS lambda function with a json dictionary containing a `domain` key carrying the domain of interest.
```sh
$ aws lambda invoke --function-name queue_domain --payload '{"domain": "cnn.com", "limit": 5}' outfile.txt
```
Results will be stored to the DynamoDB table `page_text` and can be viewed and accessed through the console or programmatically. For example:
```sh
$ aws dynamodb scan --table-name page_text
```