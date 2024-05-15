
# AWS API Gateway HTTP API to AWS Lambda in VPC to DynamoDB ans S3 CDK Python Sample!


## Overview

Coding Exercise
You are developing the service layer of an application like Instagram. You are working 
on a module which is responsible for supporting image upload and storage in the 
Cloud. Along with the image, its metadata must be persisted in a NoSQL storage. 
Multiple users are going to use this service at the same time. For this reason, the 
service should be scalable. 
The team currently uses API Gateway, Lambda Functions, S3 and DynamoDB services. 
Language: Python3.7+
Tasks:
1. Create APIs for:
1. Uploading image with metadata
2. List all images, support at least two filters to search
3. View/download image
4. Delete an image

## Setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Deploy
At this point you can deploy the stack. 

Using the default profile

```
$ cdk deploy
```

With specific profile

```
```

## After Deploy
https://github.com/Deependra-dot/fake_insta/blob/master/finsta.postman_collection.json

import postman collection from above link and test the various scenarios of adding the images and viewing the image and deleting the image.

## Cleanup 
Run below script to delete AWS resources created by this sample stack.
```
cdk destroy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
