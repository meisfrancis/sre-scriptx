# This generate Atlas Search mappings for Mongoose Schema

## Syntax

```shell
node generate-atlas-search-mapping.js <schema file name to scan> <schema name you want to generate mapping for>
```

## Steps

Say, you have the following code base
```txt
api-example/
└── src/
    └── modules/
        └── abc/
            └── abc.schema.ts
```
And you want to generate mapping for a schema exported by file `abc.schema.ts` e.g., `HelloSchema`

```shell
$ npm i -D ts-node # ensure you have ts-node
$ git clone git@github.com:setel-engineering/infra-scripts.git
$ cp infra-scripts/atlas-search-mapping/generate-atlas-search-mapping.js api-example/src/modules/abc/
$ node generate-atlas-search-mapping.js ./abc.schema.ts HelloSchema 
```

Output will be

```shell
atlas-search-mapping.json
```

## Note

- The schema you want to generate must be included in the exports of the schema file
- Must have `./` preceding the schema file name