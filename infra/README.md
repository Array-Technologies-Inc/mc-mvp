# Start infrastructure
Using podman
```bash
podman-compose -f ./base.yml up -d
```
Using docker
```bash
docker-compose -f ./base.yml up -d
```

Stop services
```bash
 podman-compose -f ./base.yml down  
```

# Services

## Victoria
### VictoriaMetrics
[WebUI](http://localhost:8428)

### VictoriaLogs
[WebUI](http://localhost:9428)

### Vmagent
[WebUI](http://localhost:8429)

Check targets state at: [Targets](http://localhost:8440/targets)
### Vmalerts
[Alerts](http://localhost:8880/vmalert/alerts?search=)

## Grafana
[Dashboards](http://localhost:3000/dashboards)
User: admin
Password: admin

## PostgreSQL
* PORT: 5432
* User: dbuser
* Password: dbpassword
* DB name: mcdb

## NATS

### Test it

Run a NATS client:
```bash
podman run --network infra_mc-bridge --rm -it natsio/nats-box
or
docker run --network infra_mc-bridge --rm -it natsio/nats-box
```

Send messages:
```bash
nats sub -s nats://nats:4222 topic &
nats pub -s "nats://nats:4222" topic [MESSAGE]
```