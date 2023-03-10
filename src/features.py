import rasterio
import rasterio.mask
import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm


class FeatureCalculator():
    
    def __init__(
        self,
        shape_path,
        image_path
    ):
        self.plot = gpd.read_file(shape_path)
        self.src = rasterio.open(image_path)
        
        self.bands = [
            19, 41, 59, 74, 94, 119, 137, 208
        ]
        
        
    
    def band_reflectance(
        self,
        geom
    ):
        mask_img, _ = rasterio.mask.mask(
            self.src,
            [geom],
            crop=True,
            nodata=np.nan
        )
        mask_img = mask_img.reshape(mask_img.shape[0], -1)
        mean_ref = np.nanmean(mask_img, axis=1)
        mean_ref = mean_ref[self.bands]
        return mean_ref.tolist()
        
        
        
    def calculate_features(
        self
    ):
        n_plots= self.plot.shape[0]
        feature_data = {}
        for i in tqdm(range(n_plots)):
            geom = self.plot.loc[i, 'geometry']
            nbi = self.plot.loc[i, 'dual_nbi']
            plotid = self.plot.loc[i, 'plotidfile']
            mean_ref = self.band_reflectance(geom)
            data = [nbi] + mean_ref
            feature_data[plotid] = data
        feature_data = pd.DataFrame(feature_data).T
        feature_data.columns = [
            'nbi', 441.525, 490.912, 531.319, 564.992,
            609.889, 666.011, 706.418, 865.803
        ]
        self.src.close()
        return feature_data
    
    
    
if __name__=="__main__":
    
    shape_paths = [
        r"F:\sustain\data\shapes\20210720-d3.shp",
        r"F:\sustain\data\shapes\20210804-d3.shp",
        r"F:\sustain\data\shapes\20220811-d16.shp"
    ]
    image_paths = [
        r"F:\sustain\data\hyper-images\20210720-ofallon-d3-hyper-50m\mosaic_long_4.dat",
        r"F:\sustain\data\hyper-images\20210804-ofallon-d4-hyper-50m\mosaic.dat",
        r"F:\sustain\data\hyper-images\20220811-ofallon-d16-hyper-50m\mosaic.dat"
    ]
    
    dfs = []
    for shape_path, image_path in zip(shape_paths, image_paths):
        fc = FeatureCalculator(
            r"F:\sustain\data\shapes\20210720-d3.shp",
            r"F:\sustain\data\hyper-images\20210720-ofallon-d3-hyper-50m\mosaic_long_4.dat"
        )
        df = fc.calculate_features()
        dfs.append(df)
    
    dfs = pd.concat(dfs)
    dfs.to_csv(r"F:\sustain\data\extracted\extracted_features.csv")
    
            