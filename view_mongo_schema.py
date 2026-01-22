"""
View MongoDB Schema - Shows collections and document structure
Similar to DESCRIBE table in MySQL
"""
from pymongo import MongoClient
from pprint import pprint

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['steel_factory_nosql']

print("=" * 80)
print("MongoDB Database: steel_factory_nosql")
print("=" * 80)

# List all collections
collections = db.list_collection_names()
print(f"\n📦 Collections ({len(collections)}):")
for coll in collections:
    count = db[coll].count_documents({})
    print(f"  • {coll}: {count} documents")

# Show sample documents from each collection
for coll_name in collections:
    collection = db[coll_name]
    count = collection.count_documents({})
    
    if count > 0:
        print(f"\n{'=' * 80}")
        print(f"Collection: {coll_name}")
        print(f"{'=' * 80}")
        print(f"Total Documents: {count}")
        
        # Get one sample document to show structure
        sample = collection.find_one()
        if sample:
            print("\nSample Document Structure:")
            print("-" * 80)
            pprint(sample, indent=2, width=80)
            
            # Show field types
            print("\nField Types:")
            print("-" * 80)
            for key, value in sample.items():
                print(f"  {key:30} : {type(value).__name__}")
    else:
        print(f"\n{'=' * 80}")
        print(f"Collection: {coll_name} (EMPTY)")
        print(f"{'=' * 80}")

print("\n" + "=" * 80)
print("To explore interactively, use MongoDB Compass or mongosh CLI")
print("=" * 80)
