# Webhook utilities

These utilities are a collection of snippets that leverage this project's features. They are built to be used as is or edited to match your own use case.

## Ingest & consume

Allows to ingest a text payload on a machine and consume it on another machine.

![Demo](../img/ingest_consume.gif?raw=true)

### Usage

#### Ingesting data on host 1

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

#### Consuming on host 2 (stdout)

```bash
host2$ python3 consume.py -i https://webhook.link/api/inspect/****
# John,Doe,120 jefferson st.,Riverside, NJ, 08075
# Jack,McGinnis,220 hobo Av.,Phila, PA,09119
# "John ""Da Man""",Repici,120 Jefferson St.,Riverside, NJ,08075
# Stephen,Tyler,"7452 Terrace ""At the Plaza"" road",SomeTown,SD, 91234
# ,Blankman,,SomeTown, SD, 00298
# "Joan ""the bone"", Anne",Jet,"9th, at Terrace plc",Desert City,CO,00123
```

#### Consuming on host 2 (opening a program)

Will save the content to a temporary file and open it with Microsoft Excel:

```bash
host2$ python3 consume.py -i https://webhook.link/api/inspect/**** --open "Microsoft Excel"
```

### Download these utilities

You can quickly download these utilities with:

```
wget -q https://raw.githubusercontent.com/gabfl/webhook/master/utilities/ingest.py
wget -q https://raw.githubusercontent.com/gabfl/webhook/master/utilities/consume.py
```

## Inspect loop (loop thru callbacks)

`inspect_loop.py` is a snippet that demonstrates how to programmatically loop thru callbacks across multiple pages.

For each callback, `process_callback()` is called and you can edit this method to match your use case.

### Usage

Example:

```bash
python3 inspect_loop.py --inspect https://webhook.link/api/inspect/****
# **** Payload ID 126,094 ****
# Payload number: 1
# Method POST on Mon, 06 Jan 2020 12:20:05 GMT
# 5 headers
# Body -> {'fail': False, 'user_id': 1234}
#
# **** Payload ID 126,093 ****
# Payload number: 2
# Method POST on Mon, 06 Jan 2020 12:20:08 GMT
# 5 headers
# Body -> {'fail': False, 'user_id': 1234}
#
# **** Payload ID 126,092 ****
# Payload number: 3
# Method POST on Mon, 06 Jan 2020 12:20:12 GMT
# 5 headers
# Body -> {'fail': False, 'user_id': 1234}
#
# **** Payload ID 126,091 ****
# Payload number: 4
# Method POST on Mon, 06 Jan 2020 12:20:18 GMT
# 7 headers
# Body -> {'fail': False, 'user_id': 1234}
```

### Download this utility

You can quickly download this utility with:

```
wget -q https://raw.githubusercontent.com/gabfl/webhook/master/utilities/inspect_loop.py
```
