# Manual Test

Edge cases on advanced features would benefit from a manual testing process.

This directory holds some utils and scripts that are convenient for such use cases.

## Docker-compose.yaml
This docker-compose.yaml spins up a fresh Apache SkyWalking instance along with UI (localhost:8080) and SW_CTL CLI for you to verify.

Uncomment kafka services to use the kafka protocol.

## Demo services
FastAPI-based services consumer (localhost:9090) and provider (localhost:9091) can be used as basis for manual testing. 

