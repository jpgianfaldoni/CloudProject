import boto3
from botocore.config import Config
import sys
import os
import time
import requests
from bs4 import BeautifulSoup
from RequestFunctions import add_user, delete_user, add_group, delete_group


def delete_everything(instance_ohio, security_group, autoscaling, django_img, elb, security_group2):
    print("Deleting Everything")
    time.sleep(60)
    instance_ohio[0].terminate()
    instance_ohio[0].wait_until_terminated()
    security_group.delete()
    time.sleep(10)
    autoscaling.delete_auto_scaling_group(AutoScalingGroupName ='AutoScalingV1', ForceDelete = True)
    time.sleep(10)
    django_img.deregister()
    time.sleep(10)
    elb.delete_load_balancer(LoadBalancerArn= lb_arn)
    time.sleep(30)
    elb.delete_target_group(TargetGroupArn= tg_arn)
    time.sleep(30)
    autoscaling.delete_launch_configuration(LaunchConfigurationName ='LCV999')
    time.sleep(90)
    security_group2.delete()
    print("Everything Deleted")


print("Starting Script")
# Create Regions
ohio_region  = Config(region_name="us-east-2")
north_virginia_region  = Config(region_name="us-east-1")

print("Regions Created")


# Create Resources
ohio_ec2 = boto3.resource('ec2', config=ohio_region)
north_virginia_ec2 = boto3.resource('ec2', config=north_virginia_region)

print("Resources Created")

#MySQL Script
script_mysql = '''#!/bin/bash
sudo apt update
sudo apt install mysql-server -y
sudo mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'cloud';CREATE USER 'root'@'%' IDENTIFIED BY 'cloud';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';FLUSH PRIVILEGES;CREATE DATABASE tasks;"
sudo sed -i 's/bind-address/#banana/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i 's/mysqlx/#banana/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo ufw allow 3306/tcp
sudo systemctl restart mysql
'''


#Security Groups
security_group = ohio_ec2.create_security_group(
    Description='string',
    GroupName='SecurityGroup7',
    TagSpecifications=[
        {
            'ResourceType': 'security-group',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'mysql'
                },
            ]
        },
    ],
)

security_group2 = north_virginia_ec2.create_security_group(
    Description='string',
    GroupName='SecurityGroup7',
    TagSpecifications=[
        {
            'ResourceType': 'security-group',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'mysql'
                },
            ]
        },
    ],
)



security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=0,ToPort=10000)
security_group2.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=0,ToPort=10000)
print("Security Groups Created")


#Create Ohio Instance
instance_ohio = ohio_ec2.create_instances(
        ImageId="ami-00399ec92321828f5",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="jpgianfaldoni",
        SecurityGroupIds = [security_group.group_id],
        UserData = script_mysql
    )

#Wait until instance is running
print("Creating Ohio Instance")
instance_ohio[0].wait_until_running()
instance_ohio[0].reload()
public_ip_ohio = instance_ohio[0].public_ip_address
time.sleep(60)
print("Ohio Instance Created")


#Django Script
script_django_mysql = f"""#!/bin/bash
cd /home/ubuntu
sudo apt update
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential -y
git clone https://github.com/raulikeda/tasks.git
cd tasks
sudo sed -i 's/node1/{public_ip_ohio}/g' portfolio/settings.py
sudo sed -i 's/django.db.backends.postgresql/django.db.backends.mysql/g' portfolio/settings.py
sudo sed -i 's/5432/3306/g' portfolio/settings.py
sudo sed -i "s/'USER': 'cloud'/'USER': 'root'/g" portfolio/settings.py
echo "mysqlclient" >> requirements.txt
./install.sh
sudo reboot 
"""

#Create North Virginia Instance
north_virginia = north_virginia_ec2.create_instances(
        ImageId="ami-09e67e426f25ce0d7",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="jpgianfaldoni",
        SecurityGroupIds = [security_group2.group_id],
        UserData = script_django_mysql
    )

print("Creating NV Instance")

#Wait until instance is running
north_virginia[0].wait_until_running()
north_virginia[0].reload()
nv_ip = north_virginia[0].public_ip_address
nv_response = "Fail"
client_nv = requests.session()
try_counter = 0

while nv_response == "Fail":
    time.sleep(1)
    try:
        nv_response = client_nv.get(f"http://{nv_ip}:8080/tasks/")
    except:
        nv_response = "Fail"
    if try_counter > 300:
        print("FAIL: Could not create NV Instance - terminating script")
        exit()
    try_counter += 1

print("NV Instance Created")


#Create Django Image
django_img = north_virginia[0].create_image(Name='django_img3')
print("Creating IMG")

#Wait Image to finish and terminare instance
while django_img.state != 'available':
    django_img.reload()
north_virginia[0].terminate()
print("IMG Created")

#Create Autoscaling and Elastic Load Balancer
autoscaling  = boto3.client('autoscaling', config=north_virginia_region)
elb = boto3.client('elbv2', config=north_virginia_region)

print("AutoScaling and ELB Created")

#Create Launch Configuration
create_launch_response = autoscaling.create_launch_configuration(
    LaunchConfigurationName='LCV999',
    ImageId= django_img.id,
    KeyName='jpgianfaldoni',
    SecurityGroups=[
        security_group2.id,
    ],
    BlockDeviceMappings=[
                        {
                            'DeviceName': '/dev/sda1',
                            'Ebs': {
                                'DeleteOnTermination': True,
                                'VolumeSize': 8,
                                'VolumeType': 'gp2'
                            },
                        },
                ],
    InstanceType='t2.micro',
)

print("LC Created")

#Create Autoscaling Group
create_autoscaling_response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='AutoScalingV1',
    LaunchConfigurationName='LCV999',
    MinSize=1,
    MaxSize=3,
    DesiredCapacity=3,
    DefaultCooldown=60,
    AvailabilityZones=[
        'us-east-1a',
        'us-east-1b',
        'us-east-1c',
        'us-east-1d',
        'us-east-1e',
        'us-east-1f',
    ]
)
print("ACG Created")
#Create Target Group
create_target_response = elb.create_target_group(
    Name='Tgroup5',
    Protocol='HTTP',
    Port=8080,
    VpcId='vpc-ebd11591',
    HealthCheckPath = '/tasks/',
    HealthCheckProtocol='HTTP',
    HealthCheckEnabled=True,
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=15,
    HealthyThresholdCount=5,
    UnhealthyThresholdCount=5,
    TargetType='instance',
    IpAddressType='ipv4'
)

print("TG Created")


#Create Target ARN
tg_arn = create_target_response['TargetGroups'][0]['TargetGroupArn']

#Create Load Balancer
create_lb_response = elb.create_load_balancer(
    Name='Elb3',
    Subnets=[
        'subnet-54296d1e',
        'subnet-7ebe0d50',
        'subnet-13fa4b4f',
        'subnet-e0f44387',
    ],

    SecurityGroups=[
        security_group2.id,
    ],
    Type='application',
    IpAddressType='ipv4',
)

#Create Load Balancer ARN
lb_arn = create_lb_response['LoadBalancers'][0]['LoadBalancerArn']

#Attach Load Balancer to Targer Groups
ab_response = autoscaling.attach_load_balancer_target_groups(
    AutoScalingGroupName='AutoScalingV1',
    TargetGroupARNs=[
        tg_arn,
    ]
)

#Create Listener
listener_response = elb.create_listener(
    LoadBalancerArn= lb_arn,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': tg_arn,
        },
    ],
    Port = 80,
    Protocol = 'HTTP',
)

#Load Balancer URLs
lb_url = create_lb_response['LoadBalancers'][0]['DNSName']


f = open("URLS.txt", "w")
f.write(lb_url)
f.close()



print("To delete everything, type y")
delete_input = input()
if delete_input == 'y':
    delete_everything(instance_ohio, security_group, autoscaling, django_img, elb, security_group2)
else:
    exit()





