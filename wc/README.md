SSH tunnel tested
```
ssh -N -L 50051:fz-0003.frequenz.io:50051 fz-0003.frequenz.io
ssh -N -L 50051:localhost:50051 fz-0003.frequenz.io
ssh -N -L 50051:0.0.0.0:50051 fz-0003.frequenz.io
```

SSH diagnostics
```
netstat -tuln | grep 50051
telnet localhost 50051
nc -vz localhost 50051
```
