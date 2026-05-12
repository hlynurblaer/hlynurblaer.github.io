import json
import requests
import pandas as pd
import time

# generate category mappings
url = "https://px.hagstofa.is:443/pxis/api/v1/is/Atvinnuvegir/sjavarutvegur/afkomasja/SJA08101.px"
meta = requests.get(url).json()
mappings = {
    var["code"]: dict(zip(var["values"], var["valueTexts"]))
    for var in meta["variables"]
}



url = "https://px.hagstofa.is:443/pxis/api/v1/is/Atvinnuvegir/sjavarutvegur/afkomasja/SJA08101.px"

def constuct_query():
    return {
        "query": [],
        "response": {
            "format": "json"
        }
        }

dfs = []

# size = 25
# l_ids_list = [list(range(1+i, min(i + size, len(mappings["Löndunarhöfn"])))) for i in range(0, len(mappings["Löndunarhöfn"]), size)]

# for f_id in range(1, len(mappings["Fisktegund"])):
# #for f_id in range(1, 3):
#     for l_ids in l_ids_list:
#         # londunarh_list = [str(i) for i in range(1,len(mappings["Löndunarhöfn"]))]
#         #londunarh_list = ["1", "2"]
#         man_list = [str(i) for i in range(1,len(mappings["Mánuður"]))]
#         # man_list = ["1", "2"]
#         q = constuct_query([str(f_id)], l_ids, man_list)
#         response = requests.post(url, json=q)
        
#         if response.status_code == 200:
#             data = response.json()["data"]
#             rows = [entry["key"] + entry["values"] for entry in data]
#             columns = [var["code"] for var in response.json()["columns"]]
#             dfs.append(pd.DataFrame(rows, columns=columns))
#         else:
#             print(f"Failed for fish {f_id}: {response.status_code}")
#             print(json.dumps(q, indent=2, ensure_ascii=False))
        
#         print(f'sleep, l_id is {l_ids[-1]}')
#         time.sleep(1)
        
#     print(f'{f_id}/{len(mappings["Fisktegund"])} fiskar   //   {100*(f_id/len(mappings["Fisktegund"])):.1f}%')



q = constuct_query()
response = requests.post(url, json=q)
if response.status_code == 200:
    data = response.json()["data"]
    rows = [entry["key"] + entry["values"] for entry in data]
    columns = [var["code"] for var in response.json()["columns"]]
    dfs.append(pd.DataFrame(rows, columns=columns))
else:
    print(f"Failed for fish {f_id}: {response.status_code}")
    print(json.dumps(q, indent=2, ensure_ascii=False))

df = pd.concat(dfs, ignore_index=True)


# apply mappings
for col, mapping in mappings.items():
    if col in df.columns:
        df[col] = df[col].map(mapping)


df.to_csv("rekstur_data.csv", index=False)