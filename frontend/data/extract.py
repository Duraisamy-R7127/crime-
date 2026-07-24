import json
import os

try:
    with open('india.geojson', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    tn_features = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        st_nm = props.get('NAME_1') or props.get('ST_NM') or props.get('state')
        if st_nm and 'tamil' in st_nm.lower():
            tn_features.append(feature)
            
    tn_data = {
        "type": "FeatureCollection",
        "features": tn_features
    }
    
    with open('tn.geojson', 'w', encoding='utf-8') as f:
        json.dump(tn_data, f)
        
    print(f"Extracted {len(tn_features)} districts for TN.")
except Exception as e:
    print("Error:", e)
