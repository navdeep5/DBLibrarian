# DBLibrarian

This repository contains two Python scripts for managing and querying a MongoDB database of articles. The first script, `load-json.py`, loads data into the database and creates various indexes and views. The second script, `query.py`, provides functions to search articles by keywords and authors.

## Prerequisites

- Python 3.x
- MongoDB
- `pymongo` library

## Setup

1. Install the required Python package:
    ```bash
    pip install pymongo
    ```

2. Ensure that MongoDB is running on your local machine.

## Scripts

### 1. load-json.py

This script connects to a MongoDB server, loads a JSON file into a database, and creates necessary indexes and views.

#### Usage

```bash
python3 load-json.py <port_no> <jsonfile_name>
```


