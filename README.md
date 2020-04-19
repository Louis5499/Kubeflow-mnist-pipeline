# Kubeflow-mnist-pipeline
A pipeline example implements mnist TFJob & KFServing

## Description
Based on this [tutorial](https://chanyilin.github.io/kubeflow-e2e-tutorial.html), We build a example for piepline chaining.

The KFServingComponent.yaml in this repo is the modified verison, which uses the image created by this [repo](https://github.com/Louis5499/Kubeflow-kfserving).

## How To
1. Follow the Kubeflow instructions to install the pipeline environment([link](https://www.kubeflow.org/docs/pipelines/tutorials/build-pipeline/))
2. Enter into command line: ``dsl-compile --py ./tfJob_kfServing_pipeline.py --output ./output.tar.gz``

