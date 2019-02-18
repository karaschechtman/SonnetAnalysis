# SonnetAnalysis

# Setup
1. Install dependencies:
  - Protobuf
  - DataMuse
1. Generate protobuf code:
```
protoc --proto_path=./proto/ --python_out=./proto/ proto/Poem.proto
```

2. Generate serialized protos from scraped data with flags for authors:
```
python3 generate_dataset.py --sidney --shakespeare --spenser --verbose
```

# Author
Created by Kara Schechtman (kws2121@columbia.edu).
