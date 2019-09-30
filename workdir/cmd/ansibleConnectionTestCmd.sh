#!/bin/bash
ansible -i workdir/test/config/sms_connection_test.txt -m ping --tree workdir/test/out sms_connection_test