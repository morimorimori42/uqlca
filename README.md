# Uncertainty Quantification in LCA

`uqlca` is a small-scale Python tool developed as part of a Master’s thesis in 2024/2025, designed for conducting **comparative, probabilistic Life Cycle Assessment (LCA)** for road infrastructure projects.

It supports multiple life cycle stages (A1–A5) and allows combining environmental data from **ecoinvent**, **national databases**, and **Environmental Product Declarations (EPDs)**. Results are calculated based on design options defined by the user and can be visualized in Jupyter notebooks or via a simple app interface.

## 🔍 What the Tool Does

- Performs **probabilistic LCA** comparisons for different road design options.
- Uses multiple background databases (ecoinvent, national, EPD).
- Allows users to define custom **layers** and **materials** in each design.
- Generates results that can be visualized directly in a notebook.

## How to Customize the Model

You can easily adapt the model to your own project needs by modifying the input files in the `data/` folder. These inputs control both the **foreground system** (your defined road designs) and the **background system** (emission data sources like ecoinvent, national source or EPDs).

### Foreground System (user-defined designs)

- `design_options.json`:  
  Define different design alternatives. Each option includes a name and a list of layers it contains.

- `layers.json`:  
  Specify details for each construction layer, such as:
  - Materials used and their composition
  - Transport distances
  - Construction energy use
  - Density and thickness

> 💡 When you define a new material or layer in `layers.json` and reference it in a design in `design_options.json`, you also have to check the database files if you can find it there - otherwise you have to add it.

### Background System (LCI databases)

- `ecoinvent_*.json`, `national_*.json`, `epd_*.json`:  
  These files contain emission factors for materials and energy sources.
  You can:
  - Replace datasets with newer versions
  - Add region-specific factors
  - Expand impact categories in the future (e.g., acidification, eutrophication)

Each file uses a consistent JSON format, making it easy to edit or extend.

## Thesis information

Topic: Evaluating the Impact of Data Input Selection in Life Cycle Assessment on Sustainable Infrastructure Projects
Duration: 10 weeks

### Abstract

Road infrastructure projects rely on large quantities of resource-intensive materials. LCA is an essential tool to understand and mitigate their environmental impact. However, many LCA databases - from generic, license-based sources to regional or product-specific open source repositories - lack transparent or consistent information. This study addresses the question of how the quantification of uncertainty can improve the reliability and robustness of LCA results, while addressing the impact on data input selection on sustainable infrastructure projects. A comparative LCA was conducted for three pavement designs (flexible and rigid) across the production and construction phases (A1–A5). Emission factors were sourced from three databases: ecoinvent, ökobaudat and EPD. A pedigree-based approach was used to assign Data Quality Indicators (DQI), which were then translated into uncertainty factors and coefficients of variation (COV). Monte Carlo Sampling (MCS) was used to propagate these uncertainties to show how deviating assumptions for emission factors - especially for bitumen and cement - lead to significant deviations in the global warming potential (GWP). The results show substantial differences in absolute GWP values and uncertainty ranges across the databases. ecoinvent generally showed higher and more variable GWP estimates, while ökobaudat and EPD produced narrower distributions with lower median values, even though with limitations in data coverage. The degree of overlap of the probability density functions (PDF) differed depending on the design and life cycle stage. Overlapping PDFs can complicate decision-making, but increase the confidence by identifying critical parameters that require closer evaluation. The study highlights that no single database is "best" suited to all conditions. The choice of data source should reflect the local context, material properties and data availability. To enhance the reliability of LCA in infrastructure projects, practitioners should systematically document assumptions, adopt probabilistic methods, and align database selection with project phases. The probabilistic approach presented in this study enables LCA practitioners to make more informed decisions regarding data input selection and design choices, supporting evidence-based sustainability practices in the road sector. Future research should expand on sensitivity analyses by systematically varying key parameters, such as functional units, system boundaries, and emission factor distributions, to identify the most influential factors in LCA models.
