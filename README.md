# Slurper API

Provides active network session data to voice clients(mostly ATC clients like TrackAudio), allowing them to determine if a user is connected to the FSD network.

## Endpoint

`GET /users/info/?cid=<CID>` or `GET /api/users/info/?cid=<CID>`.

## Response Format

Plain text CSV, one line per active session, 16 comma-separated fields:
```
{cid},{callsign},{connection_type},{frequency},{detail},{lat},{lon},0,0,0,0,0,0,0,0,
```
- `connection_type`: `"atc"` or `"pilot"`
- `frequency`: e.g. `"121.900"` (defaults `"199.998"` if empty); literal `"pilot"` for pilot connections
- `detail`: facility type or rating number
- Fields 7-14: padding zeros
- Field 15: empty string

## License
AGPL-3.0
