# Personal Note Manager MCP on AWS Lambda

MCP server (FastMCP) running on AWS Lambda via mangum, exposed through API Gateway (REST, `{proxy+}`) with an API key. Session state is stored in DynamoDB with TTL.

## Architecture

- **API Gateway** (REST, regional) → `/{proxy+}` → **Lambda** (Python 3.13, `lambda_handler.handler`)
- **DynamoDB** table for session state (`collection`/`key`, TTL attribute `ttl`)
- **Secrets Manager** holds the request-state signing key shared by Lambda instances
- **Usage plan + API key** (`x-api-key` header) for access control
- Everything is defined in `template.yaml` (AWS SAM / CloudFormation)

## Prerequisites

- AWS CLI with valid credentials (`aws sts get-caller-identity`)
- AWS SAM CLI and Docker (Docker builds the Lambda package)

## Deploy

```powershell
sam build --use-container
sam deploy --stack-name mcp-notes --region eu-south-1 --capabilities CAPABILITY_IAM --resolve-s3 --parameter-overrides StageName=prod
```

Redeploy after code changes by running the same two commands.

Get the MCP URL and the API key:

```powershell
aws cloudformation describe-stacks --stack-name mcp-notes --region eu-south-1 --query "Stacks[0].Outputs" --output table
aws apigateway get-api-key --api-key <ApiKeyId> --include-value --region eu-south-1 --query value --output text
```

## Call the server

```bash
curl -X POST "<MCP URL>" \
  -H "x-api-key: <API KEY>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Retrieve the API key later with:

```bash
aws apigateway get-api-key --api-key <API_KEY_ID> --include-value --query value --output text
```

## Local run

```bash
pip install -r requirements.txt
set DYNAMODB_TABLE_NAME=mcp-sessions   # table must exist and AWS credentials must be set
python main.py
```

## Delete

```bash
aws cloudformation delete-stack --stack-name mcp-notes --region eu-south-1
```

The artifacts bucket (`mcp-notes-artifacts-<account>-<region>`) is not managed by the stack and must be emptied and removed manually.

