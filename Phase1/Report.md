
## What Static Analysis Can and Cannot Do, and Why False Positives Happen

Static code analysis is a method of checking source code without running the program. It helps developers find bugs, security problems, coding standard violations, and code quality issues early in software development. Since the code does not need to be executed, static analysis can also be used on incomplete projects and third-party libraries.

One of the biggest advantages of static analysis is finding problems early. It can detect issues such as null pointer dereferences, buffer overflows, memory leaks, insecure functions, coding mistakes, and violations of standards like **MISRA, CERT, CWE,** and **OWASP**. It also checks code complexity, duplicate code, and coding style, helping developers write cleaner and more reliable software.

Modern static analysis tools do more than simple pattern matching. They analyze the program's structure, data flow, and control flow to understand how the code works and to find more complex bugs and security vulnerabilities. They also use heuristics to focus on the most likely execution paths instead of checking every possible path.

## Limitations of Static Analysis

Static analysis also has some limitations. Because the program is not executed, the tool cannot know the actual values of user input or observe the program's behavior at runtime. Some bugs only appear while the application is running, so static analysis may not detect them. It can also have difficulty analyzing very complex or highly dynamic applications.

## False Positives

A false positive happens when the tool reports a problem that is not actually a real bug. This occurs because the analyzer makes safe assumptions without executing the code. To avoid missing important issues, it may report code that only appears suspicious.

For example, a tool may warn about a possible null pointer dereference or SQL injection even when the code is already safe.

## False Negatives

Static analysis can also produce **false negatives**, which means a real bug is not reported. This happens because no static analysis tool can perfectly understand every possible execution path or runtime behavior.

## Conclusion

Static analysis is a powerful technique for improving software quality and security, but it cannot replace other testing methods. The best approach is to combine static analysis with dynamic testing, unit testing, and code reviews to build more secure, reliable, and maintainable software.