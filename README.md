# Uncertainty Quantification in LCA

This repository was built for a Master Thesis in 2024/2025 in the field of Life Cycle Assessment in Civil Engineering. 

### Topic: Evaluating the Impact of Data Input Selection in Life Cycle Assessment on Sustainable Infrastructure Projects

### Abstract

Road infrastructure projects rely on large quantities of resource-intensive materials. Life Cycle Assessment (LCA) is an essential tool to understand and mitigate their environmental impact. However, many LCA databases - from generic, license-based sources to regional or product-specific open source repositories - lack transparent or consistent information. This study addresses the question of how the quantification of uncertainty can improve the reliability and robustness of LCA results, while ad- dressing the impact on data input selection on sustainable infrastructure projects. A comparative LCA was conducted for three pavement designs (flexible and rigid) across the production and construction phases (A1–A5). Emission factors were sourced from three databases: ecoinvent, ökobaudat and Environmental Product Declarations (EPD). A pedigree-based approach was used to assign Data Quality Indicators (DQI), which were then translated into uncertainty factors and coefficients of variation (COV). Monte Carlo Sampling (MCS) was used to propagate these uncertainties to show how deviating assumptions for emission factors - especially for bitumen and cement - lead to signif- icant deviations in the global warming potential (GWP). The results show substan- tial differences in absolute GWP values and uncertainty ranges across the databases. ecoinvent generally showed higher and more variable GWP estimates, while ökobau- dat and EPD produced narrower distributions with lower median values, even though with limitations in data coverage. The degree of overlap of the probability density functions (PDF) differed depending on the design and life cycle stage. Overlapping PDFs can complicate decision-making, but increase the confidence by identifying crit- ical parameters that require closer evaluation. The study highlights that no single database is "best" suited to all conditions. The choice of data source should reflect the local context, material properties and data availability. To enhance the reliabil- ity of LCA in infrastructure projects, practitioners should systematically document assumptions, adopt probabilistic methods, and align database selection with project phases. The probabilistic approach presented in this study enables LCA practitioners to make more informed decisions regarding data input selection and design choices, supporting evidence-based sustainability practices in the road sector. Future research should expand on sensitivity analyses by systematically varying key parameters, such as functional units, system boundaries, and emission factor distributions, to identify the most influential factors in LCA models.

### Results

In ```results1.ipynb``` one can see the results of the study. The user could also run the ```app.py``` function to calculate and visualize results, but for a better and more straight overview the use of a jupyter notebook is recommended. 

### Changes to be applied

A user could change several inputs to adjust the product for their own needs:
1. LCI environmental background data in ```data```folder for the json files ```ecoinvent_..```, ```national_..```, and ```epd_..```
2. LCI foreground data in ```layers.json``` and ```design_options.json``` 


