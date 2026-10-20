"""Regenerate journal assets from the exact CRISP-DM functions used by Streamlit."""
import hashlib
import json
from pathlib import Path
import sys
import textwrap
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
from matplotlib.text import Text
from matplotlib.ticker import MaxNLocator, FuncFormatter
import ml.reporting as report
from ml.datasets import load_training_dataset

OUT=ROOT/'artifacts'/'crisp_publicacion'
OUT.mkdir(parents=True,exist_ok=True)
manifest={ 'source_module':'ml.reporting', 'consumer':'app_streamlit.crisp_dm_panel', 'width_mm':85,'dpi':600,'data_source':'NOAA USCRN AZ_Yuma_27_ENE; artefactos CRISP-DM existentes, separados de Neon simulado','items':[] }
labels={'soil_moisture':'Humedad actual','relative_humidity':'Humedad relativa','soil_moisture_lag_24h':'Humedad t−24 h','rainfall_24h':'Lluvia 24 h','soil_moisture_lag_1h':'Humedad t−1 h','soil_moisture_lag_3h':'Humedad t−3 h','soil_moisture_lag_6h':'Humedad t−6 h','soil_moisture_lag_12h':'Humedad t−12 h','humidity_6h_mean':'Hum. relativa media 6 h','doy_sin':'Día del año seno','doy_cos':'Día del año coseno','rainfall':'Precipitación','rainfall_6h':'Lluvia 6 h','rainfall_48h':'Lluvia 48 h','soil_temperature':'Temperatura del suelo','air_temperature':'Temperatura del aire','temperature_6h_mean':'Temperatura media 6 h','solar_radiation':'Radiación solar','solar_6h_mean':'Radiación media 6 h','soil_moisture_change_1h':'Cambio humedad 1 h','soil_moisture_change_6h':'Cambio humedad 6 h','soil_moisture_change_12h':'Cambio humedad 12 h','soil_moisture_change_previous_24h':'Cambio previo 24 h','hour_sin':'Hora seno','hour_cos':'Hora coseno'}


def export(item):
    entry={k:getattr(item,k) for k in ('key','title','kind','interpretation','explainability')}
    if item.dataframe is not None:
        item.dataframe.to_csv(OUT/(item.key+'.csv'),index=False,encoding='utf-8-sig')
        entry['records']=item.dataframe.to_dict(orient='records')
    if item.figure is not None:
        fig=item.figure
        importance=item.key in ('permutation_importance','shap_global')
        fig.set_size_inches(85/25.4,(88 if importance else 65)/25.4)
        for ax in fig.axes:
            ax.set_title('')
            ax.tick_params(labelsize=7)
            ax.xaxis.label.set_size(8)
            ax.yaxis.label.set_size(8)
            if item.key=='model_selection_figure':
                ax.set_xticks(range(4),['Extra\nTrees','Ridge','Random\nForest','Hist. Gradient\nBoosting'])
                ax.tick_params(axis='x',rotation=0)
                for tick in ax.get_xticklabels(): tick.set_ha('center')
                ax.set_ylabel('Error (m³/m³)')
                legend=ax.legend(fontsize=7,loc='upper left',frameon=False)
            elif item.key=='bootstrap':
                ax.set_ylabel('Diferencia de error (m³/m³)')
                ax.yaxis.set_major_locator(MaxNLocator(5))
            elif item.key=='cv_figure':
                ax.set_xlabel('Ventana temporal')
                ax.set_ylabel('MAE (m³/m³)')
                ax.legend(fontsize=5.8,loc='upper left',frameon=False,ncol=2)
                ax.yaxis.set_major_locator(MaxNLocator(5))
            elif item.key=='final_timeseries':
                import matplotlib.dates as mdates
                ax.set_ylabel('Humedad (m³/m³)')
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
                ax.legend(fontsize=6,loc='upper right',frameon=False)
            elif importance:
                names=[tick.get_text() for tick in ax.get_yticklabels()]
                ax.set_yticks(ax.get_yticks(),[labels.get(name,name) for name in names])
                ax.tick_params(axis='y',labelsize=6.7)
                ax.set_xlabel('ΔMAE (10⁻⁴ m³/m³)' if item.key=='permutation_importance' else 'Media |SHAP| (10⁻⁴ m³/m³)',fontsize=7)
                ax.xaxis.set_major_locator(MaxNLocator(3))
                ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value * 1e4:g}'))
                ax.xaxis.get_offset_text().set_visible(False)
        for text in fig.findobj(Text):
            if text.get_fontsize()>8: text.set_fontsize(7)
        fig.subplots_adjust(left=.49 if importance else .24,right=.97,bottom=.16 if importance else .22,top=.97)
        for fmt in ('png','svg','pdf'):
            fig.savefig(OUT/(item.key+'.'+fmt),format=fmt,dpi=600,facecolor='white')
        report.plt.close(fig)
    manifest['items'].append(entry)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print('EXPORTED',item.key,flush=True)


artifacts=report.load_crisp_dm_artifacts()
for builder in [report.table_model_selection,report.figure_model_selection,report.table_cross_validation,report.figure_cross_validation,report.table_final_holdout,report.figure_final_timeseries,report.figure_bootstrap,report.table_statistical_tests]:
    export(builder(artifacts))
print('Loading real NOAA dataset for XAI...',flush=True)
data=load_training_dataset()
# Control resource use only; same samples, seed and repeats as Streamlit.
original_permutation=report.permutation_importance
def limited_permutation(*args,**kwargs):
    kwargs['n_jobs']=2
    return original_permutation(*args,**kwargs)
report.permutation_importance=limited_permutation
artifacts['model_bundle']['pipeline'].named_steps['model'].set_params(n_jobs=1)
print('Computing or loading saved permutation importance...',flush=True)
import pandas as pd
permutation=pd.read_csv(OUT/'permutation_all.csv') if '--reuse-xai' in sys.argv else report.calculate_permutation_importance(data,artifacts)
permutation.to_csv(OUT/'permutation_all.csv',index=False)
export(report.figure_permutation_importance(permutation))
print('Computing SHAP (500 holdout samples)...',flush=True)
shap={'global':pd.read_csv(OUT/'shap_global_values.csv'),'local':pd.read_csv(OUT/'shap_local.csv'),'explained_output':'soil_moisture_change_24h'} if '--reuse-xai' in sys.argv else report.calculate_shap_explanations(data,artifacts)
shap['global'].to_csv(OUT/'shap_global_values.csv',index=False)
export(report.figure_shap_global(shap))
export(report.table_shap_local(shap))
manifest['artifact_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (ROOT/'artifacts/ml/crisp_dm').glob('*') if path.suffix in ('.csv','.json')}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print('DONE',flush=True)
