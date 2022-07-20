from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
env = os.environ
db_host, db_user, db_password, db_port = env.get('DB_HOST'), env.get('DB_USER'), env.get('DB_PASSWORD'), env.get('DB_PORT')
lambda_function_name = 'load_listens'
subprocess.run([
    'aws',
    'lambda',
    'update-function-configuration',
    '--function-name',
    lambda_function_name,
    '--environment',
    f'Variables={{RDS_HOST={db_host},NAME={db_user},PASSWORD={db_password},PORT={db_port}}}'
])