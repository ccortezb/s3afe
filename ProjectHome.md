## About ##
A command line Python script to upload a single file to a bucket on Amazon S3 (using the boto library).

## Command Line Options ##
```
Options:
  --version             show program s version number and exit
  -h, --help            show this help message and exit
  -k AWSKEY, --aws_access_key_id=AWSKEY
  -s AWSSECRET, --aws_secret_access_key=AWSSECRET
  -f FILENAME, --filename=FILENAME
  -b BUCKETNAME, --bucketname=BUCKETNAME
  -n KEYNAME, --keyname=KEYNAME
  -a ACL, --acl=ACL
```

## Example ##
The following command uploads the file ~/backups/latest.tgz to the S3 bucket called 'backupbucket' using the name '20090701.tgz'. The backup should be private.
```
python s3afe.py -f '~/backups/latest.tgz' -n '20090701.tgz' -b 'backupbucket' -a 'private' -k 'HONIKLQSJREDBCFTAGMP' -s 'och4od9cub4byms8iv7nun7fid1had3cyind5of2'
```

In case you set the environment variables AWS\_ACCESS\_KEY\_ID and AWS\_SECRET\_ACCESS\_KEY, s3afe takes those and the command is a bit shorter:
```
python s3afe.py -f '~/backups/latest.tgz' -n '20090701.tgz' -b 'backupbucket' -a 'private'
```

To prevent exposing your private data by mistake, the ACL 'private' is default. This shortens the command to:
```
python s3afe.py -f '~/backups/latest.tgz' -n '20090701.tgz' -b 'backupbucket'
```

## ACL-Options ##
  * private (default)
  * public-read
  * public-read-write
  * authenticated-read

## Requirements ##
  * Python
  * [boto](http://code.google.com/p/boto/) (try 'sudo easy\_install boto')