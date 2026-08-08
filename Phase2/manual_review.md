# Manual Review and Labelling

This document contains the manual review and classification of findings reported by different static analysis tools during the analysis of the BIRD routing daemon (v2.17.1). Each finding was manually inspected by reviewing the reported source code, the surrounding execution context, and the potential impact on program behavior.

---

## Finding 1

| Field | Value |
|-------|-------|
| Tool | CodeQL |
| Rule | `cpp/unbounded-write` |
| File | `client/birdc.c` |
| Line | 156 |
| Classification | False Positive |

**Reason:** The destination buffer is allocated based on the exact length of the input and the constant suffix, including the null terminator. Therefore, the reported buffer overflow is not possible in this code path.

---

## Finding 2

| Field | Value |
|-------|-------|
| Tool | CodeQL |
| Rule | `cpp/unbounded-write` |
| File | `client/client.c` |
| Line | 108 |
| Classification | False Positive |

**Reason:** The buffer size is calculated from the total length of all command-line arguments before allocation. Therefore, `strcpy()` writes within the allocated memory, and the reported buffer overflow is not possible in this execution path.

---

## Finding 3

| Field | Value |
|-------|-------|
| Tool | CodeQL |
| Rule | `cpp/unbounded-write` |
| File | `obj/conf/cf-lex.c` |
| Line | 12714 |
| Classification | False Positive |

**Reason:** The destination buffer is allocated using `alloca(dlen + alen + 2)`, where the size is calculated from the lengths of both the directory path and the input argument. Therefore, the `sprintf()` operation has enough space for the resulting string, and the reported buffer overflow is not possible in this execution path.

---
## Finding 4

| Field | Value |
|-------|-------|
| Tool | CodeQL |
| Rule | `cpp/unbounded-write` |
| File | `obj/conf/cf-lex.c` |
| Line | 12799 |
| Classification | False Positive |

**Reason:** The input length is validated before allocation, and the destination buffer is dynamically allocated based on the exact string length plus space for the null terminator. Therefore, `strcpy()` cannot overflow the destination in this execution path.

---
## Finding 5

| Field | Value |
|-------|-------|
| Tool | CodeQL |
| Rule | `cpp/unbounded-write` |
| File | `sysdep/unix/main.c` |
| Line | 172 |
| Classification | True Positive |

**Reason:** The `%s` conversion specifier in `sscanf()` does not limit the number of characters copied into the destination buffer. Since `name` points to an offset within a fixed-size buffer, a sufficiently long input string could overflow the remaining buffer space.

---
## Finding 6

| Field | Value |
|-------|-------|
| Tool | SonarQube |
| Rule | `c:S6069` |
| File | `client/commands.c` |
| Line | 104 |
| Classification | False Positive |

**Reason:** The destination buffer size is calculated from the lengths of the input strings before calling `sprintf()`, providing sufficient space for the formatted string and the null terminator. Therefore, no buffer overflow is possible in this execution path.

---
## Finding 7

| Field | Value |
|-------|-------|
| Tool | SonarQube |
| Rule | `c:S6069` |
| File | `client/commands.c` |
| Line | 351 |
| Classification | False Positive |

**Reason:** The destination buffer is dynamically allocated using the exact combined length of both input strings plus space for the null terminator. Therefore, the `sprintf()` call cannot overflow the allocated buffer in this execution path.

---
## Finding 8

| Field | Value |
|-------|-------|
| Tool | SonarQube |
| Rule | `c:S6069` |
| File | `obj/conf/cf-lex.c` |
| Line | 12714 |
| Classification | False Positive |

**Reason:** The destination buffer is allocated using the calculated length of the directory path and include argument. The length parameter `alen` is derived from the actual input string length (`end-start`), ensuring enough space for the formatted path, separator, and null terminator. Therefore, `sprintf()` cannot overflow the destination in this execution path.

---
## Finding 9

| Field | Value |
|-------|-------|
| Tool | SonarQube |
| Rule | `c:S5816` |
| File | `nest/iface.c` |
| Line | 277 |
| Classification | Safe (Security Hotspot) |

**Reason:** The code uses `strncpy()` with a bounded copy (`sizeof(f.name)-1`). The destination structure is zero-initialized (`struct iface f = {};`), so the remaining byte stays null, ensuring the destination string is properly terminated. After manual review, no buffer overflow or unterminated string issue was found.

---
## Finding 10

| Field          | Value                                |
|----------------|--------------------------------------|
| Tool           | SonarQube                            |
| Rule           | `c:S3519`                            |
| File           | `lib/net.h`                          |
| Line           | 505                                 |
| Classification | False Positive                       |

**Reason:** SonarQube reports a potential out-of-bounds memory copy because `memcpy()` copies `sizeof(net_addr_ip6_sadr)` bytes from a pointer originally typed as `net_addr *`. However, the copy is performed only after verifying that `n->type == NET_IP6_SADR`, which guarantees that the underlying object is actually a `net_addr_ip6_sadr`. The pointer is intentionally cast to the derived type, and the copied object has the expected size. Therefore, the reported out-of-bounds memory access cannot occur.

---
## Finding 11

| Field          | Value                           |
|----------------|---------------------------------|
| Tool           | Cppcheck                        |
| Rule           | `external_Cppcheck:syntaxError` |
| File           | `filter/decl.m4`                |
| Line           | 830                             |
| Classification | False Positive                  |

**Reason:** `filter/decl.m4` is an M4 template, not a C source file. Cppcheck analyzes the template directly and cannot interpret M4 macros, resulting in a false syntax error.

---
## Finding 12

| Field          | Value                                  |
|----------------|----------------------------------------|
| Tool           | Cppcheck                               |
| Rule           | `external_Cppcheck:preprocessorErrorDirective` |
| File           | `filter/f-inst.c`                      |
| Line           | 299                                    |
| Classification | False Positive                         |

**Reason:** `filter/f-inst.c` contains generated code and macro-based constructs used by the M4 build process. Cppcheck cannot correctly expand these custom macros and interprets the `runtime()` call incorrectly as a preprocessor issue. Manual review confirms that the generated C code is valid.

---
## Finding 13

| Field | Value |
|---|---|
| Tool | Cppcheck |
| Rule | `preprocessorErrorDirective `|
| File | `filter/trie.c` |
| Line | 368 |
| Classification | False Positive |

**Reason:** The warning is caused by Cppcheck incorrectly analyzing a debug-only macro invocation. `ipa_getbits()` requires three parameters, but the reported call is located inside the `DBG()` macro and is removed when debugging is disabled. The actual compiled code uses the correct three-parameter form of `ipa_getbits()`, and the project builds successfully without this issue.

---
## Finding 14

| Field          | Value                      |
| -------------- | -------------------------- |
| Tool           | Cppcheck                   |
| Rule           | `unknownMacro`               |
| File           | `lib/resource.c  `           |
| Line           | 108                        |
| Classification | False Positive             |

**Reason:** The warning is caused by Cppcheck failing to resolve a project-defined macro during preprocessing analysis. `WALK_LIST` is a valid macro defined in `lib/lists.h`.

---
## Finding 15

| Field | Value |
|---|---|
| Tool | Cppcheck |
| Rule | `negativeIndex `|
| File | `lib/sha512.c`|
| Line | 154 |
| Classification | **False Positive** |

**Reason:** Cppcheck incorrectly interprets `w[(t - 2) % 16]` and similar expressions as negative indexes. However, `t` is an unsigned `uint`, so unsigned arithmetic and modulo operation produce valid indexes in the range `0..15`. The `w[16]` array is intentionally used as a circular buffer.

---
## Finding 16

| Field          | Value |
| -------------- | ----- |
| Tool           | Semgrep |
| Rule           | `c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn` |
| File           | `client/client.c`|
| Line           | 108 |
| Classification | **False Positive** |

**Reason:** The warning is triggered by the use of `strcpy`, but the destination buffer is allocated with sufficient space for all input strings and their null terminators. The pointer is also advanced after each copy, so no buffer overflow occurs.

---
## Finding 17

| Field          | Value |
| -------------- | ----- |
| Tool           | Semgrep |
| Rule           | `c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn `|
| File           | `client/client.c` |
| Line           | 260 |
| Classification | **False Positive** |

**Reason:** The warning is triggered by `strcpy`, but the source length is checked against the destination buffer size before the copy. Therefore, `sa.sun_path` cannot be overflowed.

---
## Finding 18

| Field          | Value          |
| -------------- | -------------- |
| Tool           | Semgrep        |
| Rule           | `insecure-use-string-copy-fn `|
| File           | `client/client.c `|
| Line           | 343            |
| Classification | **False Positive** |

**Reason:** The destination buffer `server_read_buf` has a size of 4096 bytes, while the copied string `"?<too-long>"` requires only 11 bytes including the null terminator. Therefore, `strcpy()` cannot overflow the buffer in this case.

---
## Finding 19

| Field | Value |
|---|---|
| Tool | Semgrep |
| Rule | `c.lang.security.insecure-use-string-copy-fn` |
| File | `client/commands.c `|
| Line | 231 |
| Classification | **False Positive** |

**Reason:**  Semgrep flags the use of `strcpy()`, but the destination buffer is `char buf[256]`. The command tokens are generated from `conf/commands.h`, where the maximum token length is only 21 characters. Therefore, the copied string cannot exceed the 256-byte destination buffer, so no buffer overflow occurs in this context.

---
## Finding 20

| Field | Value |
|---|---|
| Tool | Semgrep |
| Rule | `python.flask.security.xss.audit.direct-use-of-jinja2` |
| File | `misc/gitlab/pipeline.py` |
| Line | 14 |
| Classification | **False Positive** |

**Reason:**  Semgrep flags the direct use of Jinja2, but this file is not a Flask web application. Jinja2 is used to render a `data.yml.j2` template into YAML, not HTML. Therefore, the reported XSS risk and the recommendation to use Flask `render_template()` are not applicable.

