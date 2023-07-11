# Hostname Check
check the availability of a list of hostnames and report the results in a table, continuosly run inside of a container
to isolate docker container issues due to 20.04 upgrade
# experiments
## simple
the simple compose did not reliably reproducet the error we saw in the production environment
it only failed a few times at the beginning of the run, then it was fine ( in prod the error was persistent )
adding the random restart to the services did not provoke the error as hypothesised.
( the host name can not be resolved for a few seconds after the container is started,
but in prod the error is affecting not restarting containers )
## v2
attempting to recreate a more complex network structure and more complex container visibility
attempt 2 produced the random behaviour on the linux test machine, but not on a windows test machine
see log files in
