# lambda-logs-athena-example

This serverless application is an example of using existing SAR apps ([json-logs-to-kinesis-firehose](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~json-logs-to-kinesis-firehose) and [kinesis-data-firehose-to-s3](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~kinesis-data-firehose-to-s3)) to aggregate JSON-formatted logs from multiple Lambda functions into one S3 bucket for Athena querying.

## App Architecture

![App Architecture](https://github.com/jlhood/lambda-logs-athena-example/raw/master/images/app-architecture.png)

1. The app contains two functions, MyFunction1 and MyFunction2. On invoke, these functions will log 10 random stock ticker JSON strings that look like this (note, values are random and NOT accurate): `{"ticker_symbol": "AMZN", "sector": "TECH", "change": 3.02, "price": 93.54}`
1. The [kinesis-data-firehose-to-s3](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~kinesis-data-firehose-to-s3)) app is pulled in via nested app. This creates a Kinesis Firehose Delivery Stream that writes to an S3 bucket (also created by the app).
1. For each function, an instance of the [json-logs-to-kinesis-firehose](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~json-logs-to-kinesis-firehose) app is pulled in as a nested app and connected to the Delivery Stream created by the kinesis-data-firehose-to-s3 app.

## Installation Instructions

1. [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and login
1. Go to the app's page on the [Serverless Application Repository](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:277187709615:applications~lambda-logs-athena-example) and click "Deploy"
1. Provide a stack name and click "Deploy"

## Testing the App

Once the app is deployed, you can test it by following these steps:

1. Find the deployed root stack in the [CloudFormation console](https://console.aws.amazon.com/cloudformation/home#/stacks) and click on it. Note, the root stack will be named `serverlessrepo-<stack name>`, where `<stack name>` is whatever you named your stack when you deployed it from SAR.
1. Click the "Resources" tab. Click the link for the "MyFunction1" and "MyFunction2" Lambda functions. This will open the AWS Lambda console to those two functions in different tabs.
1. In each Lambda function console tab
    1. Configure a test event (drop-down next to the "Test" button). You can name it anything and the data in it doesn't matter as long as it's a valid JSON object. Save the test event.
    1. Click the "Test" button a few times to make the Lambda functions generate some logs. The console will show you the log output, which should have JSON stock ticker entries.
1. Go back to the CloudFormation console with the root stack resources and look for the "LogPipeline" nested stack.
1. Click on the link for that resource to open the CloudFormation console for the nested stack.
1. Click the "Resources" tab and find the S3 bucket created by that nested app. This is where the JSON logs from each Lambda function will be stored.
1. Click on the bucket resource link to go to that bucket in the S3 Console.
1. You should see a "logs" folder in that bucket. If you don't you may need to refresh for a bit. This example app configures the kinesis-data-firehose-to-s3 app to batch the logs for up to 1 minute before writing them to an S3 file.
1. Once you see the logs folder, you should be able to click through folders until you find files. You can download these files and verify they contain only the JSON logs from the Lambda function.

### Querying log data with Athena

You can use [Amazon Athena](https://aws.amazon.com/athena/) to query the aggregate log data stored by the app in the S3 bucket. Here are steps you can follow to set that up.

First, note the name of the S3 bucket from the console steps above. Then go to the Amazon Athena console. Note, the following queries assume you're using the sampledb table Athena sets up for you.

In the Athena query editor, run the following DDL query to create a new table in that sampledb matching the schema of the JSON data in the logs:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS sampledb.logs_test (
  `ticker_symbol` string,
  `sector` string,
  `change` decimal(10,2),
  `price` decimal(10,2)
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
) LOCATION 's3://<your-bucket-name>/logs/'
TBLPROPERTIES ('has_encrypted_data'='false');
```

Make sure you replace `<your-bucket-name>` with the name of your S3 bucket. Once that table has been created, you can run SQL queries against it and view the results. Here are some example queries:

```sql
SELECT *
FROM sampledb.logs_test
LIMIT 10
;
```

```sql
SELECT sector,count(0)
FROM sampledb.logs_test
GROUP BY sector
ORDER BY count(0) DESC
LIMIT 10
;
```

## License Summary

This code is made available under the MIT license. See the LICENSE file.