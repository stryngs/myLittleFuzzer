



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

### In the chute now
```
git clone https://github.com/secdev/scapy.git
git clone https://github.com/stryngs/easy-thread.git
python3 scapy/setup.py sdist
python3 -m pip install dist/*.tar.gz
python3 -m pip install easy-thread/easy-thread-*.tar.gz
```

### The gist
 ```
 usage: pwnie.py [-h] (--file FILE | --gen | --run) [-i I] [-p P] [-q Q] [-s S] [-t T] [-v] [-w W]

 myLittleFuzzer

 optional arguments:
   -h, --help   show this help message and exit
   --file FILE  Read from a file instead of generating fuzz, then send
   --gen        Generate a stream of fuzz for usage later
   --run        Generate and send fuzz
   -i I         Interface
   -p P         Target Port
   -q Q         Quantity of packets fuzzed
   -s S         CIDR source range
   -t T         Target IP
   -v           Verbosity
   -w W         Wait between injects
  ```

### How exactly
The function fuzz() is able to change any default value that is not to be calculated (like checksums) by an object whose value is random and whose type is adapted to the field. This enables quickly building fuzzing templates and sending them in a loop.

Refer to the documents for a deeper explanation, https://scapy.readthedocs.io/en/latest/usage.html#fuzzing.

### SQL table schema
brd
```
The bridle table is one to rule them all
```
hex
```
Leverages binascii and hexstr to store fuzzed packets in a trackable manner
What is stored in hex is exactly what was transmitted, sans a crtl+c for an interrupt
```
png
```
The stdout for ping -D against the target ip during the run
Useful for timing guesses based upon the wait between packets
```
sum
```
Useful for an overview without needing to be exact
```

### Modes of operation
Read from a file instead of generating fuzz, then send.
```
Required args for --file:
 -i
 -w

./pwnie.py --file -i wlan0 -w 1
```
Generate a stream of fuzz for usage later.
```
Requred args for --gen:
 -q
 -s
 -t

 ./pwnie.py --gen -q 2000 -s 192.168.100.0/23 -t 192.168.100.3
```
Generate and send fuzz.
```
Requred args for --run:
 -i
 -q
 -s
 -t
 -w

 ./pwnie.py --run -i wlan0 -q 2000 -s 192.128.2.1/32 -t 192.128.2.2 -w .5
 ```


### Shelter and a diet
Hungry pwnies are angry pwnies.  Avoid this by making sure to tune their diet from time to time.  Too much fuzz and not enough lag makes for a boring ride.  The more trails you ride the higher level your corral grows.  Pull the reins from time to time and make sure you're riding with the latest gear.  A smart rider does this from time to time before running:
```
cp saddle.sqlite3 saddle.sqlite3.copy
git pull
./pwnie.py ........
```

### Hash it out
**saddle.sqlite3** is where the young herd is bred.  As your herd grows, so does the chance of catching a pwnie in the wild.  Let your herd roam as free as possible.

### Highly recommended
Use pypy3 from https://www.pypy.org/ for a 0 code change benchmark increase!
The directions above for python3 are the exact same for pypy3.
