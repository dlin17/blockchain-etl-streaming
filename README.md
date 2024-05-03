# notes on managing streams

- hardest part is keeping track of which blocks you have already downloaded
- container syncs `last_synced_block.txt` into GCS every 60s but guarantee you read a block exactly once when jobs restart
- container can restart if you push an upgrade or OOM
- avoid `helm upgrade`, use `helm uninstall` and then `helm install` to force a GCS sync
- be careful with memory, the larger your block batch size the more memory it will require, use a generous memory allocation when backfilling with large block batch sizes, can be scaled down afterwards

# redeploying

let's say that a chain is failing, checks the logs to see the source of the error

###  nothing to sync or RPC 4xx or 5xx errors

this means either the chain is stalled, the node is stalled, the node is rate limiting, or the node is down

**solution**
* usually just wait and it will recover on it's own
* if rate limiting on a public node keeps occuring you may need to find a new node, you can find public nodes on [Chainlist](https://chainlist.org/)
* rate limiting can sometimes be solved by decreasing `BLOCK_BATCH_SIZE`

### node is syncing but never pushed to pub/sub because it's going OOM

usually caused by a sudden spike in activity or a very large log(s),

**action**
* edit the config in `charts/blockchain-etl-streaming/block_data` to increase requested resources, e.g. adding

```
stream:
  resources:
    requests:
      memory: "2048Mi"
      cpu: "300m"
    limits:
      memory: "4096Mi"
      cpu: "800m"
```

* uninstall the current pod (avoid using upgrade), e.g.

```
> helm uninstall {chain} # replace {chain}
```

* reinstall the pod, e.g. from the root directory of this repo run

```
> helm install {chain} charts/blockchain-etl-streaming/ --values charts/blockchain-etl-streaming/block_data/{chain}.yaml
```

### other error with `etheruem-etl`

very uncommon but if it happens will require updating the `ethereum-etl` docker image and redeploying

* current image repo -> https://github.com/dlin17/ethereum-etl
* image registry -> https://console.cloud.google.com/artifacts/docker/circle-ds-pipelines/us-central1/blockchain-etl/blockchainetl?project=circle-ds-pipelines