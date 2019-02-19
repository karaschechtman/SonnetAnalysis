# SonnetAnalysis

# Setup
1. Install dependencies:
	- Protobuf
	- DataMuse
	- NetworkX

2. Generate protobuf code:
```
protoc --proto_path=./proto/ --python_out=./proto/ proto/Poem.proto
```

3. Generate serialized protos by scraping data (or download [here]('https://drive.google.com/file/d/17AN6tK5vQw-RZ4iy9ruAlAonyeuSetCe/view?usp=sharing')):
```
python3 generate_dataset.py --sidney --shakespeare --spenser --verbose
```

# Classes
- `DataLoader`: for loading data on a sonnet sequence.
- `RhymeLabeler`: for labeling a poem's rhyme scheme and
generating / saving rhyming dictionaries.

# To be made
- `SequenceStats`: for analyzing sequences
- `SequenceExplorer`: for making html pages with breakdowns
of sequence stats. will be hidden inside SequenceStats.

# Author
Created by Kara Schechtman (kws2121@columbia.edu).
