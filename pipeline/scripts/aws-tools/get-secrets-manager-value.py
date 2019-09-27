import argparse

import boto3


def main(secret_id: str):
    secret_value = _get_secret_value(secret_id)

    print(secret_value, end="")


def _parse_arguments():
    parser = argparse.ArgumentParser(description="Retrieve a secret value from AWS Secrets Manager")
    parser.add_argument("secret_arn", help="The ARN of the secret to check")

    return parser.parse_args().secret_arn


def _get_secret_value(secret_id):
    client = boto3.client("secretsmanager")
    secret_value_response = client.get_secret_value(SecretId=secret_id)
    secret_value = secret_value_response["SecretString"]
    return secret_value


if __name__ == "__main__":
    secret_arn = _parse_arguments()

    main(secret_arn)
