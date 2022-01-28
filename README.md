
# myLittleFuzzer
Grab the pwnie by the horns and get to work fuzzing

### Grab the reins
```
git clone https://github.com/secdev/scapy.git
git clone https://github.com/stryngs/easy-thread.git
python3 scapy/setup.py sdist
python3 -m pip install dist/*.tar.gz
python3 -m pip install easy-thread/easy-thread-*.tar.gz
```

### Buckle up
```
git clone https://github.com/secdev/scapy.git
git clone https://github.com/stryngs/easy-thread.git
python3 scapy/setup.py sdist
python3 -m pip install dist/*.tar.gz
python3 -m pip install easy-thread/easy-thread-*.tar.gz
```

### The gist
./pwnie.py {target ip} {source ip/cidr range} {quantity of fuzzed packets} {interval} *{verbosity}*
```
./pwnie.py 192.168.100.1 192.168.100.0/24 2000 3
```
Verbosity is optional with a 1 on the end
```
./pwnie.py 192.168.100.1 192.168.100.0/24 2000 3 1
```

### What did you do
```
./pwnie.py 192.168.103.1 192.168.202.1/20 21 .3 1
```
In other words chat at layer 3 with something like a router.  During this chat leverage the fuzz() from scapy and be random.
This syntax sent 21 fuzzed packets to 192.168.103.1 posing as a packet in the 192.168.202.1/20 range at an interval of .3 seconds per packet.
The 1 on the end specified verbosity and so for every packet sent a . will be printed to stdout.
Verbosity is useful but can have a negative effect on the performance of the sending node relative to the {quantity of fuzzed packets}.

### How it fuzzed
```
fuzz(IP(dst = {target IP}, src = RandIP({source ip/cidr range})))
```
The function fuzz() is able to change any default value that is not to be calculated (like checksums) by an object whose value is random and whose type is adapted to the field. This enables quickly building fuzzing templates and sending them in a loop.

Refer to the documents for a deeper explanation, https://scapy.readthedocs.io/en/latest/usage.html#fuzzing.

### Where was it stored
.\\hex.log
```
Leverages binascii and hexstr to store fuzzed packets in a trackable manner.
What is printed in hex.log is exactly what was transmitted, sans a crtl+c for an interrupt.
{interval} and the general speed of the device used to run pwnie.py matter for high quantity and low interrupt speed runs.
```
ping.log
```
The stdout for ping -D against {target ip}
Useful for timing guesses based upon the {interval}
```
summary.log
```
A stdout representation of summary()
Useful for an overview without needing to be exact
```

### Highly recommended
Use pypy3 from https://www.pypy.org/ for a 0 code change benchmark increase!
The directions above for python3 are the exact same for pypy3.
