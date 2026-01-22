"""
Debug script to analyze blockchain corruption
"""
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def debug_blockchain():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT BlockID, Hash, PrevHash, Data
        FROM blockchain_log
        ORDER BY BlockID ASC
        """
    )
    blocks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"BLOCKCHAIN DEBUG ANALYSIS - Total Blocks: {len(blocks)}")
    print(f"{'='*80}\n")
    
    corrupted = []
    
    for i, block in enumerate(blocks):
        block_id, hash_val, prev_hash, data = block
        
        print(f"\n--- Block #{block_id} (Index {i}) ---")
        print(f"Stored Hash:    {hash_val[:32]}...")
        print(f"Stored PrevHash: {prev_hash[:32] if prev_hash != '0' else '0'}")
        print(f"Data (first 80 chars): {data[:80] if data else 'None'}...")
        
        # Check 1: Hash chain continuity
        if i > 0:
            expected_prev = blocks[i-1][1]  # Previous block's hash
            if prev_hash != expected_prev:
                print(f"❌ CHAIN BREAK: Expected prev_hash = {expected_prev[:32]}...")
                print(f"               But got prev_hash = {prev_hash[:32]}...")
                corrupted.append(block_id)
            else:
                print(f"✅ Chain link valid")
        else:
            if prev_hash == "0":
                print(f"✅ Genesis block (prev_hash = '0')")
            else:
                print(f"⚠️  Genesis block but prev_hash != '0': {prev_hash}")
        
        # Check 2: Hash integrity
        expected_hash = generate_hash(data + prev_hash)
        if hash_val != expected_hash:
            print(f"❌ HASH MISMATCH:")
            print(f"   Expected: {expected_hash[:32]}...")
            print(f"   Stored:   {hash_val[:32]}...")
            print(f"   Recalculation: SHA256('{data[:40]}...' + '{prev_hash[:16]}...')")
            if block_id not in corrupted:
                corrupted.append(block_id)
        else:
            print(f"✅ Hash integrity valid")
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total Blocks: {len(blocks)}")
    print(f"Verified: {len(blocks) - len(corrupted)}")
    print(f"Corrupted: {len(corrupted)}")
    
    if corrupted:
        print(f"\nCorrupted Block IDs: {corrupted}")
        print(f"\n⚠️  RECOMMENDATION:")
        print(f"   These blocks were likely created before the current hash function was implemented.")
        print(f"   Options:")
        print(f"   1. Accept them as legacy blocks (update verification to skip)")
        print(f"   2. Rebuild blockchain from scratch (DELETE FROM blockchain_log)")
        print(f"   3. Re-hash all blocks with correct algorithm")
    else:
        print(f"\n✅ All blocks verified successfully!")

if __name__ == "__main__":
    debug_blockchain()
