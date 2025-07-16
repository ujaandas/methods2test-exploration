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
 -Dfile=lib/chatunitest-maven-plugin-2.1.0.jar \
 -DgroupId=io.github.zju-aces-ise \
 -DartifactId=chatunitest-maven-plugin \
 -Dversion=2.1.0 \
 -Dpackaging=jar

check that ok:
diff ~/.m2/repository/io/github/zju-aces-ise/chatunitest-core/2.0.0/chatunitest-core-2.0.0.jar chatunitest-core-2.1.0.jar

todo:

1. ~~get stats on distribution of std lib~~
2. ~~get full resolution of std lib names~~
3. ~~run chatunitester on dataset~~
4. ~~count # of variables inside assertion (to check if 2 vars are eq types)~~
5. ~~change graphs to make drop less drastic (logarithmic?)~~

todo:

1. ~~use github copilot instead of chattest, try it out~~
2. add number to top of bar graphs

todo:

1. instead of copilot, use simpler chatgpt-3.5-turbo and 4o-mini as well
2. temp 0.2, 0.0
3. input incl test prefix, method and classname
4. simple instr (pls generate 20 assertions)
5. collect w/ example and without example (of some other ground truth)
6. specify format - "only need to generate code etc etc..."

~~--> meet @ friday 10am~~

todo:

1. run with temp 0.0, 0.2, 0.7, compare all
2. collect json files
