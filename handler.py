import boto3
import redis
import time

from decouple import config


client = boto3.client('elasticbeanstalk')

namespace = 'aws:autoscaling:asg'
max = 'MaxSize'
min = 'MinSize'
REDIS = redis.ConnectionPool(
            host=config('BOTHUB_REDIS'),
            port=config('BOTHUB_REDIS_PORT'),
            db=config('BOTHUB_REDIS_DB'))

def get_number():
    total_instances_available = redis.Redis(connection_pool=REDIS).get("SERVERS_INSTANCES_AVAILABLES")
    total_instances_available = len(total_instances_available.split())
    total_instances_alive = len(redis.Redis(connection_pool=REDIS).keys(pattern='SERVER-ALIVE-*'))
    if total_instances_available < 1:
        return total_instances_alive+1
    elif total_instances_available > 1:
        return ((total_instances_alive-total_instances_available)+1)
    else:
        return None


while True:
    number = get_number()
    if number:
        print("Modify instances numbers to %s" % number)
        options = []
        for name in [max, min]:
            options.append(
                {
                    'Namespace': namespace,
                    'OptionName': name,
                    'Value': str(number)
                }
            )

        response = client.update_environment(
            ApplicationName='bothub-app',
            EnvironmentId='e-krhx6ymg2x',
            OptionSettings=options
            )
        print(response)
    else:
        print("None modifications")

    time.sleep(6*60)
