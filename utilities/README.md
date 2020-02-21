# Webhook utilities

## Ingest & consume

Allows to ingest a text payload on a machine and consume it on another machine.

![Demo](../img/ingest_consume.gif?raw=true)

### Ingesting data on host 1

```bash
host1$ cat addresses.csv
# John,Doe,120 jefferson st.,Riverside, NJ, 08075
# Jack,McGinnis,220 hobo Av.,Phila, PA,09119
# "John ""Da Man""",Repici,120 Jefferson St.,Riverside, NJ,08075
# Stephen,Tyler,"7452 Terrace ""At the Plaza"" road",SomeTown,SD, 91234
# ,Blankman,,SomeTown, SD, 00298
# "Joan ""the bone"", Anne",Jet,"9th, at Terrace plc",Desert City,CO,00123
host1$
host1$ cat addresses.csv | python3 ingest.py
# OK
# Consume this data with:
# python3 consume.py -i https://webhook.link/api/inspect/****
```

### Consuming on host 2 (stdout)

```bash
host2$ python3 consume.py -i https://webhook.link/api/inspect/****
# John,Doe,120 jefferson st.,Riverside, NJ, 08075
# Jack,McGinnis,220 hobo Av.,Phila, PA,09119
# "John ""Da Man""",Repici,120 Jefferson St.,Riverside, NJ,08075
# Stephen,Tyler,"7452 Terrace ""At the Plaza"" road",SomeTown,SD, 91234
# ,Blankman,,SomeTown, SD, 00298
# "Joan ""the bone"", Anne",Jet,"9th, at Terrace plc",Desert City,CO,00123
```

### Consuming on host 2 (opening a program)

Will save the content to a temporary file and open it with Microsoft Excel:

```bash
host2$ python3 consume.py -i https://webhook.link/api/inspect/**** --open "Microsoft Excel"
```
