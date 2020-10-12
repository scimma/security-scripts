"""
Data Acquisition and Tests/Information for Scimma AWS instance

This module has code to collect data from all allowed
AWS regions and buid a relational database

"""
from security_scripts.information.lib import measurements
from security_scripts.information.lib import shlog


class Acquire(measurements.Dataset):
    """
    Load information from the instance  api into a relational table.

    Optional method to clean the data of non-SCiMMA concerns.
    """
    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "ec2"
        self.make_data()
        self.clean_data()
        
    def make_data(self):
        """
        Make a table called ec2 based on tagging data.
        This collection of data is based on the resourcetaggingapi

        If the tags table exists, then we take it data collection
        would result in duplicate rows. 
        """
        if self.does_table_exist():
            shlog.normal("ec2 data already collected")
            return

        shlog.normal("beginning to make {} data".format(self.name)) 
        # Make a flattened table for the tag data.
        # one tag, value pair in each record.
        sql = """CREATE TABLE ec2 (
                 instance TEXT, vpc TEXT, subnet TEXT, publicdnsname TEXT,
                 privatednsame TEXT, privateipaddress TEXT, keyname TEXT,
                record JSON)"""
        shlog.verbose(sql)
        self.q.q(sql)
        # Get the tags for each region.
        # accomidate the boto3 API can retul data in pages
        for page, _ in self._pages_all_regions('ec2', 'describe_instances'):
            reservations = page["Reservations"]
            for r in reservations:
                for  i  in r["Instances"]:
                    record = self._json_clean_dumps(i)
                    instance = i.get("InstanceId","");
                    vpc = i.get("VpcId","");
                    subnet = i.get("SubnetId","");
                    publicdnsname =i.get("PublicDnsName","");
                    privatednsame =i.get('PrivateDnsName',"");
                    privateipaddress = i.get("PrivateIpAddress","");
                    keyname= i.get("KeyName","")
                    sql = '''INSERT INTO ec2 VALUES (?, ?, ?, ?, ?, ?, ?,?)'''
                    list = (instance, vpc, subnet, publicdnsname,  privatednsame, privateipaddress,  keyname, record)
                    self.q.executemany(sql,[list])
                    # populate the all_json table 
                    self._insert_all_json("ec2", instance, record) 


                    
    
class Report(measurements.Measurement):
    def __init__(self, args, name, q):
         measurements.Measurement.__init__(self, args, name, q)


    def inf_instances(self):
        "relational report for instances"
        sql = """SELECT
                    instance, vpc, subnet, publicdnsname,
                    privatednsame, privateipaddress, keyname
                 FROM ec2"""
        return sql
              
    def json_instance_report(self):
        "make json file"
        return """
                SELECT record FROM ec2
               """
