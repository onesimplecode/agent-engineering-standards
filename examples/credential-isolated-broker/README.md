# Credential-isolated broker

This reference pattern keeps external credentials in a host-side broker. An air-gapped agent
receives no token and can request only named operations over a private transport.

The broker validates exact resource scope and immutable event identity, binds mutation authority to
a single-use lease, revalidates immediately before mutation, and rejects stale revisions. Mount
the broker's containing directory read-only when the transport is a Unix socket; mounting only the
socket file can leave a long-lived sandbox attached to a deleted inode after broker restart.

The example is intentionally in-memory and has no external credentials or network access. It is a
policy shape, not a production broker implementation.
