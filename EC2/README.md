## To enable EC2 start and stop

* Add a tag 'auto_start' and value as 'yes' to enable auto start of a instance
* Add a tag 'auto_stop' and value as 'yes' to enable auto stop of a instance


## To enable mail sending using SES

* To enable SES. Verify email address which will be used to send mail (fromaddr)
* Attach policy SES mail sending policy to role used in lambda script
