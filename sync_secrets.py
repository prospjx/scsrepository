import boto3
import json
import base64
import subprocess
import sys

def sync_secret():
    session = boto3.session.Session(
        region_name="us-east-1"
    )
    client = session.client(service_name='secretsmanager')
    
    try:
        response = client.get_secret_value(SecretId='scs/production/database')
        secret_data = json.loads(response['SecretString'])
        print(f"Retrieved secret keys: {list(secret_data.keys())}")
        
        # Sync to Kubernetes secrets
        pw = secret_data.get('POSTGRES_PASSWORD', 'postgres')
        for sec in ['postgres-secret', 'courseapi-secret', 'studentapi-secret', 'schedulerapi-secret']:
            cmd = [
                'kubectl', 'patch', 'secret', sec, '-n', 'default',
                '--type', 'merge',
                '-p', json.dumps({"stringData": {"POSTGRES_PASSWORD": pw}})
            ]
            subprocess.run(cmd, check=True)
            print(f"Synced secret {sec} with AWS Secrets Manager")
    except Exception as e:
        print("Error syncing secret:", e)
        sys.exit(1)

if __name__ == '__main__':
    sync_secret()
