docker build . -t cr.yandex/crpce8ajs4ag6uqpr3rk/arogov:latest
docker push cr.yandex/crpce8ajs4ag6uqpr3rk/arogov:latest
yc serverless container revision deploy --container-name arogov --image cr.yandex/crpce8ajs4ag6uqpr3rk/arogov:latest --cores 1 --memory 1GB --concurrency 1 --service-account-id aje71r5t4uav7rgcb71q --execution-timeout 30s --folder-id b1gi1r2esik5n4mm93ko --environment database=/ru-central1/b1gf81qohugfbonfebbj/etnsosa269pg1r1b9mna,endpoint=grpcs://ydb.serverless.yandexcloud.net:2135,USE_METADATA_CREDENTIALS=1,containerId=bba2fefntrt4hku7ua7t,folderId=b1gi1r2esik5n4mm93ko
