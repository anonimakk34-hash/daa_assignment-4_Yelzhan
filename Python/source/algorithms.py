"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""

from collections import deque


def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters.

    Implement lcs according to docs/guide/CONTRACTS.md.
    Prefix DP state: dp[i][j] = length of LCS of a[:i] and b[:j].
    Time: O((|a| + 1)(|b| + 1)), Auxiliary Memory: O((|a| + 1)(|b| + 1)).
    """
    a = request["a"]
    b = request["b"]
    m = len(a)
    n = len(b)
    if m == 0 or n == 0:
        return {"length": 0, "sequence": ""}

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        ai = a[i - 1]
        row = dp[i]
        prev = dp[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                up = prev[j]
                left = row[j - 1]
                row[j] = up if up >= left else left

    # Reconstruct one optimal LCS by backtracking from (m, n) to (0, 0).
    i = m
    j = n
    chars = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            chars.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    chars.reverse()
    return {"length": dp[m][n], "sequence": "".join(chars)}


def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved.

    Implement merge according to docs/guide/CONTRACTS.md.
    Interval DP state: dp[l][r] = minimum cost to merge blocks l..r into [l, r].
    Time: O(n^3) for n >= 1 (O(1) for n == 0), Auxiliary Memory: O(n^2).
    """
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}

    # Prefix sums for O(1) interval weight queries: sum(sizes[l : r + 1]) = pref[r + 1] - pref[l]
    pref = [0] * (n + 1)
    for i in range(n):
        pref[i + 1] = pref[i] + sizes[i]

    dp = [[0] * n for _ in range(n)]
    # Transposed DP table dp_col[r][k + 1] == dp[k + 1][r] for fast row-contiguous inner loops
    dp_col = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            w = pref[r + 1] - pref[l]
            dp_l = dp[l]
            col_r = dp_col[r]
            best = dp_l[l] + col_r[l + 1]
            best_k = l
            for k in range(l + 1, r):
                cand = dp_l[k] + col_r[k + 1]
                if cand < best:
                    best = cand
                    best_k = k
            total = best + w
            dp_l[r] = total
            col_r[l] = total
            split[l][r] = best_k

    # Reconstruct merge plan in postorder (children merged before parent interval)
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        l, r, visited = stack.pop()
        if l >= r:
            continue
        k = split[l][r]
        if visited:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))

    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree.

    Implement tree according to docs/guide/CONTRACTS.md.
    Iterative take/skip tree DP rooted at 0 using BFS topological order.
    Time: O(n + 1), Auxiliary Memory: O(n + 1).
    """
    n = request["n"]
    weights = request["weights"]
    edges = request["edges"]
    if n == 0:
        return {"weight": 0, "selected": []}
    if n == 1:
        if weights[0] > 0:
            return {"weight": weights[0], "selected": [0]}
        return {"weight": 0, "selected": []}

    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Root at vertex 0 and build BFS order so reversed(order) is a valid postorder
    parent = [-1] * n
    visited = [False] * n
    visited[0] = True
    order = [0]
    idx = 0
    while idx < len(order):
        u = order[idx]
        idx += 1
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                order.append(v)

    take = list(weights)
    skip = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p != -1:
            su = skip[u]
            tu = take[u]
            skip[p] += tu if tu > su else su
            take[p] += su

    # Top-down reconstruction respecting parent selection constraint
    chosen = [False] * n
    selected = []
    for u in order:
        p = parent[u]
        if (p == -1 or not chosen[p]) and take[u] > skip[u]:
            chosen[u] = True
            selected.append(u)

    opt_weight = take[0] if take[0] > skip[0] else skip[0]
    return {"weight": opt_weight, "selected": selected}


def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked.

    Implement naive according to docs/guide/CONTRACTS.md.
    Time: O(n * m + n + 1), Auxiliary Memory: O(1), Output Memory: O(z + 1).
    """
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    positions = []
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)

    return {"positions": positions}


def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch.

    Implement kmp according to docs/guide/CONTRACTS.md.
    Time: O(n + m + z + 1), Auxiliary Memory: O(m + 1), Output Memory: O(z + 1).
    """
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    # Compute prefix function pi[0..m-1]
    pi = [0] * m
    k = 0
    for i in range(1, m):
        ch = pattern[i]
        while k > 0 and pattern[k] != ch:
            k = pi[k - 1]
        if pattern[k] == ch:
            k += 1
        pi[i] = k

    # Scan text using prefix fallback
    positions = []
    q = 0
    for i in range(n):
        ch = text[i]
        while q > 0 and pattern[q] != ch:
            q = pi[q - 1]
        if pattern[q] == ch:
            q += 1
            if q == m:
                positions.append(i - m + 1)
                q = pi[q - 1]

    return {"positions": positions}


def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate.

    Implement rk according to docs/guide/CONTRACTS.md.
    Polynomial rolling hash with base 31 and modulus 101.
    Time: O(n + m + c * m) for 1 <= m <= n, Auxiliary Memory: O(1) beyond input/output.
    """
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    base = 31
    mod = 101
    high_pow = 1
    for _ in range(m - 1):
        high_pow = (high_pow * base) % mod

    p_hash = 0
    w_hash = 0
    for j in range(m):
        p_hash = (p_hash * base + ord(pattern[j])) % mod
        w_hash = (w_hash * base + ord(text[j])) % mod

    positions = []
    limit = n - m
    for i in range(limit + 1):
        if w_hash == p_hash:
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                positions.append(i)
        if i < limit:
            w_hash = ((w_hash - ord(text[i]) * high_pow) * base + ord(text[i + m])) % mod
            if w_hash < 0:
                w_hash += mod

    return {"positions": positions}


def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings.

    Implement suffix according to docs/guide/CONTRACTS.md.
    Prefix doubling suffix array construction + Kasai LCP algorithm.
    Time: O(n log^2(n + 1)) for doubling + O(n) for Kasai, Auxiliary Memory: O(n + 1).
    """
    text = request["text"]
    n = len(text)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}
    if n == 1:
        return {"sa": [0], "lcp": [0], "repeated": ""}

    # Prefix doubling without sentinel; 1-based ranks so out-of-bounds second half has rank 0
    sa = list(range(n))
    rank = [ord(c) for c in text]
    key = [0] * n
    new_rank = [0] * n
    shift = 20  # 2^20 > 50000, packs (rank[i], rank[i + k]) into one integer

    k = 1
    while k < n:
        for i in range(n - k):
            key[i] = (rank[i] << shift) | rank[i + k]
        for i in range(n - k, n):
            key[i] = rank[i] << shift

        sa.sort(key=key.__getitem__)

        r = 1
        first = sa[0]
        new_rank[first] = 1
        prev_key = key[first]
        for idx in sa[1:]:
            cur_key = key[idx]
            if cur_key != prev_key:
                r += 1
                prev_key = cur_key
            new_rank[idx] = r

        rank, new_rank = new_rank, rank
        if r == n:
            break
        k <<= 1

    # Kasai's algorithm for adjacent LCP in O(n) time
    pos = [0] * n
    for idx, s in enumerate(sa):
        pos[s] = idx

    lcp = [0] * n
    h = 0
    for i in range(n):
        r = pos[i]
        if r > 0:
            j = sa[r - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[r] = h
            if h > 0:
                h -= 1
        else:
            h = 0

    max_len = 0
    best_sa_idx = 0
    for r in range(1, n):
        if lcp[r] > max_len:
            max_len = lcp[r]
            best_sa_idx = sa[r]

    repeated = text[best_sa_idx : best_sa_idx + max_len] if max_len > 0 else ""
    return {"sa": sa, "lcp": lcp, "repeated": repeated}


def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts.

    Implement aho according to docs/guide/CONTRACTS.md.
    Aho-Corasick trie with failure links and reverse-BFS visit propagation per text.
    """
    patterns = request["patterns"]
    texts = request["texts"]
    p = len(patterns)
    q = len(texts)
    if q == 0:
        return {"counts": []}
    if p == 0:
        return {"counts": [[] for _ in range(q)]}

    # Build trie; duplicate patterns share the same terminal trie state
    trie = [{}]
    pat_node = [0] * p
    for idx, pat in enumerate(patterns):
        u = 0
        for ch in pat:
            nxt = trie[u].get(ch)
            if nxt is None:
                nxt = len(trie)
                trie[u][ch] = nxt
                trie.append({})
            u = nxt
        pat_node[idx] = u

    num_states = len(trie)
    fail = [0] * num_states
    bfs_order = []
    queue = deque()

    for ch, v in trie[0].items():
        fail[v] = 0
        queue.append(v)
        bfs_order.append(v)

    while queue:
        u = queue.popleft()
        fu = fail[u]
        for ch, v in trie[u].items():
            f = fu
            while f and ch not in trie[f]:
                f = fail[f]
            fail[v] = trie[f].get(ch, 0)
            queue.append(v)
            bfs_order.append(v)

    rev_bfs = list(reversed(bfs_order))
    counts = []
    for text in texts:
        if not text:
            counts.append([0] * p)
            continue
        visits = [0] * num_states
        state = 0
        for ch in text:
            while state and ch not in trie[state]:
                state = fail[state]
            state = trie[state].get(ch, 0)
            visits[state] += 1

        # Reverse-failure propagation aggregates suffix-pattern matches in O(S)
        for v in rev_bfs:
            visits[fail[v]] += visits[v]

        counts.append([visits[u] for u in pat_node])

    return {"counts": counts}
