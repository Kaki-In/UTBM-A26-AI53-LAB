# Project Phase 1
## Milestone 0

**Engineering checkpoint 1.**
Because of randomness

## Milestone 1

**Engineering checkpoint 2.**
Setting random_state=42 does not guarantee bit-for-bit identical results across every CPU, GPU, or software stack.
It only ensures reproducibility of the random number generation under the same conditions.

Results may still differ because of:

* Hardware differences: CPUs and GPUs may perform floating-point operations differently.
* Software versions: Different library, compiler, or driver versions may change algorithms or implementations.
* Parallel processing: Different execution orders can produce slightly different floating-point results.
* Non-deterministic operations: Some GPU operations are inherently non-deterministic.

## Milestone 2

**Engineering checkpoint 3.**
The Git remote stores source code and DVC tracking files, the DVC remote stores the actual raw images, and git push does not transfer DVC-managed images (use dvc push instead).

## Milestone 3

*nothing to write*

## Milestone 4

`PREPARE` depends directly on `reports/data_quality.json` (the result of `validate`), but not on `data/raw` directly, because `validate` already ensures `data/raw` is available. Once the data is validated, `data/raw` is ready. 

`TRAIN` must be updated for every change in the parameters, because each parameter influences the output of the task. 

`EVALUATE` needs to evaluate the selected model - identified by `selection.run_id`. 

The `metrics` provided to `DVC` are `reports/train_summary.json` and `reports/test_metrics.json` - the two files that actually provide real matric data. 

We get the following schema : 
```
        +--------------+          
        | data/raw.dvc |          
        +--------------+          
           **        **           
         **            **         
        *                **       
+----------+               *      
| validate |             **       
+----------+           **         
           **        **           
             **    **             
               *  *               
           +---------+            
           | prepare |            
           +---------+            
           **        **           
         **            **         
        *                *        
  +-------+         +----------+  
  | train |         | evaluate |  
  +-------+         +----------+  
```
## Milestone 5

**Engineering point 4**

 * Git : 

Git helps tracking the code, and whether the workspace was clean or not when running the project. 

* DVC : 

DVC versions the data and defines the pipeline stages (dependencies/outputs), so it can tell which stages need to rerun.

* MLflow

MLflow records everything about each training execution: parameters, metrics, artifacts, the dataset used, and the final model.

