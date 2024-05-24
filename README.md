# DBLibrarian

## Table of Contents

- [Overview](#overview)
- [User Guide](#user-guide)
- [Testing Strategy](#testing-strategy)
- [Group Work Breakdown/Responsibilities](#group-work-breakdownresponsibilities)
- [Method of Coordination](#method-of-coordination)
- [Appendix](#appendix)

## Overview

This repository contains two Python scripts for managing and querying a MongoDB database of articles. The first script, `load-json.py`, loads data into the database and creates various indexes and views. The second script, `query.py`, provides functions to search articles by keywords and authors.

## Prerequisites

- Python 3.x
- MongoDB
- `pymongo` library

## Setup

1. Install the required Python package:
    ```
    pip install pymongo
    ```

2. Ensure that MongoDB is running on your local machine.

## User Guide

### 1. load-json.py

This script connects to a MongoDB server, loads a JSON file into a database, and creates necessary indexes and views.

#### Usage

```bash
python3 load-json.py <port_no> <jsonfile_name>
```
<port_no>: The port number on which MongoDB is running (default is 27017).
<jsonfile_name>: The name of the JSON file containing the data to be loaded into the database.

Example:
```bash
python3 load-json.py 27017 dblp-ref-1k.json
```

### 2. phase2.py

This script provides functions to query the MongoDB database for articles based on keywords and authors.

#### Usage

```python
from query import search_by_keyword, search_by_author

# Search articles by keyword
articles_by_keyword = search_by_keyword("keyword")

# Search articles by author
articles_by_author = search_by_author("author_name")
```

Replace "keyword" with the desired keyword and "author_name" with the name of the author you want to search for.


### Testing Strategy

- Unit tests for each function in `load-json.py` and `phase2.py`.
- Integration tests to ensure proper interaction with MongoDB.
- Testing against various data sets to ensure scalability and efficiency.

#### Group Work Breakdown/Responsibilities

- **Development**: Splitting the tasks of developing the scripts and testing them.
- **Documentation**: Writing the README and any additional documentation needed.
- **Testing**: Designing and executing the testing strategy.

#### Method of Coordination

- Regular meetings to discuss progress and any roadblocks.
- Use of project management tools like Trello or Asana for task tracking.
- Communication via Slack or other messaging platforms for quick updates.

### Appendix

#### License

This project is licensed under the MIT License - see the LICENSE file for details.
