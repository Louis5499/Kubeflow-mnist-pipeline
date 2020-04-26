import json
from kfp import components
import kfp.dsl as dsl

@dsl.pipeline(
    name="Launch kubeflow tfjob & kfserving template",
    description="An example to launch tfjob."
)
def mnist_pipeline(
        name="mnist",
        namespace="kubeflow",
        workerNum=2,
        deleteAfterDone=False):
    tfjob_launcher_op = components.load_component_from_file("./tfJobComponent.yaml")
    kfserving_op = components.load_component_from_file("./kfServingComponent.yaml")
    duplicated_gs_deletion_op = components.load_component_from_file("./duplicatedGsDeleteComponent.yaml")
    bucket = "kf_second_test"
    
    chief = {
      "replicas": 1,
      "template": {
        "metadata": {
          "annotations": {
            "sidecar.istio.io/inject": "false"
          }
        },
        "spec": {
          "containers": [
            {
              "command": [
                "/usr/bin/python",
                "/opt/model.py",
                "--tf-model-dir=$(modelDir)",
                "--tf-export-dir=$(exportDir)",
                "--tf-train-steps=$(trainSteps)",
                "--tf-batch-size=$(batchSize)",
                "--tf-learning-rate=$(learningRate)"
              ],
              "env": [
                {
                  "name": "modelDir",
                  "value": f"gs://{bucket}/my-model"
                },
                {
                  "name": "exportDir",
                  "value": f"gs://{bucket}/my-model/export"
                },
                {
                  "name": "trainSteps",
                  "value": "200"
                },
                {
                  "name": "batchSize",
                  "value": "100"
                },
                {
                  "name": "learningRate",
                  "value": "0.01"
                }
              ],
              "image": "gcr.io/kubeflow-examples/mnist/model:build-1202842504546750464",
              "name": "tensorflow",
              "workingDir": "/opt"
            }
          ],
          "restartPolicy": "OnFailure",
          "serviceAccount": "k8s-sa"
        }
      }
    }
    worker = {}
    if workerNum > 0:
      worker = {
        "replicas": workerNum,
        "template": {
          "metadata": {
            "annotations": {
              "sidecar.istio.io/inject": "false"
            }
          },
          "spec": {
            "containers": [
              {
                "command": [
                  "/usr/bin/python",
                  "/opt/model.py",
                  "--tf-model-dir=$(modelDir)",
                  "--tf-export-dir=$(exportDir)",
                  "--tf-train-steps=$(trainSteps)",
                  "--tf-batch-size=$(batchSize)",
                  "--tf-learning-rate=$(learningRate)"
                ],
                "env": [
                  {
                    "name": "modelDir",
                    "value": f"gs://{bucket}/my-model"
                  },
                  {
                    "name": "exportDir",
                    "value": f"gs://{bucket}/my-model/export"
                  },
                  {
                    "name": "trainSteps",
                    "value": "200"
                  },
                  {
                    "name": "batchSize",
                    "value": "100"
                  },
                  {
                    "name": "learningRate",
                    "value": "0.01"
                  }
                ],
                "image": "gcr.io/kubeflow-examples/mnist/model:build-1202842504546750464",
                "name": "tensorflow",
                "workingDir": "/opt"
              }
            ],
            "restartPolicy": "OnFailure",
            "serviceAccount": "k8s-sa"
          }
        }
      }

    ps = {
      "replicas": 1,
      "template": {
        "metadata": {
          "annotations": {
            "sidecar.istio.io/inject": "false"
          }
        },
        "spec": {
          "containers": [
            {
              "command": [
                "/usr/bin/python",
                "/opt/model.py",
                "--tf-model-dir=$(modelDir)",
                "--tf-export-dir=$(exportDir)",
                "--tf-train-steps=$(trainSteps)",
                "--tf-batch-size=$(batchSize)",
                "--tf-learning-rate=$(learningRate)"
              ],
              "env": [
                {
                  "name": "modelDir",
                  "value": f"gs://{bucket}/my-model"
                },
                {
                  "name": "exportDir",
                  "value": f"gs://{bucket}/my-model/export"
                },
                {
                  "name": "trainSteps",
                  "value": "200"
                },
                {
                  "name": "batchSize",
                  "value": "100"
                },
                {
                  "name": "learningRate",
                  "value": "0.01"
                }
              ],
              "image": "gcr.io/kubeflow-examples/mnist/model:build-1202842504546750464",
              "name": "tensorflow",
              "workingDir": "/opt"
            }
          ],
          "restartPolicy": "OnFailure",
          "serviceAccount": "k8s-sa"
        }
      }
    }
    tfJobLauncher = tfjob_launcher_op(
      name=name,
      namespace=namespace,
      worker_spec=worker,
      chief_spec=chief,
      ps_spec=ps,
      delete_finished_tfjob=deleteAfterDone
    )

    duplicatedGsDirDeletion = duplicated_gs_deletion_op(
      bucket_name=bucket
    ).after(tfJobLauncher)

    kfserving_op(
      name="kfserving",
      default_model_uri=f"gs://{bucket}/my-model/export",
      model_name="main",
      transformer_custom_image="jackfantasy/image-transformer:v1"
    ).after(duplicatedGsDirDeletion)

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(mnist_pipeline, __file__ + ".tar.gz")
