# Code Security – Core Concepts & Bug Classes

This note is prepared to give a compact view of core security concepts and common bug classes, plus short vulnerable snippets to make the static analysis findings easier to understand.

---

### CIA Triad (High-Level View)

- **Confidentiality** – Only authorized parties can access sensitive data.
- **Integrity** – Data and system behavior remain accurate and unaltered except by authorized actions.
- **Availability** – Authorized users can reliably access systems and data when needed.

---

#### Static Analysis & False Positives

- **Static analysis**: Automated checking of source code without running it, to spot potential bugs, security issues, and style problems early in development.
- **How it works (short)**: Tools parse code into structures (like syntax trees) and apply rules and patterns over data/control flow to find risky constructs.
- **Why false positives happen**: A rule sees a pattern that *could* be dangerous but doesn’t know all real inputs, configs, or calling context, so safe code can still be flagged.
- **Takeaway**: Treat each finding as a hypothesis, not a guaranteed bug; use surrounding code and real usage to decide “real issue vs noise.”

#### Static vs Dynamic Analysis (Very Short)

- **Static analysis**: Looks at code (or bytecode) without executing it, giving broad coverage early in the lifecycle but with more false positives and limited understanding of real runtime behavior.
- **Dynamic analysis**: Observes the program while it runs (tests, fuzzing, DAST), seeing actual inputs and states, which reduces false positives but only for the paths and scenarios that are exercised.
- **Takeaway**: Static analysis finds *potential* problems everywhere; dynamic analysis confirms problems on specific executions. Use both together when judging risk.

---

### Common Bug Classes

#### 1. Memory Safety Bugs

- **Definition**: Incorrect use of memory that leads to corruption, crashes, or unintended data access.
- **Examples**: Buffer overflow, out-of-bounds read/write, use-after-free, double free (especially relevant in C/C++ daemons like BIRD).
- **Impact**: Often leads to arbitrary code execution, info leaks, and privilege escalation.

<br>

`Buffer overflow`
- **Explanation**: Writing more data into a fixed-size buffer than it can hold, overwriting adjacent memory.
- **Impact**: Can let an attacker overwrite control data (like return addresses) and hijack execution for arbitrary code execution.
- **Snippet (C)**:
```c
void copy_name(const char *name) {
    char buf;[1]
    // VULNERABLE: no length check, 'name' can be longer than 15 chars
    strcpy(buf, name);
    printf("Hello %s\n", buf);
}
```

<br>

`Out-of-bounds read/write`
- **Explanation**: Accessing an array or buffer index outside its valid range (too low or too high), reading or writing unintended memory.
- **Impact**: Can leak sensitive data from nearby memory or corrupt data structures, leading to crashes or privilege escalation.
- **Snippet (C)**:
```c
void print_item(int *items, int count, int index) {
    // VULNERABLE: index not validated against [0, count)
    printf("Item: %d\n", items[index]);
}
```

<br>

`Use-after-free`
- **Explanation**: Using a pointer to memory after that memory has been freed, leading to reads/writes into invalid or reused memory.
- **Impact**: Attackers can cause the program to operate on attacker-controlled data by reallocating the freed region and then triggering the stale pointer access.
- **Snippet (C)**:
```c
void uaf_demo() {
    int *p = malloc(sizeof(int));
    *p = 42;
    free(p);
    // VULNERABLE: dereferencing 'p' after free
    printf("Value: %d\n", *p);
}
```

<br>

`Double free`
- **Explanation**: Calling `free` on the same pointer more than once, corrupting allocator state and potentially enabling exploitation.
- **Impact**: Can corrupt heap metadata, allowing attackers to manipulate future allocations and gain arbitrary write capabilities.
- **Snippet (C)**:
```c
void double_free_demo() {
    char *p = malloc(32);
    strcpy(p, "test");
    free(p);
    // VULNERABLE: freeing 'p' a second time
    free(p);
}
```

---

#### 2. Injection Bugs

- **Definition**: Untrusted input is interpreted as commands, format strings, or parameters that control external subsystems (shell, logging, packet filters, helper tools) inside a router or routing daemon.
- **Examples**: Shell/command injection via `system()` or `popen()`, format string injection in logging, config/CLI injection into helper utilities.
- **Impact**: Attackers can execute arbitrary commands on the router, leak sensitive memory, or change routing and firewall rules using the daemon’s privileges.

`Example – shell/command injection in a routing daemon`
```c
void apply_filter(const char *iface, const char *filter) {
    char cmd;

    // VULNERABLE: 'filter' can contain injected shell metacharacters
    snprintf(cmd, sizeof(cmd),
             "/sbin/iptables -A INPUT -i %s %s", iface, filter);

    system(cmd);
}
```
- **Impact**: If an attacker controls `filter` (e.g., via a management API or config file), they can append `; rm -rf /` or other commands, gaining remote code execution with the daemon’s privileges.

<br>

`Example – format string injection in router logging`
```c
#include <syslog.h>

void log_iface(const char *iface_name) {
    // VULNERABLE: user-controlled 'iface_name' used as format string
    syslog(LOG_INFO, iface_name);
}
```
- **Impact**: An attacker who controls `iface_name` can include `%x` or `%n` specifiers, causing the daemon to leak stack contents or corrupt memory, potentially leading to information disclosure or code execution.

---

#### 3. Authentication & Authorization Bugs

- **Definition**: Flaws in how a routing daemon verifies who is issuing commands (authentication) or whether they are allowed to perform specific operations (authorization).
- **Examples**: Unauthenticated management socket, shared/static credentials reused everywhere, missing privilege checks on commands that change routes or firewall rules.
- **Impact**: Attackers can connect to the daemon or management interface and read/modify routing state, filter rules, or sensitive config without proper rights.

`Example – missing authorization check for a management command (C)`
```c
struct client {
    int fd;
    int is_authenticated;
    int role; /* 0 = user, 1 = admin */
};

void handle_cmd(struct client *c, const char *cmd, const char *arg)
{
    if (strcmp(cmd, "show_routes") == 0) {
        /* SAFE-ish: read-only, allowed for all connected clients */
        dump_routes(c->fd);
    }
    else if (strcmp(cmd, "add_route") == 0) {
        /* VULNERABLE: no check on c->is_authenticated or c->role */
        add_route(arg);  /* e.g., "10.0.0.0/24 via 192.0.2.1" */
        send_ok(c->fd);
    }
}
```

- **What this can lead to**: Any client that connects to the management socket (even unauthenticated or low-privilege) can send `add_route` and inject arbitrary routes, potentially hijacking traffic, blackholing networks, or creating man-in-the-middle paths through attacker-controlled nodes.

---

#### 4. Logic & State Machine Flaws

- **Definition**: Vulnerabilities caused by wrong workflow or state transitions in the daemon’s control logic (session states, timers, command flows), not just by low-level API misuse.
- **Examples**: Race conditions between threads, accepting commands in the wrong state, replaying old messages because state isn’t tracked, failing to clear flags when a session resets.
- **Impact**: Can bring up sessions when they should be down, re-apply old routes or configs, or let an attacker abuse message/command ordering to change routing or bypass checks, even though individual functions look “safe”.

`Example – incorrect state handling allows replayed route updates`
```c
enum session_state {
    STATE_DOWN,
    STATE_HANDSHAKE,
    STATE_ESTABLISHED
};

struct peer {
    enum session_state state;
    int allow_updates;
};

void handle_msg(struct peer *p, const char *type, const char *payload)
{
    if (strcmp(type, "HELLO") == 0) {
        p->state = STATE_HANDSHAKE;
        p->allow_updates = 0;
    }
    else if (strcmp(type, "AUTH_OK") == 0) {
        p->state = STATE_ESTABLISHED;
        p->allow_updates = 1;
    }
    else if (strcmp(type, "UPDATE") == 0) {
        /* BUG: no check that we are still ESTABLISHED or that
           this UPDATE is fresh and from the same session */
        if (p->allow_updates) {
            apply_route_update(payload);
        }
    }
}
```

- **What this can lead to**: If an attacker can replay old `UPDATE` messages after the session should be `STATE_DOWN` (for example, after a disconnect) but `allow_updates` was never cleared, they can keep injecting or changing routes using stale messages, causing traffic hijacking or persistent misrouting.

---

#### 5. Input Validation & Data Handling Bugs

- **Definition**: Failing to correctly validate, sanitize, normalize, or constrain external input (packets, CLI, config files) and derived data.
- **Examples**: Integer overflow in length fields, format string bugs in logging, missing bounds checks on packet or CLI parameters.
- **Impact**: Often the entry point for more complex attacks, allowing memory corruption, information leaks, or unauthorized changes to routing state.

`Example – missing length check on a packet field (C)`
```c
struct pkt_header {
    uint16_t len;
    uint8_t  type;
};

void handle_packet(int fd)
{
    struct pkt_header hdr;
    uint8_t buf;

    /* read header first */
    if (read(fd, &hdr, sizeof(hdr)) != sizeof(hdr))
        return;

    /* VULNERABLE: trusts hdr.len without validation */
    if (read(fd, buf, hdr.len) != hdr.len)
        return;

    /* later: parse buf based on hdr.type ... */
    process_payload(hdr.type, buf, hdr.len);
}
```

- **What this can lead to**: If an attacker sends a packet with `len` larger than `buf` (or crafted to trigger integer wraparound), the daemon can read more data than the buffer can safely hold, or treat uninitialized memory as valid payload, leading to memory corruption or logic errors.

<br>

`Example – format string bug in logging (C)`
```c
void log_peer(const char *peer_name)
{
    /* VULNERABLE: untrusted 'peer_name' used as format string */
    syslog(LOG_INFO, peer_name);
}
```

- **What this can lead to**: An attacker who controls `peer_name` can include `%x` or `%n` specifiers, causing the daemon to leak stack contents or write arbitrary values in memory, potentially exposing secrets or enabling exploitation.

---

#### 6. Cryptography & Secrets Handling Bugs

- **Definition**: Misuse of cryptographic primitives or unsafe handling of keys, shared secrets, and credentials (for routing protocol auth, management APIs, VPNs, etc.).
- **Examples**: Hardcoded shared keys in protocol auth, static admin passwords baked into firmware, weak or predictable keys, insecure randomness, outdated/broken algorithms.
- **Impact**: Quietly weakens confidentiality and integrity; an attacker who obtains or guesses these secrets can impersonate routers, decrypt configs, or take over management interfaces.

`Example – hardcoded shared key for routing protocol authentication (C)`
```c
/* VULNERABLE: shared key compiled into binary */
static const char AUTH_KEY[] = "R0uterSharedKey123";

uint16_t make_auth_digest(const uint8_t *data, size_t len)
{
    /* simplified example – real code might use HMAC-MD5/SHA */
    return simple_hash(AUTH_KEY, strlen(AUTH_KEY), data, len);
}

int verify_packet(const uint8_t *data, size_t len, uint16_t recv_digest)
{
    uint16_t calc = make_auth_digest(data, len);
    return (calc == recv_digest);
}
```

- **What this can lead to**: If an attacker can reverse-engineer the daemon or firmware and recover `AUTH_KEY`, they can forge authenticated routing packets or management messages, pretending to be a trusted neighbor or controller, and inject false routes or configuration changes.

---

#### 7. Configuration & Hardening Issues

- **Definition**: Insecure defaults or deployment settings around otherwise acceptable code (debug options, crypto settings, file permissions, management interfaces).
- **Examples**: Debug commands left enabled in production, weak or deprecated crypto suites allowed, management sockets bound to all interfaces, config files readable by non-privileged users.
- **Impact**: Turns otherwise secure code into exploitable systems by exposing sensitive information or making it easy to bypass other defenses.

`Example – debug command exposed in a routing daemon (C)`
```c
void handle_cmd(int fd, const char *cmd)
{
    if (strcmp(cmd, "show_routes") == 0) {
        dump_routes(fd);
    }
    else if (strcmp(cmd, "debug_dump") == 0) {
        /* VULNERABLE: leaks full configuration and secrets to any client */
        dump_full_config(fd);
    }
}
```

- **What this can lead to**: If `debug_dump` is reachable in production (for example, over a management TCP port without strong access control), an attacker can connect and retrieve full routing configuration, authentication keys, and other sensitive details, making further attacks much easier.

---

### How This Connects to Static Analysis

- Static analysis tools look for patterns similar to the snippets above (dangerous APIs, unvalidated input, missing checks, hardcoded secrets).
- Understanding these bug classes makes it easier to judge whether a reported issue is a real vulnerability or a false positive.

---

### Recommended Reading – Static Analysis & SAST

For a clear, beginner-friendly introduction to static analysis and SAST, read this article:

- [What Is Static Code Analysis? A Comprehensive Overview – Parasoft](https://www.parasoft.com/learning-center/static-code-analysis-guide/)

**Assignment question:**  
After reading the article, write a short note answering:

> What static analysis can and cannot do, and why false positives happen.
