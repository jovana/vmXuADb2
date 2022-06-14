# Lambda Container Image
This dummy container is used to preload Lambda function, created by Terraform.


## Install
Below commands, replace 526403589863 with the correct AWS client_id
```
docker build -t lambda-image-dummy .
aws ecr get-login-password --region eu-central-1|docker login --username AWS --password-stdin 526403589863.dkr.ecr.eu-central-1.amazonaws.com
aws ecr create-repository --repository-name lambda-image-dummy --region eu-central-1

docker tag lambda-image-dummy:latest 526403589863.dkr.ecr.eu-central-1.amazonaws.com/lambda-image-dummy:latest
docker push 526403589863.dkr.ecr.eu-central-1.amazonaws.com/lambda-image-dummy:latest

```


## Check
```
docker run -it --rm lambda-image-dummy
```