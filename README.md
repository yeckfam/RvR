# RvR
RvR throughput measurement

1. The scripts measure throughput at different attenuations.
2. Currently 2 attenuators are supported: JFW and adaura.
3. Results are generated in csv and json format.

iperf_test.py needs to be run using sudo.

Sample usage:
sudo python iperf_test.py -c 192.168.1.161 -a 0 63 2 --logfile test-run