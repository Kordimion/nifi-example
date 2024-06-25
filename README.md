# Nifi automation example

This is a very simple example with Apache Nifi.

All this service does, is clones root directory from `./sftp-in` to `nifi-out` after some time.

The difference is that the entire thing starts with a single script. You don't have to do a lot of management.

If you really dislike using UI for anything, but you have to use Apache Nifi, you can use those scripts to help you start out with it.

## Prerequisites

You need to install python and docker for this setup to work.

## How to start

Go to the root directory, and run `start.ps1`

This will:
1. Create python virtual environment (if not exists) and activate it
2. Download all libraries for python venv
3. Create key for sftp server ssh connection. It will open new window
4. Create with docker compose sftp server and nifi (if docker works, if not stop script)
5. Start python script, which creates new process group and parameter context, and starts the process group

At this point, everything should work:
- file cloning from `./sftp-in` to `./nifi-out` will happen each 5 seconds 
- `http://localhost:8082/nifi` should point you to nifi ui. You'll see there a process group that does all the work

This is just an example how you might setup this. You can replace that with your own template from nifi.

Extra:
- Look in `localhost:8082/nifi` to see your workflow.

### How to mount smb from windows share from linux

I had to put files to windows share from linux, and this is how i did it:
- Install samba and all tools for it (smbconfig and cift-tools) [see arch wiki](https://wiki.archlinux.org/title/Samba)
- Create samba config at `/etc/samba/smb.conf`. search for [default samba config](https://git.samba.org/samba.git/?p=samba.git;a=blob_plain;f=examples/smb.conf.default;hb=HEAD), paste it in and add those fields to it:
    ```
    [global]

    client use spnego = no
    client NTLMv2 auth = no

    # workgroup = NT-Domain-Name or Workgroup-Name, eg: MIDEARTH
       workgroup = HOMEST
       client max protocol = NT1
    ```
- Edit `/etc/fstab` file, add your mounted folder to it:
    ```
    //<samba-ip>/<samba-folder-path> <mounted-pos> cifs username=<user>,password=<password>,uid=<(echo $UID)>,file_mode=0777,dir_mode=0777 0 0
    ```
    - `sudo mount -a`

