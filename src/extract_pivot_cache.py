import zipfile,re,sys
from lxml import etree
import pandas as pd
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def extract(path, defn, rec):
    z=zipfile.ZipFile(path)
    d=etree.fromstring(z.read(defn))
    fields=[]
    for cf in d.iter(NS+'cacheField'):
        si=cf.find(NS+'sharedItems')
        items=[]
        if si is not None:
            for it in si:
                items.append(it.get('v') if it.tag!=NS+'m' else None)
        fields.append((cf.get('name'),items))
    rows=[]
    with z.open(rec) as f:
        for ev,el in etree.iterparse(f,tag=NS+'r'):
            row=[]
            for i,c in enumerate(el):
                t=c.tag[len(NS):]
                if t=='x': row.append(fields[i][1][int(c.get('v'))])
                elif t=='m': row.append(None)
                else: row.append(c.get('v'))
            rows.append(row); el.clear()
    df=pd.DataFrame(rows,columns=[f[0] for f in fields])
    df.columns=[c.replace(' ','_') for c in df.columns]
    return df
c=extract('data/raw/Perturbed_Award_Course_Completions_Pivot_Table_2024.xlsx','xl/pivotCache/pivotCacheDefinition1.xml','xl/pivotCache/pivotCacheRecords1.xml')
c.to_pickle('data/processed/completions.pkl'); print(c.shape); print(c.head(3).T)
e=extract('data/raw/Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx','xl/pivotCache/pivotCacheDefinition1.xml','xl/pivotCache/pivotCacheRecords1.xml')
e.to_pickle('data/processed/enrolments.pkl'); print(e.shape); print(e.head(3).T)
