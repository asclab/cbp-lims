# cbp-lims
LIMS system for SPCG

Running this version:

1. Install Vagrant
2. Copy app.config.default -> app.config and change the values
3. ```vagrant up --no-parallel```


This creates a Vagrant VM running Postgres and Python Flask Docker images.

If you want to view the status of the current app from the Postgres or Flask Docker instance, you need to SSH to the host VM first:
find the VM id here: ```vagrant global-status```, then you can ```vagrant ssh {vmid}}```.

From the VM, you can see the docker instances running with: ```docker ps```. If you want to attach to them and run arbitrary commands, 
run this: ```docker exec -it {instance_id} /bin/bash```.

If you want to automatically sync your changes to the VM, you should run: ```vagrant rsync-auto```
