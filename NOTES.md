# Running

1. `git lfs pull`
2. `tar -xvjf dataset/eval.tar.bz2`

# Primary Goals

1. Count assertions with method sequences (i.e; assertEquals(0, a.foo().bar()))
2. Find distribution of method sequence lengths
3. How many method sequenced assertions have input arguments?
4. Find distribution of assertions appearing in one test
5. Find distribution of assertion types

---

mvn install:install-file \
 -Dfile=/Users/ooj/Dev/Research/assertion/methods2test-exploration/src/spoon-analyzer/chatunitest-core-2.1.0.jar \
 -DgroupId=io.github.ZJU-ACES-ISE \
 -DartifactId=chatunitest-core \
 -Dversion=2.0.0 \
 -Dpackaging=jar

todo:

1. get stats on distribution of std lib
2. get full resolution of std lib names
3. chatunitester
