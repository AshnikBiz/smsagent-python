#!/bin/bash
ansible -i workdir/log/config/sms_log.txt -m setup --tree workdir/log/out sms_log