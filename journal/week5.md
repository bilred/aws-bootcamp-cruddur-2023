# Week 5 — DynamoDB and Serverless Caching


## DynamoDB Bash Scripts

```sh
./bin/ddb/schem-load
```

## Conceptualisation
DynamoDB is a NoSQL database, based on key, value concepts (non-relational)
- Data duplication would be good if we have a use case in our application (specifically with data volume) unlike the relational database.
- To design our data structure we need to find our "Utilisation Patterns"
- Based on our utilization patterns, We can make decisions about what we need
  * Flat table (make essay the relation without joining but with duplication data)
  * Who is our P.K
  * Design what the application does is important before starting


## The Boundaries of DynamoDB

- When you write a query you have provide a Primary Key (equality) eg. pk = 'andrew'
- Are you allowed to "update" the Hash and Range?
  - No, whenever you change a key (simple or composite) eg. pk or sk you have to create a new item.
    - you have to delete the old one
- Key condition expressions for query only for RANGE, HASH is only equality 
- Don't create UUID for entity if you don't have an access pattern for it


3 Access Patterns