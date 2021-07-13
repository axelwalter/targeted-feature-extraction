# Targeted Feature Extraction
### GUI for the OpenMS FeatureFinderMetaboIdent

This is a simple GUI tool for targeted feature extraction with the OpenMS tool FeatureFinderMetaboIdent.

https://abibuilder.informatik.uni-tuebingen.de/archive/openms/Documentation/experimental/feature/proteomic_lfq/html/a15547.html

https://pyopenms.readthedocs.io/en/latest/metabolomics_targeted_feature_extraction.html

Based on compounds specified in a target library (see links) this tool extracts features from mzML files.
Instead of using the OpenMS featureXML file format, this tool stores the results in a json file together with additional information
like the area under the curve.
