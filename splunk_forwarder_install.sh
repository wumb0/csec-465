#!/bin/bash
#http://lifeunix.blogspot.com/2013/10/install-and-configure-splunk-forwarder.html
rpm -Uvh http://download.splunk.com/products/splunk/releases/6.3.0/universalforwarder/linux/splunkforwarder-6.3.0-aa7d4b1ccb80-linux-2.6-x86_64.rpm
/opt/splunkforwarder/bin/splunk start --accept-license
/opt/splunkforwarder/bin/splunk edit user admin -password NEWPASS -auth
/opt/splunkforwarder/bin/splunk add forward-server splunk.phryanjr.com:5555 -auth USERNAME:PASSWORD
/opt/splunkforwarder/bin/splunk enable boot-start
chkconfig splunk on
/opt/splunkforwarder/bin/splunk list forward-server
