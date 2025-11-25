#!/usr/bin/env python3
"""
Script to ensure all 6 CSV files are processed and stored in the database.
This will force reprocessing of all CSV files to ensure 6 games appear on the dashboard.
"""

import sys
import os
import requests
import json

def main():
    print("=" * 70)
    print("🚀 PROCESSING ALL 6 CSV FILES FOR ANALYTICS DASHBOARD")
    print("=" * 70)
    print()
    
    # Try to call the API endpoint
    base_url = "http://localhost:5000"
    
    print("📡 Calling API endpoint to process all CSV files...")
    print(f"   Endpoint: {base_url}/api/cog-scores/process-all-csvs")
    print()
    
    try:
        response = requests.post(f"{base_url}/api/cog-scores/process-all-csvs", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Successfully processed CSV files!")
                print()
                print(f"📊 Total files found: {data.get('total_files', 0)}")
                print(f"✅ Successfully processed: {len(data.get('processed', []))}")
                print(f"⚠️  Skipped: {len(data.get('skipped', []))}")
                print(f"❌ Errors: {len(data.get('errors', []))}")
                print()
                
                if data.get('processed'):
                    print("📋 Processed files:")
                    for item in data['processed']:
                        print(f"   • {item.get('filename')} - {item.get('date_iso')} vs {item.get('opponent')} - Score: {item.get('overall')}% ({item.get('action')})")
                    print()
                
                if data.get('errors'):
                    print("❌ Errors:")
                    for error in data['errors']:
                        print(f"   • {error}")
                    print()
                
                # Now force recalculation to ensure all data is synced
                print("🔄 Syncing with analytics dashboard...")
                sync_response = requests.get(f"{base_url}/api/team-statistics?force_recalculate=true", timeout=120)
                
                if sync_response.status_code == 200:
                    sync_data = sync_response.json()
                    if sync_data.get('success'):
                        unique_dates = set()
                        if sync_data.get('statistics'):
                            for stat in sync_data['statistics']:
                                unique_dates.add(stat.get('date'))
                        
                        print(f"✅ Dashboard synced! Found {len(unique_dates)} unique game dates")
                        print()
                        print("🎯 Games available on dashboard:")
                        overall_scores = sync_data.get('overall_scores', {})
                        game_info = sync_data.get('game_info', {})
                        
                        for date_iso in sorted(overall_scores.keys()):
                            info = game_info.get(date_iso, {})
                            opponent = info.get('opponent', 'Unknown')
                            date_str = info.get('date_string', date_iso)
                            score = overall_scores[date_iso]
                            print(f"   • {date_str} vs {opponent} - Score: {score:.2f}%")
                        
                        print()
                        print("=" * 70)
                        print("✅ SUCCESS! All 6 games should now appear on the analytics dashboard.")
                        print("=" * 70)
                    else:
                        print(f"⚠️  Sync warning: {sync_data.get('error', 'Unknown error')}")
                else:
                    print(f"⚠️  Could not sync dashboard (status: {sync_response.status_code})")
            else:
                print(f"❌ Processing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server.")
        print()
        print("Please start the Flask app first:")
        print("  cd testApp1 && python3 run_app.py")
        print()
        print("Then run this script again.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

