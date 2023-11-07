# Deploy Your Flask App to Kubernetes Using EKS

## Prerequisites
* Docker Desktop - Installation instructions for all OSes can be found <a href="https://docs.docker.com/install/" target="_blank">here</a>.
* Git: <a href="https://git-scm.com/downloads" target="_blank">Download and install Git</a> for your system. 
* Code editor: You can <a href="https://code.visualstudio.com/download" target="_blank">download and install VS code</a> here.
* AWS Account
* Python version between 3.7 and 3.9. Check the current version using:
```bash
#  Mac/Linux/Windows 
python --version
```
You can download a specific release version from <a href="https://www.python.org/downloads/" target="_blank">here</a>.

* Python package manager - PIP 19.x or higher. PIP is already installed in Python 3 >=3.4 downloaded from python.org . However, you can upgrade to a specific version, say 20.2.3, using the command:
```bash
#  Mac/Linux/Windows Check the current version
pip --version
# Mac/Linux
pip install --upgrade pip==20.2.3
# Windows
python -m pip install --upgrade pip==20.2.3
```
* Terminal
   * Mac/Linux users can use the default terminal.
   * Windows users can use either the GitBash terminal or WSL. 
* Command line utilities:
  * AWS CLI installed and configured using the `aws configure` command. Another important configuration is the region. Do not use the us-east-1 because the cluster creation may fails mostly in us-east-1. Let's change the default region to:
  ```bash
  aws configure set region us-east-2  
  ```
  Ensure to create all your resources in a single region. 
  * EKSCTL installed in your system. Follow the instructions [available here](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html#installing-eksctl) or <a href="https://eksctl.io/introduction/#installation" target="_blank">here</a> to download and install `eksctl` utility. 
  * The KUBECTL installed in your system. Installation instructions for kubectl can be found <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl/" target="_blank">here</a>. 

## Installation
### Install AWS CLI
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```
Reference: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### AWS Configure
```bash
aws configure
export AWS_CONFIG_FILE=~/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=~/.aws/credentials
```

### Install Eksctl
```bash
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl
```

### Install Kubectl
```bash
brew install kubectl
```

### Install packages
```bash
pip install -r requirements.txt
```

## Build Application
### Run locally
```bash
python main.py
```

Request method `POST`:
```bash
export TOKEN=`curl --data '{"email":"quyetcv1@fpt.com","password":"mypwd"}' --header "Content-Type: application/json" -X POST localhost:8080/auth  | jq -r '.token'`
```

Response: `echo $TOKEN`
```bash
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MDA1NDcwNDgsIm5iZiI6MTY5OTMzNzQ0OCwiZW1haWwiOiJxdXlldGN2MUBmcHQuY29tIn0.jF0tx5FgzM55v_xtvBuazSycW2Gt9zbbcqspe34JhOM
```

Request method `GET`:
```bash
curl --request GET 'http://localhost:8080/contents' -H "Authorization: Bearer ${TOKEN}" | jq .
```

Response:
![get_info](./images/jq1.png)

### Run Pytest
```bash
pytest test_main.py --disable-pytest-warnings
```

Result:
![pytest](./images/pytest.png)

### Build Docker Image
```bash
docker build -t simple-jwt-api .
```

### Run Docker Container
```bash
docker run --detach --publish 80:8080 --env-file=.env_file simple-jwt-api
```

### Test Docker Container
```bash
export TOKEN=`curl --data '{"email":"quyetcv1@fpt.com","password":"mypwd"}' --header "Content-Type: application/json" -X POST localhost:80/auth  | jq -r '.token'`
```
Result:
![docker_test1](./images/docker_test_1.png)

```bash
curl --request GET 'http://localhost:80/contents' -H "Authorization: Bearer ${TOKEN}" | jq .
```

Result"
![docker_test](./images/docker_test.png)

### Push Docker Image to Docker Hub
```bash
docker tag simple-jwt-api:latest 36vanquyet/simple-jwt-api:latest
docker push 36vanquyet/simple-jwt-api:latest
```

## Deploy Application to Kubernetes Cluster
### CloudFormation Design
![cloudformation_template_designer](./images/template1-designer.png)

### Create EKS Cluster
```bash
eksctl create cluster --name simple-jwt-api --nodes=2 --instance-types=t2.medium --region=us-east-1
```

![eksctl_create](./images/eksctl_create_cluster.png)

Get cluster information:
```bash
kubectl get nodes
```
![get_nodes](./images/kubectl_get.png)

### Get current AWS account
```bash
aws sts get-caller-identity --query Account --output text 
```
Result: `486387019881`

### Create IAM Role and attach policy
```bash
aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document file://trust.json --output text --query 'Role.Arn'
```

Result: `arn:aws:iam::486387019881:role/UdacityFlaskDeployCBKubectlRole`

```bash
aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file://iam-role-policy.json
```

### Set Environment Variables
```bash
aws ssm put-parameter --name JWT_SECRET --value "quyetcv1-secret" --type  SecureString --region us-east-1
```

### Create Kubernetes ConfigMap
```bash
kubectl get -n kube-system configmap/aws-auth -o yaml > /tmp/aws-auth-patch.yml
kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"
```

Result: `configmap/aws-auth patched`

### Get GitHub Access Token
In GitHub, go to Settings > Developer settings > Personal access tokens > Generate new token

### Create CloudFormation Stack
1. Modify `ci-cd-codepipeline.cfn.yaml` file
2. Review the resources
3. Create stack

![cloudformation_stack](./images/create_stack.png)

### Create CodePipeline
Details in `buildspec.yml` file

### Check CodePipeline Deployment
![codepipeline_build](./images/code_build.png)

### Test Endpoint
```bash
kubectl get services simple-jwt-api -o wide
```

![kubectl_service](./images/test_endpoint.png)

Request method `POST`:
```bash
export TOKEN=`curl -d '{"email":"quyet@fpt.com","password":"mypwd"}' -H "Content-Type: application/json" -X POST aefaa17ad9e1249d49e7d02b29af31e8-1793618444.us-east-1.elb.amazonaws.com/auth  | jq -r '.token'`
```

Request method `GET`:
```bash
curl --request GET 'aefaa17ad9e1249d49e7d02b29af31e8-1793618444.us-east-1.elb.amazonaws.com/contents' -H "Authorization: Bearer ${TOKEN}" | jq
```

Result:
![test_endpoint1](./images/test_endpoint_1.png)

### Delete CloudFormation Stack
```bash
aws cloudformation delete-stack --stack-name <stack-name>
```

### Delete EKS Cluster
```bash
eksctl delete cluster --name <eksname> --region=us-east-1
```

## CI/CD
### GitHub Actions
Build and push Docker image to Docker Hub
![github_action](./images/github_action.png)

![push_docker_hub](./images/docker_hub.png)
### CodePipeline
Check CodePipeline Deployment
![trigger_new_commit](./images/code_build.png)