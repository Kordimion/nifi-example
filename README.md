# Nifi hello world

this is a very simple example with Apache Nifi.

all you need to do, is run docker compose to run the entire stack, and that will start the service.

all this service does, is clones root directory from `./sftp-in` to `nifi-out` after some time.


## How to start

1. go to the root directory of this repository
2. run in shell `docker compose up`
3. add some files in your newly created `./sftp-in` directory
4. wait for some time, and see copied files in `nifi-out` directory. You can delete the file, and it will be copied after some time.

extra:
- look in `localhost:8082/nifi` to see your workflow.

