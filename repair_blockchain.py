"""
Blockchain Repair Script - Rebuilds blockchain with correct SHA-256 hashing
"""
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def rebuild_blockchain():
    print("\n" + "="*80)
    print("BLOCKCHAIN REPAIR TOOL - Auto Mode")
    print("="*80)
    print("\n🔧 Rebuilding blockchain with correct SHA-256 hashing...")
    print("   All block data will be preserved, hashes recalculated.\n")
    
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = conn.cursor()
    
    # Step 1: Fetch all blocks in order
    cursor.execute(
        """
        SELECT BlockID, PerformanceID, Data, Timestamp
        FROM blockchain_log
        ORDER BY BlockID ASC
        """
    )
    blocks = cursor.fetchall()
    
    print(f"\n📊 Found {len(blocks)} blocks to rebuild...")
    
    # Step 2: Delete all blocks
    print("🗑️  Deleting old blocks...")
    cursor.execute("DELETE FROM blockchain_log")
    conn.commit()
    
    # Step 3: Re-insert blocks with correct hashing
    print("🔨 Rebuilding blockchain with correct hashes...")
    prev_hash = "0"
    
    for i, (old_block_id, perf_id, data, timestamp) in enumerate(blocks, 1):
        # Calculate new hash
        new_hash = generate_hash(data + prev_hash)
        
        # Insert with correct hash
        cursor.execute(
            """
            INSERT INTO blockchain_log (PerformanceID, Hash, PrevHash, Data, Timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (perf_id, new_hash, prev_hash, data, timestamp)
        )
        
        print(f"  Block {i:2d}: {data[:60]}...")
        print(f"          Hash: {new_hash[:32]}...")
        
        # Update prev_hash for next block
        prev_hash = new_hash
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Blockchain rebuilt successfully!")
    print(f"   Total blocks: {len(blocks)}")
    print(f"   All hashes recalculated with SHA-256")
    print(f"\n🔍 Run 'python debug_blockchain.py' to verify integrity.\n")

if __name__ == "__main__":
    rebuild_blockchain()
