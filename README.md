simplify-srl
============

Use Vickrey-Koller simplification rules for semantic role labeling

Information from Ravi
 14/02/18:
  - The code is here
    /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/source
  - I think config.sh in this directory is the script which runs everything.
 14/03/30:
  - Here is the code i used for our experiments.
    /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/instances
  - 100 instances were created to handle parts of the test file. The command to run one instance can be found here
    /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/intermediate_files/testCharShell/1
  - The output of each instance can be found here
    /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/intermediate_files/latesttestCharVerbPaths/1
  - In the output, we print all the predicates which got simplified to S-VP-V-<predicate> spine with all the rules which helped achieve this simplification
    {('managed', 87): [5, 9, 11, 14, 16, 20, 21, 22, 23, 61, 147], ('plunged', 49): [60, 62], ('stay', 94): [62]}
    The transformed chart is also in the log to check this transformation. 
  - The test set is partitioned using using this command
    /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/instances/create.py
