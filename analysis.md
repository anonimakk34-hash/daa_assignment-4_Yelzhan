# Assignment 4 — analysis (complete in English)

## Environment and commands

- **Selected language and runtime:** Python (`submission.json`: `{"language": "Python"}`), CPython `3.11.2` locally (fully compatible with Python `3.12+` in GitHub Actions `ubuntu-24.04`).
- **OS / CPU / RAM:** Linux `6.12.105+` (`x86_64`), Intel(R) Xeon(R) Platinum 8481C (2 vCPUs), 7.8 GiB RAM.
- **Setup, public check, student test, and benchmark commands (run from repository root):**
  ```sh
  python3 tools/run.py --setup
  python3 tools/run.py --check
  python3 tools/run.py --input tests/student/student_tests.jsonl
  python3 tests/student/benchmark_search.py
  ```
- **Moodle submission note:** Commit `submission.json`, `Python/source/algorithms.py`, `tests/student/student_tests.jsonl`, `tests/student/benchmark_search.py`, and `ANALYSIS.md`, verify that GitHub Actions **Public checks** pass, and submit the exact commit URL with its full 40-character SHA in Moodle Online text.

## Algorithm explanations

### 1. `lcs` — Longest Common Subsequence (Prefix DP)

- **State and index meaning:** For strings $a$ of length $m = |a|$ and $b$ of length $n = |b|$, `dp[i][j]` (for $0 \le i \le m$, $0 \le j \le n$) stores the maximum length of a common subsequence of prefixes `a[0..i-1]` (first $i$ characters of $a$) and `b[0..j-1]` (first $j$ characters of $b$).
- **Base cases and transitions:**
  - Base cases: `dp[i][0] = 0` for all $0 \le i \le m$ and `dp[0][j] = 0` for all $0 \le j \le n$ (an empty prefix has only the empty subsequence `""` of length $0$).
  - Transition for $i \ge 1, j \ge 1$:
    $$\text{dp}[i][j] = \begin{cases} \text{dp}[i-1][j-1] + 1 & \text{if } a[i-1] = b[j-1], \\ \max(\text{dp}[i-1][j],\, \text{dp}[i][j-1]) & \text{if } a[i-1] \ne b[j-1]. \end{cases}$$
- **Processing order and dependency readiness:** Rows $i = 1 \dots m$ are filled outer-loop and columns $j = 1 \dots n$ inner-loop. Computing `dp[i][j]` requires `dp[i-1][j-1]` (previous row, previous column), `dp[i-1][j]` (previous row, same column), and `dp[i][j-1]` (same row, previous column), all of which are already computed before `(i, j)`.
- **Correctness argument:** By induction on $i + j$: if $a[i-1] = b[j-1] = c$, any common subsequence of $a[0..i-1]$ and $b[0..j-1]$ not ending at both final characters has length at most $\max(\text{dp}[i-1][j], \text{dp}[i][j-1]) \le \text{dp}[i-1][j-1] + 1$, whereas appending $c$ to an optimal LCS of $a[0..i-2]$ and $b[0..j-2]$ achieves $\text{dp}[i-1][j-1] + 1$. If $a[i-1] \ne b[j-1]$, no common subsequence can simultaneously match both $a[i-1]$ and $b[j-1]$ as its final element, so an optimal common subsequence must lie entirely within $(a[0..i-2], b[0..j-1])$ or $(a[0..i-1], b[0..j-2])$. Thus taking $\max(\text{dp}[i-1][j], \text{dp}[i][j-1])$ preserves optimality.
- **Reconstruction and tie handling:** Starting at $(i, j) = (m, n)$, if $a[i-1] = b[j-1]$, we append $a[i-1]$ and move diagonally to $(i-1, j-1)$. Otherwise, if $\text{dp}[i-1][j] \ge \text{dp}[i][j-1]$, we step up to $(i-1, j)$ (breaking ties deterministically in favor of stepping up); else we step left to $(i, j-1)$. Collected characters are reversed at the end. Every diagonal step decreases $\text{dp}[i][j]$ by $1$ and matches identical characters in decreasing index order, guaranteeing a valid common subsequence of length $\text{dp}[m][n]$.
- **Time and memory complexity:** Let $m = |a|$ and $n = |b|$. Input storage is $O(m + n)$ and output storage is $O(\text{dp}[m][n] + 1)$. Using a 2D Python list of size $(m+1) \times (n+1)$, time complexity is $O((m+1)(n+1))$ and auxiliary memory is $O((m+1)(n+1))$ (with an early $O(1)$ exit when $m = 0$ or $n = 0$).
- **Boundary/counterexample test (`S02-lcs-subseq-repeats`):** `a = "abacaba"`, `b = "babbca"` returns `{"length": 4, "sequence": "abca"}`. This detects implementations that mistakenly solve longest common *substring* (which has length $2$, `"ab"` or `"ba"`) or greedily consume the first matching character in $b$.

### 2. `merge` — Ordered Adjacent-Block Merging (Interval DP)

- **State and index meaning:** For $n$ initial blocks `sizes[0..n-1]`, each original block starts as closed interval $[i, i]$. For $0 \le l \le r < n$, `dp[l][r]` is the minimum total cost to merge the contiguous subarray of original blocks $l \dots r$ into a single combined block $[l, r]$, and `split[l][r] = k` ($l \le k < r$) stores the midpoint where the final merge combines $[l, k]$ and $[k+1, r]$.
- **Base cases and transitions:**
  - Base cases: for $n \le 1$, return `cost = 0, plan = []`. For $n \ge 2$, `dp[i][i] = 0` for all $0 \le i < n$ because a single block $[i, i]$ requires zero merges.
  - Let `pref[i]` be the prefix sum $\sum_{t=0}^{i-1} \text{sizes}[t]$, so the combined weight of $[l, r]$ is $W(l, r) = \text{pref}[r+1] - \text{pref}[l]$.
  - Transition for $0 \le l < r < n$:
    $$\text{dp}[l][r] = \min_{l \le k < r} \bigl(\text{dp}[l][k] + \text{dp}[k+1][r]\bigr) + W(l, r).$$
- **Processing order and dependency readiness:** Intervals are evaluated by increasing length $\ell = r - l + 1$ from $2$ to $n$. For an interval $[l, r]$ of length $\ell$, every candidate split $k \in [l, r-1]$ references subintervals $[l, k]$ of length $k - l + 1 < \ell$ and $[k+1, r]$ of length $r - k < \ell$, both of which have strictly smaller lengths and are already computed.
- **Correctness argument:** Because merges are restricted to adjacent blocks and preserve original order, the final step producing $[l, r]$ must merge two adjacent blocks $[l, k]$ and $[k+1, r]$ for some $l \le k < r$ at an immediate cost equal to the invariant sum $\sum_{t=l}^{r} \text{sizes}[t] = W(l, r)$. Because the internal merge sequences producing $[l, k]$ and $[k+1, r]$ operate on disjoint index ranges, their costs are independent and exhibit optimal substructure. Minimizing over all $k \in [l, r-1]$ therefore finds the global minimum cost for $[l, r]$.
- **Reconstruction and tie handling:** During DP, strict inequality (`cand < best`) deterministically keeps the smallest split index $k$ on ties. To reconstruct `plan`, we perform an iterative postorder traversal of the split tree rooted at $[0, n-1]$: for $[l, r]$ with $l < r$ and $k = \text{split}[l][r]$, we recursively emit all merges for $[l, k]$, then all merges for $[k+1, r]$, and finally append `[l, k, r]`. Child merges must precede their parent merge `[l, k, r]` so that the constituent blocks $[l, k]$ and $[k+1, r]$ already exist as adjacent blocks when `[l, k, r]` is executed.
- **Time and memory complexity:** Input size is $O(n)$ and output plan size is $O(\max(0, n-1))$. For $n \ge 1$, the three nested loops over $\ell$, $l$, and $k$ perform $\binom{n+1}{3} = \Theta(n^3)$ iterations in $O(n^3)$ time using 64-bit-safe Python integers, with $O(n^2)$ auxiliary memory for `dp`, `dp_col` (transposed table for contiguous row lookups), and `split`, plus $O(n)$ for `pref` and the traversal stack. For $n = 0$, time and auxiliary memory are $O(1)$.
- **Boundary/counterexample test (`S05-merge-balanced-vs-greedy`):** `sizes = [10, 1, 10, 1]` yields `cost = 44` and `plan = [[0, 0, 1], [2, 2, 3], [0, 1, 3]]`. This catches two common defects: (1) greedy arbitrary merging (merging the two smallest elements `1` and `1` at indices $1$ and $3$, which violates adjacency), and (2) pre-order or linear-only plan reconstruction (which would attempt to merge `[0, 1, 3]` before `[2, 2, 3]` has been created).

### 3. `tree` — Maximum-Weight Independent Set on a Tree (Tree DP)

- **State and index meaning:** Rooting the undirected tree arbitrarily at vertex $0$ (for $n \ge 1$), for each vertex $u \in \{0, \dots, n-1\}$:
  - `take[u]` is the maximum weight of an independent set in the subtree rooted at $u$ given that $u$ **is** selected.
  - `skip[u]` is the maximum weight of an independent set in the subtree rooted at $u$ given that $u$ **is not** selected.
- **Base cases and transitions:**
  - Empty tree ($n = 0$): return `weight = 0, selected = []`.
  - For every leaf $u$: `take[u] = weights[u]` and `skip[u] = 0`.
  - For an internal vertex $u$ with children $C(u)$:
    $$\text{take}[u] = \text{weights}[u] + \sum_{v \in C(u)} \text{skip}[v], \qquad \text{skip}[u] = \sum_{v \in C(u)} \max(\text{take}[v],\, \text{skip}[v]).$$
- **Processing order and dependency readiness:** To prevent recursion depth failures (`RecursionError`) on deep chains up to $n = 100{,}000$, we build an adjacency list and run an iterative breadth-first search (BFS) from root $0$ to record `parent[u]` and topological array `order`. Iterating $u$ in `reversed(order)` visits every child before its parent (a valid bottom-up postorder), ensuring `take[v]` and `skip[v]` are finalized before propagating into `parent[u]`.
- **Correctness argument:** Because a tree has no cycles, removing $u$ disconnects the subtrees of its children $v \in C(u)$. If $u$ is selected, no child $v \in C(u)$ may be selected, so the best valid choice in each child subtree is `skip[v]`. If $u$ is skipped, each child $v$ may independently be either taken or skipped, contributing $\max(\text{take}[v], \text{skip}[v])$. Note that `skip[u] >= 0` holds for all $u$ (since the empty set is always valid), so negative-weight vertices never force a negative total weight.
- **Reconstruction and tie handling:** After the bottom-up pass, the optimal weight is $\max(\text{take}[0], \text{skip}[0])$. We reconstruct `selected` in a single top-down pass over `order`: vertex $u$ is selected (`chosen[u] = True`) if and only if its parent $p = \text{parent}[u]$ was **not** selected (`p == -1 or not chosen[p]`) and `take[u] > skip[u]`. Breaking ties (`take[u] == skip[u]`) in favor of `skip[u]` avoids selecting zero-weight vertices unnecessarily while preserving optimal weight.
- **Time and memory complexity:** Input size is $O(n)$ (with $n-1$ edges) and output size is $O(|selected| + 1) \le O(n + 1)$. Adjacency lists, `order`, `parent`, `visited`, `take`, `skip`, and `chosen` each use $O(n)$ space, giving $O(n + 1)$ time and $O(n + 1)$ auxiliary memory ($O(1)$ for $n = 0$).
- **Boundary/counterexample test (`S08-tree-star-skip-root`):** `n = 4, weights = [10, 8, 8, 8], edges = [[0,1], [0,2], [0,3]]` returns `weight = 24, selected = [1, 2, 3]`. This detects greedy largest-weight-first heuristics (which pick root $0$ of weight $10$ and block all three leaves of total weight $24$).

### 4. `naive` — Exact Pattern Search (Naive Baseline)

- **State and index meaning:** Given `text` of length $n$ and `pattern` of length $m$, outer index $i \in [0, n - m]$ is the candidate zero-based start position in `text`, and inner index $j \in [0, m - 1]$ is the offset inside `pattern` comparing `text[i + j]` against `pattern[j]`.
- **Base cases and transitions:**
  - If $m = 0$, every boundary $0 \dots n$ matches immediately: return `list(range(n + 1))`.
  - If $m > n$, no window of length $m$ fits inside `text`: return `[]`.
  - For $1 \le m \le n$, for each $i = 0 \dots n - m$, advance $j$ from $0$ to $m - 1$ while `text[i + j] == pattern[j]`. If all $m$ characters match, append $i$ to `positions`; on the first mismatch, break the inner loop and advance to $i + 1$.
- **Processing order and dependency readiness:** Candidate start positions $i$ are tested in strictly increasing order $0, 1, \dots, n - m$. Advancing $i$ by $1$ after either a match or a mismatch naturally finds all overlapping occurrences in increasing order.
- **Correctness argument:** A substring of length $m \ge 1$ starting at $i$ lies inside `text[0..n-1]` if and only if $0 \le i \le n - m$. Exhaustively checking `text[i + j] == pattern[j]` for all $0 \le j < m$ is the exact definition of substring equality.
- **Time and memory complexity:** Input storage is $O(n + m)$ and output storage is $O(z + 1)$ for $z$ returned indices ($z = n + 1$ when $m = 0$). Time complexity is $O(n \cdot m + n + 1)$, and auxiliary memory is $O(1)$ (only scalar loop variables).
- **Boundary/counterexample test (`S10-naive-overlap-case-punct`):** `text = "a!a!a!A!a!a"`, `pattern = "a!a"` returns `positions = [0, 2, 8]`. This detects off-by-one errors in the outer loop bound (`n - m` vs. `n - m + 1`), failure to allow overlapping matches (`0` and `2` overlap at index `2`), and improper case folding (`'A'` at index `6` must not match `'a'`).

### 5. `kmp` — Exact Pattern Search (Knuth–Morris–Pratt)

- **State and index meaning:**
  - Prefix function array `pi[0..m-1]`: for $0 \le i < m$, `pi[i]` is the length of the longest **proper** prefix of `pattern[0..i]` that is also a suffix of `pattern[0..i]`.
  - Automaton state `q` ($0 \le q \le m$) during text scan at text index $i \in [0, n - 1]$: `q` is the length of the longest prefix of `pattern` that is a suffix of `text[0..i]`.
- **Base cases and transitions:**
  - If $m = 0$, return `list(range(n + 1))`; if $m > n$, return `[]`.
  - Prefix table base case: `pi[0] = 0`. For $i = 1 \dots m - 1$ with candidate border length $k = \text{pi}[i-1]$: while $k > 0$ and `pattern[k] != pattern[i]`, set $k \leftarrow \text{pi}[k - 1]$; then if `pattern[k] == pattern[i]`, increment $k \leftarrow k + 1$; set `pi[i] = k`.
  - Text scan update at $i = 0 \dots n - 1$ from state $q$: while $q > 0$ and `pattern[q] != text[i]`, fall back $q \leftarrow \text{pi}[q - 1]$; if `pattern[q] == text[i]`, set $q \leftarrow q + 1$; if $q == m$, record match start $i - m + 1$ and fall back $q \leftarrow \text{pi}[q - 1]$ to preserve overlapping matches.
- **Processing order and dependency readiness:** When computing `pi[i]`, every fallback accesses `pi[k - 1]` with $k - 1 < i$, which is already computed. During the left-to-right scan of `text`, `pi[0..m-1]` is completely precomputed.
- **Correctness argument:** Any border of `pattern[0..i]` of length $> 0$ is obtained by extending a border of `pattern[0..i-1]` by `pattern[i]`. Since `pi` enumerates all border lengths of `pattern[0..i-1]` in strictly decreasing order ($k, \text{pi}[k-1], \dots$), the first border extensible by `pattern[i]` (or `text[i]` during search) is the longest possible valid prefix match. Falling back to `q = pi[m - 1]` after a full match retains the longest proper prefix of `pattern` that is a suffix of the current match, so no overlapping occurrence can be missed.
- **Time and memory complexity:** By amortized analysis with potential $\Phi = k$ (for `pi`) and $\Phi = q$ (for text scan), each `for` iteration increments $k$ or $q$ by at most $1$, while each `while` iteration decreases $k$ or $q$ by at least $1$ and keeps $k, q \ge 0$. Hence the `while` loops execute at most $m$ and $n$ times in total. Time complexity is $O(n + m + z + 1)$, auxiliary memory is $O(m + 1)$ for `pi`, and output memory is $O(z + 1)$.
- **Boundary/counterexample test (`S11-kmp-overlap-case-punct`):** `text = "a!a!a!A!a!a"`, `pattern = "a!a"` returns `[0, 2, 8]`, verifying that after matching `"a!a"` at `i = 2` (start `0`), KMP transitions to `q = pi[2] = 1` (`"a"`) rather than resetting `q = 0`, thereby catching the overlapping match at start `2`.

### 6. `rk` — Exact Pattern Search (Rabin–Karp with Base 31, Modulus 101)

- **State and index meaning:** For $1 \le m \le n$, `p_hash` is the polynomial fingerprint of `pattern[0..m-1]` and `w_hash` at window start $i \in [0, n - m]$ is the fingerprint of `text[i..i+m-1]`:
  $$H(S[0..m-1]) = \left(\sum_{j=0}^{m-1} \text{ord}(S[j]) \cdot 31^{m - 1 - j}\right) \bmod 101,$$
  where the leftmost character carries the highest power `high_pow` $= 31^{m-1} \bmod 101$.
- **Base cases and transitions:**
  - Handle $m = 0$ (`list(range(n + 1))`) and $m > n$ (`[]`) before forming any hash window.
  - Initial hashes (`i = 0`): computed by Horner's rule over $j = 0 \dots m - 1$: `h = (h * 31 + ord(c)) % 101`.
  - Rolling update from window $i$ to $i + 1$ (for $i < n - m$):
    $$w_{\text{next}} = \bigl((w_{\text{curr}} - \text{ord}(\text{text}[i]) \cdot \text{high\_pow}) \cdot 31 + \text{ord}(\text{text}[i + m])\bigr) \bmod 101,$$
    normalizing negative remainders into $[0, 100]$.
- **Processing order and dependency readiness:** `high_pow` and the initial window hash at $i = 0$ are computed in $O(m)$ time first. Then windows slide sequentially from $i = 0$ to $n - m$, where each `w_hash` at $i + 1$ depends only on `w_hash` at $i$, outgoing character `text[i]`, and incoming character `text[i + m]`.
- **Correctness argument:** Because arithmetic modulo $101$ is a ring homomorphism, any true match `text[i..i+m-1] == pattern` is guaranteed to satisfy `w_hash == p_hash` (zero false negatives). Because $101$ is small, distinct strings can collide (`w_hash == p_hash` when substrings differ); therefore, every equal-hash candidate is explicitly verified character-by-character across $j = 0 \dots m - 1$ before appending $i$ (zero false positives).
- **Time and memory complexity:** Input storage is $O(n + m)$ and output storage is $O(z + 1)$. Auxiliary memory is $O(1)$ (scalar 64-bit-safe integers for rolling state). Let $c$ be the number of equal-hash candidate windows ($z \le c \le n - m + 1$). For $1 \le m \le n$, time complexity is candidate-sensitive: $O(n + m + c \cdot m)$, which is $O(n \cdot m + n + m + 1)$ across all permitted inputs (and quadratic when $c = \Theta(n)$).
- **Boundary/counterexample test (`S12-rk-collision-and-neg-mod`):** `text = "~!abdjab"`, `pattern = "ab"` returns `positions = [2, 6]`. With base $31$ and modulus $101$, `"ab"` has hash $(97 \cdot 31 + 98) \bmod 101 = 3105 \bmod 101 = 75$, and `"dj"` at index $4$ also has hash $(100 \cdot 31 + 106) \bmod 101 = 3206 \bmod 101 = 75$. In addition, rolling out `'~'` (ASCII $126$) produces a negative intermediate value before modulo normalization. This test catches both missing collision verification (which would falsely report index $4$) and faulty negative remainder handling.

### 7. `suffix` — Suffix Array (Prefix Doubling) and Kasai LCP

- **State and index meaning:**
  - **Prefix Doubling:** For nonempty `text` of length $n$, in round $k = 1, 2, 4, \dots < n$, `rank[i]` ($1 \le \text{rank}[i] \le n$) is the 1-based lexicographical equivalence rank of the $k$-prefix `text[i : min(n, i + k)]`. Each suffix $i \in [0, n - 1]$ is ordered by the rank pair $(\text{rank}[i],\, \text{rank}[i + k])$ where $\text{rank}[i + k] = 0$ if $i + k \ge n$ (representing exhaustion of the suffix without adding a sentinel character to the output).
  - **Kasai LCP:** `sa[0..n-1]` is the sorted permutation of suffix starts, `pos[i]` is the inverse permutation (`pos[sa[r]] = r`), and for $r \ge 1$, `lcp[r]` is the length of the longest common prefix of adjacent sorted suffixes `sa[r - 1]` and `sa[r]` (with `lcp[0] = 0`).
- **Base cases and transitions:**
  - Empty text ($n = 0$): return `sa = [], lcp = [], repeated = ""`. Single character ($n = 1$): return `sa = [0], lcp = [0], repeated = ""`.
  - Doubling initialization: `sa = [0, ..., n-1]` and `rank[i] = ord(text[i])`. In each step $k$, pack the pair `(rank[i], rank[i + k] if i + k < n else 0)` into a single integer key `(rank[i] << 20) | r2` (valid since $n \le 50{,}000 < 2^{20}$), sort `sa` by `key`, and assign new 1-based ranks `1..r` by scanning `sa` and incrementing $r$ whenever `key[sa[t]] != key[sa[t-1]]`. Stop early as soon as $r = n$.
  - Kasai update: maintain matched prefix length $h$ (initially $0$). For text position $i = 0 \dots n - 1$ with rank $r = \text{pos}[i] > 0$ and predecessor $j = \text{sa}[r - 1]$, increment $h$ while $i + h < n$, $j + h < n$, and `text[i + h] == text[j + h]`; set `lcp[r] = h`, and then update $h \leftarrow \max(0, h - 1)$ for step $i + 1$.
- **Processing order and dependency readiness:**
  - In prefix doubling, round $2k$ uses `rank` values from round $k$ because a $2k$-prefix is the concatenation of two $k$-prefixes at $i$ and $i + k$.
  - In Kasai's algorithm, suffixes are processed in text order $i = 0, 1, \dots, n - 1$ rather than `sa` order so that the lower bound $\text{LCP}(\text{sa}[\text{pos}[i+1]-1],\, i+1) \ge \text{LCP}(\text{sa}[\text{pos}[i]-1],\, i) - 1$ is available from the previous iteration.
- **Correctness argument:**
  - *Prefix Doubling:* By induction on $k = 2^t$, two suffixes have equal rank after step $k$ iff their $k$-prefixes are identical, and a smaller rank iff their $k$-prefix is lexicographically smaller (with `0` correctly ordering shorter suffixes before longer extensions). Once all ranks are distinct ($r = n$) or $k \ge n$, `sa` is the unique lexicographical suffix order.
  - *Kasai LCP:* If suffix $i$ shares $h \ge 1$ characters with its predecessor $j = \text{sa}[\text{pos}[i] - 1]$, then suffix $i + 1$ shares at least $h - 1$ characters with $j + 1$, which precedes $i + 1$ in `sa`. Since LCP across sorted intervals equals the minimum adjacent LCP, the immediate predecessor $\text{sa}[\text{pos}[i+1] - 1]$ of $i + 1$ shares at least $h - 1$ characters with $i + 1$, justifying starting comparisons at offset $h - 1$.
- **Reconstruction and tie handling (Longest Repeated Substring):** Any substring occurring at two distinct start positions $p \ne q$ is a common prefix of suffixes $p$ and $q$. In sorted suffix order, $\text{LCP}(p, q) = \min_{\text{pos}[p] < r \le \text{pos}[q]} \text{lcp}[r] \le \max_{1 \le r < n} \text{lcp}[r]$. Thus the maximum value in `lcp[1..n-1]` equals the length of a longest repeated substring (including overlaps). We select the first index $r$ maximizing `lcp[r]` and return `text[sa[r] : sa[r] + lcp[r]]` (or `""` if $\max(\text{lcp}) = 0$).
- **Time and memory complexity:**
  - *Doubling:* At most $\lceil \log_2 n \rceil \le 16$ rounds; each round sorts $n$ packed integer keys using Python's Timsort in $O(n \log n)$ time, giving $O(n \log^2(n + 1))$ worst-case time.
  - *Kasai:* $h$ decreases at most $n$ times (by at most $1$ per $i$) and never exceeds $n$, so $h$ increments at most $2n$ times; Kasai runs in $O(n)$ time.
  - *Memory:* Input is $O(n)$, output (`sa`, `lcp`, `repeated`) is $O(n + 1)$, and auxiliary arrays (`rank`, `new_rank`, `key`, `pos`) take $O(n + 1)$ memory without materializing suffix strings.
- **Boundary/counterexample test (`S15-suffix-low-ascii-no-sentinel`):** `text = " ! !"` (ASCII $32$ `' '` and $33$ `'!'`) returns `sa = [2, 0, 3, 1], lcp = [0, 2, 0, 1], repeated = " !"`. Implementations that append a `'$'` sentinel (ASCII $36$) place `'$'` *after* `' '` ($32$) and `'!'` ($33$), corrupting the suffix order of `" !"` vs. `" ! !"`.

### 8. `aho` — Dictionary Automaton (Aho–Corasick with Reverse-Failure Propagation)

- **State and index meaning:**
  - `trie[u]` maps character `ch` to child state $v$ for state $u \in \{0, \dots, S-1\}$ ($0$ is the root representing `""`).
  - `pat_node[idx]` ($0 \le \text{idx} < p$) stores the terminal trie state reached by dictionary pattern `patterns[idx]`. Duplicate patterns naturally point to the same terminal state `u`.
  - `fail[u]` is the longest proper suffix of the string of state $u$ that is also a prefix in the trie.
  - For each text, `visits[u]` counts how many times state $u$ is entered during the text scan, and after reverse-BFS propagation stores the total number of text positions where state $u$'s string occurs as a suffix.
- **Base cases and transitions:**
  - If `texts == []`, return `{"counts": []}`. If `patterns == []`, return `{"counts": [[] for _ in texts]}`.
  - Trie construction: insert each pattern `patterns[idx]` from root $0$ and set `pat_node[idx] = u`.
  - Failure-link BFS: for depth-1 children $v$ of root $0$, `fail[v] = 0`. For each state $u$ popped in BFS order and each trie edge $(c, v)$ from $u$, walk $f \leftarrow \text{fail}[u]$ via $f \leftarrow \text{fail}[f]$ while $f > 0$ and $c \notin \text{trie}[f]$, then set `fail[v] = trie[f].get(c, 0)`.
  - Per-text scan & propagation: reset `state = 0` and `visits = [0] * S`. For each character $c$ of `text`, walk `state = fail[state]` while `state > 0` and $c \notin \text{trie}[\text{state}]$, advance `state = trie[state].get(c, 0)`, and increment `visits[state] += 1`. After scanning `text`, iterate $v$ in `reversed(bfs_order)` and update `visits[fail[v]] += visits[v]`. Emit `[visits[u] for u in pat_node]`.
- **Processing order and dependency readiness:**
  - BFS order visits states in non-decreasing depth. Since `depth(fail[u]) < depth(u)` for all $u > 0$, all failure links at smaller depths are ready when computing `fail[v]`.
  - Reversing `bfs_order` visits states in non-increasing depth, so every state $v$ finishes accumulating counts from its failure-tree descendants before adding `visits[v]` into its parent `fail[v]`.
- **Correctness argument:** After reading prefix `text[0..j]`, the automaton is at the state $s_j$ corresponding to the longest trie prefix that is a suffix of `text[0..j]`. Every dictionary pattern that ends at position $j$ is a suffix of $s_j$ and therefore corresponds to an ancestor of $s_j$ in the failure-link tree. Adding $1$ to `visits[s_j]` for each $j$ and summing subtree weights bottom-up along `fail` links (`visits[fail[v]] += visits[v]`) computes for every trie state $u$ the exact number of indices $j$ where $u$ is a failure-ancestor of $s_j$. Looking up `visits[pat_node[idx]]` then gives the exact occurrence count for every dictionary entry `idx`, handling suffix patterns, overlaps, and duplicates without per-match output-link loops.
- **Time and memory complexity:** Let $L = \sum |\text{patterns}[i]|$, $p = |\text{patterns}|$, $S \le L + 1$ trie states, $q = |\text{texts}|$, and $T = \sum |\text{texts}[r]|$. By the depth potential argument ($\Phi = \text{depth}(\text{state})$), both failure-link construction across the trie and text scanning across each text perform at most $L$ and $|\text{text}|$ failure steps respectively. Construction takes $O(L + S + p)$ time and $O(S + p)$ auxiliary memory (well within the permitted $O(L + 95S + p)$ bound), and each independent text takes $O(|\text{text}| + S + p)$ time, for $O(L + T + q(S + p) + 1)$ total time and $O(q(p + 1) + 1)$ output memory.
- **Boundary/counterexample test (`S16-aho-ushers-duplicates-reset`):** `patterns = ["ushers", "she", "he", "hers", "he"]`, `texts = ["ushers", "", "shehe"]` returns `counts = [[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 1, 2, 0, 2]]`. This verifies that embedded suffix pattern `"he"` is counted when `"she"` matches at indices $1..3$, duplicate pattern `"he"` at indices $2$ and $4$ receives identical counts, empty text returns zeros, and `visits`/`state` are cleanly reset between texts.

## Own tests

All 16 custom cases are stored in `tests/student/student_tests.jsonl` and executed via `python3 tools/run.py --input tests/student/student_tests.jsonl`.

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|`lcs`|`tests/student/student_tests.jsonl` line 1: `{"task":"lcs","a":"","b":""}`|`{"length":0,"sequence":""}`|`{"length":0,"sequence":""}` (PASS)|Both strings empty; detects missing base case or out-of-bounds indexing at `(0,0)`.|
|`lcs`|`tests/student/student_tests.jsonl` line 2: `{"task":"lcs","a":"abacaba","b":"babbca"}`|`{"length":4,"sequence":"abca"}`|`{"length":4,"sequence":"abca"}` (PASS)|Non-contiguous subsequence with repeated characters (tied with `"baba"`); detects substring-only logic or character reuse.|
|`lcs`|`tests/student/student_tests.jsonl` line 3: `{"task":"lcs","a":"XYZW","b":"WZYX"}`|`{"length":1,"sequence":"X"}`|`{"length":1,"sequence":"X"}` (PASS)|Four tied optimal LCS witnesses of length 1 (`"X"`,`"Y"`,`"Z"`,`"W"`); verifies deterministic tie handling during backtracking.|
|`merge`|`tests/student/student_tests.jsonl` line 4: `{"task":"merge","sizes":[42]}`|`{"cost":0,"plan":[]}`|`{"cost":0,"plan":[]}` (PASS)|Single block `n=1`; detects invalid merge emission or non-zero cost when no merges are needed.|
|`merge`|`tests/student/student_tests.jsonl` line 5: `{"task":"merge","sizes":[10,1,10,1]}`|`{"cost":44,"plan":[[0,0,1],[2,2,3],[0,1,3]]}`|`{"cost":44,"plan":[[0,0,1],[2,2,3],[0,1,3]]}` (PASS)|Balanced interval split vs. non-adjacent greedy merge; verifies child-before-parent postorder plan.|
|`merge`|`tests/student/student_tests.jsonl` line 6: `{"task":"merge","sizes":[1000000000,0,1000000000,1000000000]}`|`{"cost":6000000000,"plan":[[1,1,2],[1,2,3],[0,0,3]]}`|`{"cost":6000000000,"plan":[[1,1,2],[1,2,3],[0,0,3]]}` (PASS)|Zero-sized block mixed with `10^9` sizes; detects 32-bit signed integer overflow and zero-cost split bugs.|
|`tree`|`tests/student/student_tests.jsonl` line 7: `{"task":"tree","n":1,"weights":[-7],"edges":[]}`|`{"weight":0,"selected":[]}`|`{"weight":0,"selected":[]}` (PASS)|Single negative vertex; detects failure to permit the empty independent set (`weight=0`).|
|`tree`|`tests/student/student_tests.jsonl` line 8: `{"task":"tree","n":4,"weights":[10,8,8,8],"edges":[[0,1],[0,2],[0,3]]}`|`{"weight":24,"selected":[1,2,3]}`|`{"weight":24,"selected":[1,2,3]}` (PASS)|Star graph where skipping heavy root (`10`) yields higher leaf sum (`24`); detects greedy root selection.|
|`tree`|`tests/student/student_tests.jsonl` line 9: `{"task":"tree","n":5,"weights":[1000000000,900000000,-50,0,1000000000],"edges":[[0,1],[1,2],[2,3],[3,4]]}`|`{"weight":2000000000,"selected":[0,4]}`|`{"weight":2000000000,"selected":[0,4]}` (PASS)|Chain with `10^9`, negative, and zero weights; detects 32-bit overflow, forced zero/negative picks, and adjacency bugs.|
|`naive`|`tests/student/student_tests.jsonl` line 10: `{"task":"naive","text":"a!a!a!A!a!a","pattern":"a!a"}`|`{"positions":[0,2,8]}`|`{"positions":[0,2,8]}` (PASS)|Overlapping occurrences with punctuation and case sensitivity; detects off-by-one at last start `n-m`.|
|`kmp`|`tests/student/student_tests.jsonl` line 11: `{"task":"kmp","text":"a!a!a!A!a!a","pattern":"a!a"}`|`{"positions":[0,2,8]}`|`{"positions":[0,2,8]}` (PASS)|Identical input to S10 for KMP; verifies prefix fallback `q = pi[q-1]` after full match and case sensitivity.|
|`rk`|`tests/student/student_tests.jsonl` line 12: `{"task":"rk","text":"~!abdjab","pattern":"ab"}`|`{"positions":[2,6]}`|`{"positions":[2,6]}` (PASS)|Spurious collision (`"ab"` and `"dj"` both hash to `75 mod 101`) plus high-ASCII `'~'` (`126`) rolling removal.|
|`suffix`|`tests/student/student_tests.jsonl` line 13: `{"task":"suffix","text":"dcba"}`|`{"sa":[3,2,1,0],"lcp":[0,0,0,0],"repeated":""}`|`{"sa":[3,2,1,0],"lcp":[0,0,0,0],"repeated":""}` (PASS)|Strictly decreasing distinct characters; verifies all-zero LCP and empty repeated string.|
|`suffix`|`tests/student/student_tests.jsonl` line 14: `{"task":"suffix","text":"ababa"}`|`{"sa":[4,2,0,3,1],"lcp":[0,1,3,0,2],"repeated":"aba"}`|`{"sa":[4,2,0,3,1],"lcp":[0,1,3,0,2],"repeated":"aba"}` (PASS)|Overlapping longest repeat `"aba"` at indices `0` and `2`; verifies prefix-doubling tie-breaking and Kasai LCP.|
|`suffix`|`tests/student/student_tests.jsonl` line 15: `{"task":"suffix","text":" ! !"}`|`{"sa":[2,0,3,1],"lcp":[0,2,0,1],"repeated":" !"}`|`{"sa":[2,0,3,1],"lcp":[0,2,0,1],"repeated":" !"}` (PASS)|ASCII `32` (`' '`) and `33` (`'!'`) below `'$'` (`36`); detects illegal `'$'` sentinel that inverts suffix order.|
|`aho`|`tests/student/student_tests.jsonl` line 16: `{"task":"aho","patterns":["ushers","she","he","hers","he"],"texts":["ushers","","shehe"]}`|`{"counts":[[1,1,1,1,1],[0,0,0,0,0],[0,1,2,0,2]]}`|`{"counts":[[1,1,1,1,1],[0,0,0,0,0],[0,1,2,0,2]]}` (PASS)|Suffix-pattern matches (`"he"` inside `"she"`/`"ushers"`), duplicate dictionary entries, and state reset across texts.|

## Search comparison

- **Methodology and timing scope:**
  - Reproducible script: `python3 tests/student/benchmark_search.py`.
  - Three increasing input sizes within the common domain ($n, m \le 3000$): $(n, m) \in \{(1000, 200),\, (2000, 400),\, (3000, 600)\}$.
  - **Random distribution:** Uniformly sampled characters from the 4-letter alphabet `"ABCD"` using `random.Random(20261104 + idx)` (`idx = 0, 1, 2`).
  - **Repetitive distribution:** Deterministic unary strings `text = "a" * n` and `pattern = "a" * m`, where every window $i \in [0, n - m]$ is an overlapping match ($801$, $1601$, and $2401$ matches respectively).
  - **Correctness check before timing:** Prior to timing, the script verifies that `naive`, `kmp`, and `rk` return identical `positions` lists on all benchmark inputs as well as on the known collision pairs `("abdj", "ab") -> [0]` and `("bcek", "bc") -> [0]`.
  - **Timing boundary & warm-up policy:** Timing measures only the in-memory algorithm call `fn(req)` (after JSON parsing and module import) using `time.perf_counter_ns()`, converted to milliseconds (`ms`). Each algorithm executes `2` untimed warm-up runs followed by `5` measured runs per case; both raw times and the median are reported below.

|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Run 4 (ms)|Run 5 (ms)|Median (ms)|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|
|Random (uniform `'ABCD'`)|1000|200|`random.Random(20261104)` over `'ABCD'`|`naive`|0.098|0.098|0.097|0.098|0.098|0.098|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|1000|200|`random.Random(20261104)` over `'ABCD'`|`kmp`|0.086|0.077|0.084|0.076|0.076|0.077|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|1000|200|`random.Random(20261104)` over `'ABCD'`|`rk`|0.110|0.110|0.110|0.116|0.111|0.110|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|2000|400|`random.Random(20261105)` over `'ABCD'`|`naive`|0.218|0.217|0.217|0.222|0.225|0.218|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|2000|400|`random.Random(20261105)` over `'ABCD'`|`kmp`|0.151|0.150|0.156|0.158|0.150|0.151|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|2000|400|`random.Random(20261105)` over `'ABCD'`|`rk`|0.215|0.214|0.211|0.211|0.210|0.211|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|3000|600|`random.Random(20261106)` over `'ABCD'`|`naive`|0.306|0.311|0.310|0.303|0.302|0.306|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|3000|600|`random.Random(20261106)` over `'ABCD'`|`kmp`|0.216|0.216|0.221|0.207|0.197|0.216|Yes (0 matches; `naive==kmp==rk`)|
|Random (uniform `'ABCD'`)|3000|600|`random.Random(20261106)` over `'ABCD'`|`rk`|0.290|0.283|0.272|0.276|0.312|0.283|Yes (0 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|1000|200|deterministic `'a'*n, 'a'*m`|`naive`|5.752|5.450|5.783|5.605|5.101|5.605|Yes (801 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|1000|200|deterministic `'a'*n, 'a'*m`|`kmp`|0.087|0.089|0.087|0.089|0.086|0.087|Yes (801 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|1000|200|deterministic `'a'*n, 'a'*m`|`rk`|5.386|5.539|5.914|5.650|5.799|5.650|Yes (801 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|2000|400|deterministic `'a'*n, 'a'*m`|`naive`|23.322|23.702|23.603|22.603|23.754|23.603|Yes (1601 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|2000|400|deterministic `'a'*n, 'a'*m`|`kmp`|0.224|0.228|0.222|0.222|0.230|0.224|Yes (1601 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|2000|400|deterministic `'a'*n, 'a'*m`|`rk`|24.097|23.303|23.793|23.193|24.436|23.793|Yes (1601 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|3000|600|deterministic `'a'*n, 'a'*m`|`naive`|55.433|54.940|54.370|54.761|53.402|54.761|Yes (2401 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|3000|600|deterministic `'a'*n, 'a'*m`|`kmp`|0.334|0.345|0.339|0.341|0.341|0.341|Yes (2401 matches; `naive==kmp==rk`)|
|Repetitive (`'a'^n` vs `'a'^m`)|3000|600|deterministic `'a'*n, 'a'*m`|`rk`|53.870|55.015|53.870|55.164|53.898|53.898|Yes (2401 matches; `naive==kmp==rk`)|

- **Discussion of observations and modulus 101:**
  - *Empirical timings vs. asymptotic proof:* Empirical wall-clock medians reflect interpreter loop overhead, branch prediction, and memory access patterns on finite inputs rather than a mathematical proof of asymptotic complexity.
  - *Random inputs:* On uniform `'ABCD'` strings, all three methods exhibit near-linear scaling (`0.098 -> 0.218 -> 0.306 ms` for `naive`, `0.077 -> 0.151 -> 0.216 ms` for `kmp`, and `0.110 -> 0.211 -> 0.283 ms` for `rk`). In `naive`, the inner loop mismatches on the first character with probability $3/4$, performing only $\approx 4/3$ character comparisons per window on average.
  - *Repetitive inputs:* On `'a'^n` vs. `'a'^m`, `kmp` maintains linear scaling (`0.087 -> 0.224 -> 0.341 ms`) because `q = pi[m - 1] = m - 1` transitions in $O(1)$ amortized work after each match. By contrast, both `naive` (`5.605 -> 23.603 -> 54.761 ms`) and exact `rk` (`5.650 -> 23.793 -> 53.898 ms`) scale quadratically ($\approx 4.2\times$ when doubling and $\approx 9.7\times$ when tripling $n$ and $m$) because all $c = n - m + 1$ windows share the pattern hash and require $m$-character verification ($O(n + m + c \cdot m)$).
  - *Effect of modulus 101:* The specification intentionally chooses a tiny prime modulus $\text{mod} = 101$ so hash collisions occur frequently ($\approx 1/101$ of random windows) and can be deterministically tested (e.g., `"ab"` and `"dj"` both hash to $75 \bmod 101$, and `"bc"` and `"ek"` both hash to $76 \bmod 101$). This collision frequency is specific to this didactic laboratory setup and does not generalize to production rolling-hash systems, which typically use large 61-bit/64-bit primes (such as $2^{61}-1$) or randomized double hashing to reduce spurious collision rates below $10^{-18}$, though exact verification is still required whenever a zero-false-positive guarantee is mandated.

## Sources and AI assistance

- **Course materials used:** Week 8–10 lecture notes on Dynamic Programming (prefix, interval, and tree DP), Knuth–Morris–Pratt and polynomial rolling hashes, and Suffix Arrays / Kasai LCP / Aho–Corasick (`docs/Assignment_4_EN.md`, `docs/guide/CONTRACTS.md`, `docs/LECTURE_CLARIFICATIONS_EN_RU.md`).
- **AI assistance disclosure:** An AI assistant (Gemini) assisted in drafting the explanations in `ANALYSIS.md`.
- **Verification performed:** Every implementation was verified against all 44 public test cases and the two-batch state-reset check (`python3 tools/run.py --check`), validated against 16 targeted boundary/counterexample cases (`python3 tools/run.py --input tests/student/student_tests.jsonl`), stress-tested at the maximum published domain limits (`|a|=|b|=1000` for `lcs`, `n=200` for `merge`, `n=100,000` chain for `tree`, `n=200,000, m=100,000` for `kmp`, `n=50,000` for `suffix`, and `p=10,000, T=200,000` for `aho`), and cross-checked across `naive`, `kmp`, and `rk` in `benchmark_search.py`.
