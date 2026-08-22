# Production hotfix — ticket aging Categorical fillna

**Error:** `TypeError: Cannot setitem on a Categorical with a new category (0)`

**Where:** `script.py` → `build_ticket_aging_analysis` → `groupby('aging_bucket').fillna(0)`

**Fix applied in repo:** convert `aging_bucket` to object and only `fillna` on the numeric `Tickets` column.

If Cloud has not picked up `script.py` yet, replace the aging block with:

```python
p['aging_bucket'] = pd.cut(p['age_days'], bins=bins, labels=labels)
aging = p.groupby('aging_bucket', observed=False, as_index=False).agg(Tickets=('id','size'))
if 'aging_bucket' in aging.columns:
    aging['aging_bucket'] = aging['aging_bucket'].astype(object)
aging['Tickets'] = pd.to_numeric(aging['Tickets'], errors='coerce').fillna(0).astype(int)
```
