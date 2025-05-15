## Install needed tools

Protobuf to generate messages (Optional)
```bash
winget install protobuf
```

UV to manage Python environment  (Optional)
```bash
winget install uv
```

### Generate Python code from .proto files
Run the following command from the project root
```bash
protoc --proto_path=.\devices\common\ --python_out=.\devices\common\ --pyi_out=.\devices\common\ .\devices\common\messages.proto
```

### Run devices simulation
Deployment is control with environment variables files. You should create one file per gateway.
```
NODES_COUNT: Number of trackers to create
GW_ID ID: ID of the gateway
```
There are two example files on the devices folder.

#### Run a gateway deployment

IMPORTANT: Infrastructure deployment must be running or the gateway will stop working since it can not reach the MC.

For gateway 1
```
podman-compose.exe --env-file .\gateway\gw1.env -p gw-1 up --no-recreate  --quiet-pull -d
```

For gateway 2
```
podman-compose.exe --env-file .\gateway\gw2.env -p gw-2 up --no-recreate  --quiet-pull -d
```

More gateways can be created if needed.

'
