def analyseDataset(decomposed_site,dataset):
    return pd.merge(decomposed_site,dataset,on='zone_id',how='left')
