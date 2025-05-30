# Security Exceptions

This document lists security vulnerabilities that have been reviewed and determined to be false positives or acceptable risks for this project.

## py==1.11.0 - PYSEC-2022-42969

**Vulnerability ID**: PYSEC-2022-42969 (CVE-2022-42969, GHSA-w596-4wvx-j9j6)

**Affected Package**: py==1.11.0 (dependency of interrogate)

**Description**: The py library through 1.11.0 for Python allows remote attackers to conduct a ReDoS (Regular Expression Denial of Service) attack via a Subversion repository with crafted info data, because the InfoSvnCommand argument is mishandled.

**Risk Assessment**:

- **Status**: Ignored/False Positive
- **Rationale**:
  1. This vulnerability only affects SVN-related functionality, specifically when processing Subversion repository information
  2. The china-data project does not use SVN or any SVN-related features
  3. The vulnerability has been disputed by multiple third parties as not being reproducible
  4. There is no newer version of the py package available (1.11.0 is the latest)
  5. The py package is in maintenance mode and is only used by interrogate for docstring coverage checking

**Mitigation**:

- The vulnerability is ignored in security scans via:
  - `pip-audit --ignore-vuln PYSEC-2022-42969`
  - safety automatically ignores it based on project policy
- No code changes required as the vulnerable code path is not used

**Review Date**: 2025-05-29

**Reviewed By**: Development Team

**Next Review**: Check quarterly if:

1. A new version of py is released that fixes this issue
2. interrogate removes its dependency on py
3. An alternative to interrogate becomes available that doesn't depend on py
