# Nifi automation example

this is a very simple example with Apache Nifi.

all this service does, is clones root directory from `./sftp-in` to `nifi-out` after some time.

the difference is that the entire thing starts with a single script. You don't have to do a lot of management.

if you really dislike using UI for anything, but you have to use Apache Nifi, you can use those scripts to help you start out with it.

## Prerequisites

you need to install python and docker for this setup to work.

## How to start

go to the root directory, and run `start.ps1`

This will:
1. create python virtual environment (if not exists) and activate it
2. download all libraries for python venv
3. create key for sftp server ssh connection. It will open new window
4. create with docker compose sftp server and nifi (if docker works, if not stop script)
5. start python script, which creates new process group and parameter context, and starts the process group

at this point, everything should work:
- file cloning from `./sftp-in` to `./nifi-out` will happen each 5 seconds 
- `http://localhost:8082/nifi` should point you to nifi ui. You'll see there a process group that does all the work

this is just an example how you might setup this. You can replace that with your own template from nifi.

extra:
- look in `localhost:8082/nifi` to see your workflow.

### How to mount smb from windows share from linux

I had to put files to windows share from linux, and this is how i did it:
- install samba and all tools for it (smbconfig and cift-tools)
- create samba config at `/etc/samba/smb.conf`. search for default one and add those fields to it:
```
[global]

client use spnego = no
client NTLMv2 auth = no

# workgroup = NT-Domain-Name or Workgroup-Name, eg: MIDEARTH
   workgroup = HOMEST
   client max protocol = NT1
```
- edit `/etc/fstab` file, add your mounted folder to it:
``
- `sudo mount -a`

