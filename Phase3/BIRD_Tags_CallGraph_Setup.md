# BIRD Tag and Call Graph Setup

This document summarizes the commands used to generate the **CTags symbol information** and **LLVM Call Graph** for BIRD 2.17.1.

## 1. Install Universal Ctags

```bash
sudo apt install universal-ctags
```

Verify installation:

```bash
ctags --version
```

## 2. Generate CTags

From the BIRD source directory:

```bash
cd ~/Projects/bird-2.17.1

ctags -R \
  --languages=C,C++ \
  --c-kinds=+p \
  --fields=+n \
  -f tags .
```

Verify the generated tags:

```bash
ls -lh tags
head -20 tags
wc -l tags
```

The generated `tags` file is used by the batch-building script to obtain function, structure, macro, and symbol information.

---

## 3. Install WLLVM

```bash
pip install wllvm
```

Verify:

```bash
which wllvm
which extract-bc
```

## 4. Configure LLVM/WLLVM

```bash
export LLVM_COMPILER=clang
export CC=wllvm
```

Verify:

```bash
echo $LLVM_COMPILER
echo $CC

clang --version
llvm-config --version
```

## 5. Build BIRD with WLLVM

From the BIRD source directory:

```bash
cd ~/Projects/bird-2.17.1

make clean
autoreconf -fi
./configure
make 
```

## 6. Extract LLVM Bitcode

After the build completes:

```bash
extract-bc bird
```

Verify:

```bash
ls -lh bird.bc
file bird.bc
```

---

## 7. Generate LLVM Call Graph

Check the LLVM version:

```bash
opt --version
```

Generate the Call Graph:

```bash
opt --disable-output --passes=dot-callgraph bird.bc
```

This generates:

```text
bird.bc.callgraph.dot
```

Verify:

```bash
ls -lh *.dot
find . -maxdepth 1 -name "*.dot" -print
head -20 bird.bc.callgraph.dot
```

Count Call Graph nodes and edges:

```bash
grep -c 'Node0x' bird.bc.callgraph.dot
grep -c -- '->' bird.bc.callgraph.dot
```

For the current BIRD 2.17.1 build:

```text
Nodes: 9534
Edges: 7549
```


These files provide symbol/function information and call-graph context for enriching the findings before sending them to the LLM for false-positive analysis.
