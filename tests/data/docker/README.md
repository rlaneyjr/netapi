# Docker lab scenario

There are emultiple ways to setup a lab scenario for CI purposes, but none of them ar streamlined. So I am following 2 approaches here from a couple of excellent projects:

- [vrnetlab](https://github.com/plajjan/vrnetlab): Its purpose is mainly to build docker images of network devices images. And can create device connections.
> I believe the biggest limitation is to build complex topologies out of it. But I haven't really tested it, there is this topology-machine that I might revisit later.
- [docker-topo](https://github.com/networkop/docker-topo): Its main purpose is to create topologies out of network containers. It supports a lot of options for connections and setting configurations files.
> The big limitation here is the use of pyroute2 -> which is Linux based and cannot run the topologies on the mac natively. Can be run though on the Ubuntu server without issues.

# Docker-topo

The docker-topo files are in its folder where the configuration can be stored as well.

# VRNetlab

There isn't a folder of topology files since most of it is run as terminal commands. So here is an example of how to run them:

```
docker run -d --name veosRing1 --privileged vr-veos:4.21.5F
docker run -d --name veosRing2 --privileged vr-veos:4.21.5F
docker run -d --name veosRing3 --privileged vr-veos:4.21.5F
```
Give it around 10 minutes to fire up.

The default credentials of vrnetlab/VR-netlab9.

## Inspecting the VR containers
You can verify their IP address:
```
docker inspect --format '{{.NetworkSettings.IPAddress}}' veosRing1
```
So you can ssh to it:
```
ssh -l vrnetlab $(docker inspect --format '{{.NetworkSettings.IPAddress}}' veosRing1)
```
You can open a console session (port 5000 by default):
```
telnet $(docker inspect --format '{{.NetworkSettings.IPAddress}}' veosRing1) 5000
```

Next create the links using `vr-xcon` (For this I just did `docker pull vrnetlab/vr-xcon`)

```
docker run -d --privileged --name vr-xcon --link vr1 --link vr2 --link vr3 vrnetlab/vr-xcon --p2p veosRing1/1--veosRing2/1 veosRing1/2--veosRing3/1 veosRing2/2--veosRing3/2
```
